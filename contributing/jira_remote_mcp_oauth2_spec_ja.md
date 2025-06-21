# Jira リモート MCP サーバーエージェント仕様書（OAuth2認証）

## 概要

この仕様書は、OAuth2認証を使用してAtlassianのリモートJira MCPサーバーに接続するADKエージェントを定義します。このアプローチは、自動リフレッシュ機能付きのより安全なトークンベース認証を提供し、本番環境およびマルチユーザーシナリオに適しています。

## アーキテクチャ

### 接続方法
- **プロトコル**: OAuth2付きServer-Sent Events (SSE)
- **エンドポイント**: `https://mcp.atlassian.com/v1/sse`
- **接続タイプ**: ADKのOAuth2認証フレームワークを使用した`SseConnectionParams`

### 認証フロー
- **方式**: OAuth 2.0 認可コードフロー
- **プロバイダー**: Atlassian OAuth2
- **トークン管理**: ADKの`OAuth2CredentialRefresher`による自動リフレッシュ

## OAuth2設定

### Atlassian OAuth2エンドポイント
```python
ATLASSIAN_AUTH_ENDPOINTS = {
    "authorization_endpoint": "https://auth.atlassian.com/authorize",
    "token_endpoint": "https://auth.atlassian.com/oauth/token",
    "userinfo_endpoint": "https://api.atlassian.com/me",
    "revocation_endpoint": "https://auth.atlassian.com/oauth/revoke"
}
```

### 必要なOAuth2スコープ
```python
JIRA_OAUTH_SCOPES = [
    "read:jira-work",           # Jiraプロジェクトと課題データの読み取り
    "write:jira-work",          # 課題の作成と更新
    "read:jira-user",           # ユーザー情報へのアクセス
    "read:me",                  # ユーザープロファイルの読み取り
    "offline_access"            # リフレッシュトークンサポート
]
```

## 実装詳細

### ディレクトリ構造
```
contributing/samples/jira_remote_mcp_oauth2_agent/
├── __init__.py
├── agent.py
├── auth_config.py
├── oauth_callback_server.py
├── .env.example
├── README.md
└── requirements.txt
```

### 環境設定

`.env.example`:
```env
# OAuth2クライアント設定（Atlassianアプリから）
ATLASSIAN_CLIENT_ID=your_client_id_here
ATLASSIAN_CLIENT_SECRET=your_client_secret_here
ATLASSIAN_REDIRECT_URI=http://localhost:8080/callback

# Jiraインスタンス
JIRA_URL=https://yourcompany.atlassian.net

# トークンストレージ（オプション、デフォルトはメモリ内）
TOKEN_STORAGE_PATH=~/.adk/jira_tokens.json
```

### OAuth2認証設定

