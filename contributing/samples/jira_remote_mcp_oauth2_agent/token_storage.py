"""OAuth2トークン用のセキュアなトークンストレージ。"""

import json
import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging


class TokenStorage:
    """基本的なセキュリティ機能を備えた簡単なファイルベースのトークンストレージ。
    
    注意: 本番環境では、keyringまたは暗号化されたストレージの使用を検討してください。
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """トークンストレージを初期化します。
        
        Args:
            storage_path: トークンを保存するパス（デフォルトは ~/.jira_mcp_tokens）
        """
        if storage_path is None:
            storage_path = Path.home() / ".jira_mcp_tokens"
        
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 制限的な権限を設定（所有者のみ）
        os.chmod(self.storage_path, 0o700)
        
        self.logger = logging.getLogger(__name__)
    
    def _get_token_file(self, domain: str) -> Path:
        """特定のドメインのトークンファイルパスを取得します。
        
        Args:
            domain: Jiraドメイン（例: 'company.atlassian.net'）
            
        Returns:
            トークンファイルへのパス
        """
        # ファイル名のためにドットをアンダースコアに置換
        safe_domain = domain.replace(".", "_")
        token_file = self.storage_path / f"{safe_domain}.json"
        return token_file
    
    def save_tokens(
        self,
        domain: str,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        cloud_id: Optional[str] = None
    ) -> None:
        """OAuth2トークンを安全に保存します。
        
        Args:
            domain: Jiraドメイン
            access_token: OAuth2アクセストークン
            refresh_token: OAuth2リフレッシュトークン
            expires_in: トークンの有効期間（秒）
            cloud_id: サイトのAtlassianクラウドID
        """
        token_file = self._get_token_file(domain)
        
        # 有効期限を計算
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at.isoformat(),
            "cloud_id": cloud_id,
            "domain": domain,
            "saved_at": datetime.utcnow().isoformat()
        }
        
        # 制限的な権限で書き込み
        with open(token_file, "w") as f:
            json.dump(token_data, f, indent=2)
        
        # ファイル権限が制限的であることを確認
        os.chmod(token_file, 0o600)
        
        self.logger.info(f"Tokens saved for domain: {domain}")
    
    def load_tokens(self, domain: str) -> Optional[Dict]:
        """ドメインのOAuth2トークンを読み込みます。
        
        Args:
            domain: Jiraドメイン
            
        Returns:
            見つかって有効な場合はトークンデータ、そうでなければNone
        """
        token_file = self._get_token_file(domain)
        
        if not token_file.exists():
            self.logger.debug(f"No tokens found for domain: {domain}")
            return None
        
        try:
            with open(token_file, "r") as f:
                token_data = json.load(f)
            
            # アクセストークンがまだ有効かチェック
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.utcnow() >= expires_at:
                self.logger.info(f"Access token expired for domain: {domain}")
                # とにかくデータを返す、呼び出し元がリフレッシュ可能
                token_data["expired"] = True
            else:
                token_data["expired"] = False
            
            return token_data
            
        except Exception as e:
            self.logger.error(f"Failed to load tokens for {domain}: {e}")
            return None
    
    def delete_tokens(self, domain: str) -> None:
        """ドメインの保存されたトークンを削除します。
        
        Args:
            domain: Jiraドメイン
        """
        token_file = self._get_token_file(domain)
        
        if token_file.exists():
            token_file.unlink()
            self.logger.info(f"Tokens deleted for domain: {domain}")
    
    def update_access_token(
        self,
        domain: str,
        access_token: str,
        expires_in: int
    ) -> None:
        """アクセストークンのみを更新します（リフレッシュ後）。
        
        Args:
            domain: Jiraドメイン
            access_token: 新しいアクセストークン
            expires_in: トークンの有効期間（秒）
        """
        token_data = self.load_tokens(domain)
        if not token_data:
            raise ValueError(f"No existing tokens found for domain: {domain}")
        
        # アクセストークンと有効期限を更新
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token_data["access_token"] = access_token
        token_data["expires_at"] = expires_at.isoformat()
        token_data["refreshed_at"] = datetime.utcnow().isoformat()
        
        # 更新されたデータを保存
        self.save_tokens(
            domain=domain,
            access_token=access_token,
            refresh_token=token_data["refresh_token"],
            expires_in=expires_in,
            cloud_id=token_data.get("cloud_id")
        )