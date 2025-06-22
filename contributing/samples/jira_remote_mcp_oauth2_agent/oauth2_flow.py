"""Atlassian向けOAuth2認証フロー実装。"""

import asyncio
import base64
import hashlib
import json
import secrets
import webbrowser
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import aiohttp

from auth_config import AtlassianOAuth2Config


class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    """OAuth2コールバック用HTTPハンドラー。"""
    
    def do_GET(self):
        """OAuth2コールバック用GETリクエストを処理。"""
        query_components = parse_qs(urlparse(self.path).query)
        
        if "code" in query_components:
            self.server.auth_code = query_components["code"][0]
            self.server.state = query_components.get("state", [None])[0]
            
            # 成功レスポンスを送信
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                <h1>Authentication Successful!</h1>
                <p>You can close this window and return to the application.</p>
                </body>
                </html>
            """)
        else:
            # エラーを処理
            error = query_components.get("error", ["Unknown error"])[0]
            self.server.auth_error = error
            
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body>
                <h1>Authentication Failed</h1>
                <p>Error: {error}</p>
                </body>
                </html>
            """.encode())
    
    def log_message(self, format, *args):
        """ログメッセージを非表示にする。"""
        pass


class OAuth2Flow:
    """Atlassian向けOAuth2認証フローを処理。"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        port: int = 8080
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.port = port
        self.config = AtlassianOAuth2Config()
        
        # PKCEパラメータ
        self.code_verifier = None
        self.code_challenge = None
        self.state = None
    
    def _generate_pkce_parameters(self) -> Tuple[str, str]:
        """PKCEコード検証子とチャレンジを生成。
        
        Returns:
            (code_verifier, code_challenge)のタプル
        """
        # コード検証子を生成（43-128文字）
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode("utf-8").rstrip("=")
        
        # コードチャレンジを生成（検証子のSHA256）
        challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
        
        return code_verifier, code_challenge
    
    def _generate_state(self) -> str:
        """CSRF保護用のランダムなstateを生成。"""
        return secrets.token_urlsafe(32)
    
    async def start_auth_flow(self) -> Optional[str]:
        """OAuth2認証フローを開始。
        
        Returns:
            成功時は認証コード、失敗時はNone
        """
        # PKCEとstateを生成
        self.code_verifier, self.code_challenge = self._generate_pkce_parameters()
        self.state = self._generate_state()
        
        # 認証URLを構築
        auth_url = self.config.get_authorize_url(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            state=self.state,
            code_challenge=self.code_challenge
        )
        
        # コールバックサーバーを開始
        server = HTTPServer(("localhost", self.port), OAuth2CallbackHandler)
        server.auth_code = None
        server.auth_error = None
        server.state = None
        
        # サーバーをスレッドで実行
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        # ブラウザを開く
        print(f"認証のためブラウザを開いています...")
        print(f"ブラウザが開かない場合は、こちらにアクセスしてください: {auth_url}")
        webbrowser.open(auth_url)
        
        # コールバックを待機
        server_thread.join(timeout=300)  # 5分のタイムアウト
        
        if server.auth_code and server.state == self.state:
            return server.auth_code
        else:
            error = getattr(server, "auth_error", "タイムアウトまたはキャンセル")
            raise Exception(f"認証に失敗しました: {error}")
    
    async def exchange_code_for_token(self, auth_code: str) -> Dict:
        """認証コードをアクセストークンに交換。
        
        Args:
            auth_code: コールバックからの認証コード
            
        Returns:
            access_tokenとrefresh_tokenを含むトークンレスポンス
        """
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
                "code_verifier": self.code_verifier
            }
            
            async with session.post(
                self.config.token_url,
                data=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"トークン交換に失敗しました ({response.status}): {error_text}"
                    )
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """リフレッシュトークンを使用してアクセストークンを更新。
        
        Args:
            refresh_token: 有効なリフレッシュトークン
            
        Returns:
            新しいトークンレスポンス
        """
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token
            }
            
            async with session.post(
                self.config.token_url,
                data=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"トークンの更新に失敗しました ({response.status}): {error_text}"
                    )
    
    async def get_accessible_resources(self, access_token: str) -> list:
        """アクセス可能なAtlassianリソースのリストを取得。
        
        Args:
            access_token: 有効なアクセストークン
            
        Returns:
            アクセス可能なリソース（Jiraサイト）のリスト
        """
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with session.get(
                self.config.accessible_resources_url,
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"リソースの取得に失敗しました ({response.status}): {error_text}"
                    )