`auth_config.py`:
```python
from google.adk.auth import AuthCredential, AuthScheme
from google.adk.auth.auth_schemes import AuthSchemeType, OAuthGrantType
from google.adk.auth.oauth2_credential_util import OAuth2CredentialUtil
from google.adk.auth.refresher.oauth2_credential_refresher import OAuth2CredentialRefresher
from fastapi.openapi.models import OAuthFlow, OAuthFlows, SecurityScheme
import os
from typing import Optional

class JiraOAuth2Config:
    """Jira OAuth2認証の設定。"""
    
    def __init__(self):
        self.client_id = os.getenv("ATLASSIAN_CLIENT_ID")
        self.client_secret = os.getenv("ATLASSIAN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ATLASSIAN_REDIRECT_URI", "http://localhost:8080/callback")
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("OAuth2クライアント認証情報が設定されていません")
    
    def create_auth_scheme(self) -> AuthScheme:
        """Atlassian用のOAuth2認証スキームを作成。"""
        return SecurityScheme(
            type=AuthSchemeType.oauth2,
            flows=OAuthFlows(
                authorizationCode=OAuthFlow(
                    authorizationUrl="https://auth.atlassian.com/authorize",
                    tokenUrl="https://auth.atlassian.com/oauth/token",
                    scopes={
                        "read:jira-work": "Jiraデータの読み取り",
                        "write:jira-work": "Jiraデータの書き込み",
                        "read:jira-user": "ユーザー情報の読み取り",
                        "read:me": "プロファイルの読み取り",
                        "offline_access": "リフレッシュトークン"
                    }
                )
            )
        )
    
    async def get_or_refresh_credential(
        self, 
        stored_token_path: Optional[str] = None
    ) -> AuthCredential:
        """OAuth2認証情報を取得、必要に応じてリフレッシュ。"""
        # 保存されたトークンを確認
        if stored_token_path and os.path.exists(stored_token_path):
            with open(stored_token_path, 'r') as f:
                import json
                token_data = json.load(f)
                
            # 保存されたトークンから認証情報を作成
            credential = AuthCredential(
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                expires_at=token_data.get("expires_at")
            )
            
            # リフレッシュが必要かチェック
            if OAuth2CredentialUtil.is_expired(credential):
                refresher = OAuth2CredentialRefresher(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    token_endpoint="https://auth.atlassian.com/oauth/token"
                )
                credential = await refresher.refresh(credential)
                
                # リフレッシュされたトークンを保存
                self._save_token(credential, stored_token_path)
            
            return credential
        else:
            # 新しいOAuth2フローを開始
            return await self._initiate_oauth_flow()
    
    async def _initiate_oauth_flow(self) -> AuthCredential:
        """OAuth2認可フローを開始。"""
        from .oauth_callback_server import start_callback_server
        
        # ローカルコールバックサーバーを開始
        auth_code = await start_callback_server(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            auth_url="https://auth.atlassian.com/authorize",
            scopes=["read:jira-work", "write:jira-work", "read:jira-user", "read:me", "offline_access"]
        )
        
        # コードをトークンに交換
        util = OAuth2CredentialUtil(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_endpoint="https://auth.atlassian.com/oauth/token"
        )
        
        credential = await util.exchange_code_for_token(
            code=auth_code,
            redirect_uri=self.redirect_uri
        )
        
        # トークンを保存
        token_path = os.getenv("TOKEN_STORAGE_PATH", "~/.adk/jira_tokens.json")
        self._save_token(credential, os.path.expanduser(token_path))
        
        return credential
    
    def _save_token(self, credential: AuthCredential, path: str):
        """トークンをファイルに保存。"""
        import json
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump({
                "access_token": credential.access_token,
                "refresh_token": credential.refresh_token,
                "expires_at": credential.expires_at
            }, f)
```

### エージェント実装

`agent.py`:
```python
import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from .auth_config import JiraOAuth2Config

# 環境変数の読み込み
load_dotenv()

# 設定の検証
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
if not JIRA_URL:
    raise ValueError("JIRA_URL環境変数が必要です")

async def create_jira_agent():
    """OAuth2認証でJiraエージェントを作成。"""
    # OAuth2設定を初期化
    oauth_config = JiraOAuth2Config()
    
    # OAuth2認証情報を取得またはリフレッシュ
    token_path = os.path.expanduser(
        os.getenv("TOKEN_STORAGE_PATH", "~/.adk/jira_tokens.json")
    )
    credential = await oauth_config.get_or_refresh_credential(token_path)
    
    # OAuth2トークンでMCP接続を設定
    jira_remote_tools = MCPToolset(
        connection_params=SseConnectionParams(
            url="https://mcp.atlassian.com/v1/sse",
            headers={
                "Authorization": f"Bearer {credential.access_token}",
                "X-Atlassian-Instance-URL": JIRA_URL,
                "Accept": "text/event-stream",
                "Content-Type": "application/json"
            },
            timeout=10.0,
            sse_read_timeout=300.0
        ),
        auth_scheme=oauth_config.create_auth_scheme(),
        auth_credential=credential
    )
    
    # エージェントを作成
    return Agent(
        name="jira_remote_oauth2_agent",
        model="gemini-2.0-flash",
        instruction="""あなたはOAuth2認証を使用するJiraプロジェクト管理アシスタントです。

OAuth2認証により組織のJiraインスタンスへの安全なアクセスが可能です。
これにより、セキュリティの向上と自動トークン管理が提供されます。

利用可能な機能:
1. 完全なJira課題管理（作成、読み取り、更新、トランジション）
2. プロジェクトとコンポーネントの管理
3. ユーザーとチームの操作
4. 高度なJQLクエリ
5. カスタムフィールド操作
6. 添付ファイルの処理

常にセキュリティのベストプラクティスを維持し、明確で有用な応答を提供してください。
認証は自動的に管理されるため、ユーザーのJiraタスクの支援に集中してください。
""",
        tools=[jira_remote_tools],
    )

# 非同期コンテキスト用
root_agent = None

def get_agent():
    """Jiraエージェントを取得または作成。"""
    global root_agent
    if root_agent is None:
        loop = asyncio.get_event_loop()
        root_agent = loop.run_until_complete(create_jira_agent())
    return root_agent
```

### OAuth2コールバックサーバー

`oauth_callback_server.py`:
```python
import asyncio
import urllib.parse
from aiohttp import web
import webbrowser
from typing import Optional

async def start_callback_server(
    client_id: str,
    redirect_uri: str,
    auth_url: str,
    scopes: list[str],
    port: int = 8080
) -> str:
    """OAuth2コールバックを処理するローカルサーバーを開始。"""
    
    auth_code: Optional[str] = None
    app = web.Application()
    
    async def handle_callback(request):
        nonlocal auth_code
        auth_code = request.query.get('code')
        
        if auth_code:
            return web.Response(
                text="認証が成功しました！このウィンドウを閉じてください。",
                content_type='text/html; charset=utf-8'
            )
        else:
            error = request.query.get('error', '不明なエラー')
            return web.Response(
                text=f"認証に失敗しました: {error}",
                content_type='text/html; charset=utf-8',
                status=400
            )
    
    app.router.add_get('/callback', handle_callback)
    
    # 認証URLを構築
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'audience': 'api.atlassian.com',
        'prompt': 'consent'
    }
    
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    # 認証用にブラウザを開く
    print(f"認証用にブラウザを開いています: {full_auth_url}")
    webbrowser.open(full_auth_url)
    
    # サーバーを開始
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    
    # コールバックを待機
    while auth_code is None:
        await asyncio.sleep(0.1)
    
    # クリーンアップ
    await runner.cleanup()
    
    return auth_code
```

## 高度な機能

### トークンリフレッシュ処理

エージェントは自動的にトークンリフレッシュを処理します：

```python
class AutoRefreshMCPToolset(MCPToolset):
    """自動OAuth2トークンリフレッシュ機能付きMCPToolset。"""
    
    def __init__(self, oauth_config: JiraOAuth2Config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oauth_config = oauth_config
        self._refresher = OAuth2CredentialRefresher(
            client_id=oauth_config.client_id,
            client_secret=oauth_config.client_secret,
            token_endpoint="https://auth.atlassian.com/oauth/token"
        )
    
    async def get_tools(self, readonly_context=None):
        """401エラー時のトークンリフレッシュ処理をオーバーライド。"""
        try:
            return await super().get_tools(readonly_context)
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                # トークンをリフレッシュして再試行
                new_credential = await self._refresher.refresh(self._auth_credential)
                self._auth_credential = new_credential
                
                # 接続ヘッダーを更新
                self._connection_params.headers["Authorization"] = f"Bearer {new_credential.access_token}"
                
                # 再試行
                return await super().get_tools(readonly_context)
            raise
```

### マルチテナントサポート

複数のJiraインスタンスをサポートする場合：

```python
class MultiTenantJiraAgent:
    """異なるOAuth2アプリで複数のJiraインスタンスをサポート。"""
    
    def __init__(self):
        self.instances = {}
    
    def add_instance(self, name: str, config: dict):
        """Jiraインスタンス設定を追加。"""
        self.instances[name] = {
            'url': config['jira_url'],
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'agent': None
        }
    
    async def get_agent(self, instance_name: str) -> Agent:
        """特定のインスタンス用のエージェントを取得。"""
        if instance_name not in self.instances:
            raise ValueError(f"不明なインスタンス: {instance_name}")
        
        if self.instances[instance_name]['agent'] is None:
            # このインスタンス用のエージェントを作成
            config = JiraOAuth2Config()
            config.client_id = self.instances[instance_name]['client_id']
            config.client_secret = self.instances[instance_name]['client_secret']
            
            # エージェントを作成...
            self.instances[instance_name]['agent'] = await create_jira_agent_for_instance(config)
        
        return self.instances[instance_name]['agent']
```

## セキュリティのベストプラクティス

### トークンストレージ
```python
import keyring
from cryptography.fernet import Fernet

class SecureTokenStorage:
    """システムキーチェーンを使用した安全なトークンストレージ。"""
    
    def __init__(self, service_name="adk_jira_oauth"):
        self.service_name = service_name
        self.encryption_key = self._get_or_create_key()
    
    def _get_or_create_key(self) -> bytes:
        """暗号化キーを取得または作成。"""
        key = keyring.get_password(self.service_name, "encryption_key")
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password(self.service_name, "encryption_key", key)
        return key.encode()
    
    def save_token(self, user_id: str, token_data: dict):
        """暗号化されたトークンを保存。"""
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(json.dumps(token_data).encode())
        keyring.set_password(self.service_name, user_id, encrypted.decode())
    
    def get_token(self, user_id: str) -> Optional[dict]:
        """トークンを取得して復号化。"""
        encrypted = keyring.get_password(self.service_name, user_id)
        if encrypted:
            f = Fernet(self.encryption_key)
            decrypted = f.decrypt(encrypted.encode())
            return json.loads(decrypted.decode())
        return None
```

### スコープ管理
- 必要なスコープのみをリクエスト
- 必要に応じてスコープエスカレーションを実装
- 監査用にスコープ使用状況をログ

### セッションセキュリティ
```python
# セッションタイムアウトを実装
SESSION_TIMEOUT = 3600  # 1時間

# セッション検証を追加
async def validate_session(credential: AuthCredential) -> bool:
    """OAuth2セッションがまだアクティブかを検証。"""
    try:
        # userinfoエンドポイントを呼び出してトークンを検証
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.atlassian.com/me",
                headers={"Authorization": f"Bearer {credential.access_token}"}
            ) as response:
                return response.status == 200
    except:
        return False
```

## テストガイドライン

### ユニットテスト
```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_oauth_flow():
    """OAuth2認証フローのテスト。"""
    config = JiraOAuth2Config()
    
    with patch('webbrowser.open') as mock_browser:
        with patch('aiohttp.web.TCPSite.start') as mock_server:
            # 認証コードコールバックをシミュレート
            mock_code = "test_auth_code"
            
            # フロー開始をテスト
            credential = await config._initiate_oauth_flow()
            
            assert mock_browser.called
            assert credential.access_token is not None

@pytest.mark.asyncio  
async def test_token_refresh():
    """自動トークンリフレッシュのテスト。"""
    config = JiraOAuth2Config()
    
    # 有効期限切れの認証情報を作成
    expired_credential = AuthCredential(
        access_token="expired_token",
        refresh_token="refresh_token",
        expires_at=0  # すでに期限切れ
    )
    
    # リフレッシュをテスト
    refreshed = await config.get_or_refresh_credential()
    assert refreshed.access_token != "expired_token"
```

### 統合テスト
```python
@pytest.mark.integration
async def test_jira_operations_with_oauth():
    """OAuth2でのJira操作のテスト。"""
    agent = await create_jira_agent()
    
    # 課題検索をテスト
    result = await agent.execute(
        "プロジェクトTESTのすべてのオープン課題を検索"
    )
    
    assert result.success
    assert "issues" in result.data
```

## デプロイメント

### 本番環境設定
```python
# 本番環境設定
PRODUCTION_CONFIG = {
    "token_storage": "aws_secrets_manager",  # または "azure_keyvault"
    "session_timeout": 3600,
    "max_refresh_attempts": 3,
    "ssl_verify": True,
    "log_level": "INFO"
}
```

### Dockerデプロイメント
```dockerfile
FROM python:3.11-slim

# 依存関係をインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# エージェントコードをコピー
COPY . /app
WORKDIR /app

# 安全なトークンストレージを使用
ENV TOKEN_STORAGE_PATH=/secure/tokens
ENV PYTHONPATH=/app

# 制限された権限で実行
USER nobody
CMD ["python", "-m", "agent"]
```

## モニタリングと可観測性

### OAuth2メトリクス
```python
from prometheus_client import Counter, Histogram

oauth_token_refreshes = Counter(
    'jira_oauth_token_refreshes_total',
    'OAuth2トークンリフレッシュの総数'
)

oauth_auth_duration = Histogram(
    'jira_oauth_auth_duration_seconds',
    'OAuth2認証フローの所要時間'
)

class MonitoredOAuth2Config(JiraOAuth2Config):
    """モニタリング機能付きOAuth2設定。"""
    
    async def get_or_refresh_credential(self, *args, **kwargs):
        with oauth_auth_duration.time():
            credential = await super().get_or_refresh_credential(*args, **kwargs)
        
        if hasattr(self, '_did_refresh') and self._did_refresh:
            oauth_token_refreshes.inc()
        
        return credential
```

## トラブルシューティング

### よくある問題

1. **無効なクライアントエラー**
   - クライアントIDとシークレットを確認
   - AtlassianでのOAuth2アプリ設定を確認

2. **スコープエラー**
   - リクエストしたスコープがOAuth2アプリで承認されているかを確認
   - Atlassian API権限を確認

3. **トークン有効期限**
   - 適切なリフレッシュロジックを実装
   - トークンの有効期限を監視

4. **ネットワーク問題**
   - 指数バックオフ付きのリトライロジックを実装
   - パフォーマンス向上のためのコネクションプーリングを追加

## 参考資料

- [Atlassian OAuth 2.0ドキュメント](https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [ADK認証ガイド](https://github.com/google/adk-python/blob/main/docs/auth.md)
- [MCP認証仕様](https://modelcontextprotocol.io/specification/basic/authorization)