# integration_connector_euc_agent - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`integration_connector_euc_agent` エージェントは、Google Cloud Integration Connectors でエンドユーザー認証（End User Credentials）を使用した外部API統合の実装方法を示すサンプルです。OAuth2 認証フローとApplication Integration Toolsetの組み合わせにより、セキュアなユーザー認証ベースの統合を学習できます。

### 主要機能
- **エンドユーザー OAuth2 認証**: ユーザー固有の認証フロー
- **Google Calendar 統合**: OAuth2を使用したCalendar API アクセス
- **Application Integration 活用**: 認証付き外部システム統合
- **セキュアな認証管理**: 認証スキームとクレデンシャルの適切な管理

### 対象ユースケース
- ユーザー個別認証が必要な外部サービス統合
- SaaS アプリケーションとの OAuth2 統合
- エンドユーザー権限での API アクセス
- セキュアな統合パターンの学習

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (Calendar操作要求)
[integration_connector_euc_agent] 
    ↓ (OAuth2 認証フロー)
┌─────────────────────────────────────────────────────────┐
│ End User Credentials (EUC) OAuth2 Flow                 │
│ 1. OAuth2 スキーム定義                                  │
│ 2. 認証クレデンシャル作成                                │
│ 3. Authorization Code Flow                             │
│ 4. アクセストークン取得                                  │
│ 5. Application Integration での利用                      │
└─────────────────────────────────────────────────────────┘
    ↓ (認証済み統合リクエスト)
[Google Cloud Application Integration]
    ↓ (Integration Connector with EUC)
[Google Calendar API]
    ├── Calendars.list - カレンダー一覧
    └── Events.list - イベント取得
    ↓ (ユーザーのCalendarデータ)
[ADK エージェント応答]
```

### OAuth2 + Application Integration パターン
```
[OAuth2 Authentication Layer]
    ├── Authorization Code Flow
    ├── Client Credentials Management
    ├── Scope Definition
    └── Token Lifecycle Management
    ↓
[Application Integration Layer]
    ├── OAuth2-enabled Connector
    ├── EUC Token Integration
    ├── API Action Mapping
    └── Response Processing
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス + OAuth2統合)
- **OAuth2認証**: `OAuth2Auth` + `AuthCredential`
- **統合ツールセット**: `ApplicationIntegrationToolset` (OAuth2対応)
- **認証スキーム**: FastAPI OAuth2 スキーム定義
- **接続管理**: Integration Connector with EUC

### 依存関係
```python
# OAuth2 認証
from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows

# Application Integration
from google.adk.tools.application_integration_tool import ApplicationIntegrationToolset

# ADK コンポーネント
from google.adk import Agent

# 環境設定
import os
from dotenv import load_dotenv
```

## 3. コード詳細解説

### 3.1 OAuth2 スキーム定義

```python
# OAuth2 認証スキームの設定
oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            scopes={
                "https://www.googleapis.com/auth/calendar.readonly": (
                    "Read access to Google Calendar"
                )
            },
        )
    )
)
```

**OAuth2 設定の詳細**:

#### 認証エンドポイント
- **authorizationUrl**: Google OAuth2 認証開始URL
- **tokenUrl**: アクセストークン取得URL
- **標準準拠**: OAuth2.0 Authorization Code Flow

#### スコープ定義
```python
scopes = {
    "https://www.googleapis.com/auth/calendar.readonly": "Read access to Google Calendar"
}
```

**スコープ管理の重要性**:
- **最小権限**: 必要最小限のアクセス権限
- **ユーザー透明性**: ユーザーが許可する内容の明確化
- **セキュリティ**: 過度な権限要求の回避

### 3.2 認証クレデンシャル設定

```python
# 環境変数から OAuth2 認証情報を取得
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# 認証クレデンシャルの作成
auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=client_id,
        client_secret=client_secret
    )
)
```

**認証クレデンシャルの特徴**:
- **環境変数管理**: セキュアな認証情報管理
- **OAuth2Auth**: ADK OAuth2 統合クラス
- **型安全**: AuthCredentialTypes による型管理

### 3.3 Application Integration Toolset with OAuth2

```python
calendar_tool = ApplicationIntegrationToolset(
    project=connection_project,
    location=connection_location,
    connection=connection_name,
    actions=["GET_calendars/%7BcalendarId%7D/events"],
    auth_scheme=oauth2_scheme,
    auth_credential=auth_credential
)
```

**統合設定の詳細**:

#### アクション定義
```python
actions=["GET_calendars/%7BcalendarId%7D/events"]
```

**URL エンコーディング**:
- `%7B` = `{` (左波括弧)
- `%7D` = `}` (右波括弧)
- パスパラメータ: `{calendarId}` の安全なエンコーディング

#### 認証統合
- **auth_scheme**: OAuth2 フロー定義
- **auth_credential**: 認証クレデンシャル
- **統合**: Application Integration での自動認証処理

### 3.4 エージェント設定

```python
root_agent = Agent(
    model="gemini-2.0-flash",
    name="integration_connector_euc_agent",
    instruction="""
    You are an integration agent that demonstrates End User Credentials (EUC) 
    authentication with Google Cloud Integration Connectors.
    
    You can help users access their Google Calendar data using their own 
    OAuth2 credentials through Application Integration.
    
    Key capabilities:
    1. Authenticate users with OAuth2 flow
    2. Access user's Google Calendar events
    3. Demonstrate secure EUC integration patterns
    4. Handle OAuth2 token lifecycle
    
    Always ensure user privacy and follow OAuth2 best practices.
    """,
    tools=[calendar_tool],
)
```

**エージェント設計の特徴**:
- **EUC専門**: エンドユーザー認証の専門エージェント
- **プライバシー重視**: ユーザーデータ保護の明示
- **OAuth2準拠**: 標準OAuth2フローの遵守

## 4. 設定・環境構築

### 4.1 Google Cloud Console 設定

#### OAuth2 クライアント作成
1. **Google Cloud Console** → **API とサービス** → **認証情報**
2. **認証情報を作成** → **OAuth 2.0 クライアント ID**
3. **アプリケーションの種類**: ウェブアプリケーション
4. **承認済みのリダイレクト URI**:
   ```
   http://localhost/dev-ui/
   ```

#### Calendar API 有効化
```bash
# Google Calendar API の有効化
gcloud services enable calendar-json.googleapis.com

# Integration Connectors API の有効化
gcloud services enable connectors.googleapis.com
gcloud services enable integrations.googleapis.com
```

### 4.2 Integration Connector (EUC) 設定

#### EUC対応 Calendar Connector の作成
```bash
# Calendar Integration Connector (EUC対応) の作成
gcloud integration connections create calendar-euc-connector \
    --location=us-central1 \
    --connector-version=projects/connectors/locations/global/providers/googleapis/connectors/googleapis/versions/1 \
    --config-variable=base_url=https://www.googleapis.com \
    --config-variable=auth_type=oauth2 \
    --enable-euc \
    --oauth-client-credentials-secret=projects/PROJECT_ID/secrets/oauth-client-credentials/versions/latest
```

#### OAuth2 Client Credentials Secret 作成
```bash
# OAuth2 認証情報をSecret Managerに保存
echo '{"client_id":"your-client-id","client_secret":"your-client-secret"}' | \
gcloud secrets create oauth-client-credentials \
    --data-file=-

# Connector が Secret にアクセスできるよう権限付与
gcloud secrets add-iam-policy-binding oauth-client-credentials \
    --member="serviceAccount:connector-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 4.3 環境変数設定

#### .env ファイル設定
```bash
# OAuth2 Client Credentials
CLIENT_ID=your-oauth-client-id
CLIENT_SECRET=your-oauth-client-secret

# Google Cloud Project Configuration
CONNECTION_PROJECT=your-gcp-project-id
CONNECTION_LOCATION=us-central1
CONNECTION_NAME=projects/your-project/locations/us-central1/connections/calendar-euc-connector

# Optional: Additional Configuration
OAUTH_SCOPES=https://www.googleapis.com/auth/calendar.readonly
REDIRECT_URI=http://localhost/dev-ui/
```

### 4.4 権限設定

#### 必要な IAM 権限
```bash
# Service Account での EUC 権限
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:your-service-account@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/integrations.integrationInvoker"

# EUC Token 管理権限
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:your-service-account@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/connectors.eucTokenManager"

# Secret Manager アクセス権限
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:your-service-account@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### Calendar イベント取得
```
ユーザー: "Show me my calendar events for today"
エージェント: [OAuth2認証フロー開始]
"I need access to your Google Calendar. Please authorize me..."

[ユーザーがOAuth2認証を完了]

エージェント: [Calendar API経由でイベント取得]
"Here are your calendar events for today:

1. Team Meeting (9:00 AM - 10:00 AM)
   Location: Conference Room A
   
2. Client Call (2:00 PM - 3:00 PM)  
   Location: Zoom Meeting
   
3. Code Review (4:00 PM - 5:00 PM)
   Location: Online"
```

### 5.2 高度な OAuth2 パターン

#### マルチスコープ認証
```python
# 複数スコープでの OAuth2 設定
extended_oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            scopes={
                "https://www.googleapis.com/auth/calendar.readonly": "Read calendar events",
                "https://www.googleapis.com/auth/calendar.events": "Manage calendar events",
                "https://www.googleapis.com/auth/gmail.readonly": "Read Gmail messages"
            },
        )
    )
)

# 複数サービス統合エージェント
multi_service_agent = Agent(
    name="multi_oauth_agent",
    tools=[
        create_calendar_toolset(extended_oauth2_scheme, auth_credential),
        create_gmail_toolset(extended_oauth2_scheme, auth_credential)
    ]
)
```

#### 条件付きスコープ要求
```python
class ConditionalOAuth2Manager:
    def __init__(self):
        self.scope_requirements = {
            "read_calendar": ["https://www.googleapis.com/auth/calendar.readonly"],
            "manage_calendar": [
                "https://www.googleapis.com/auth/calendar.readonly",
                "https://www.googleapis.com/auth/calendar.events"
            ],
            "full_access": [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/gmail.readonly"
            ]
        }
    
    def create_oauth_scheme(self, permission_level: str) -> OAuth2:
        """権限レベルに応じたOAuth2スキーム作成"""
        
        required_scopes = self.scope_requirements.get(permission_level, [])
        
        scopes_dict = {}
        for scope in required_scopes:
            if "calendar" in scope:
                scopes_dict[scope] = "Google Calendar access"
            elif "gmail" in scope:
                scopes_dict[scope] = "Gmail access"
        
        return OAuth2(
            flows=OAuthFlows(
                authorizationCode=OAuthFlowAuthorizationCode(
                    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
                    tokenUrl="https://oauth2.googleapis.com/token",
                    scopes=scopes_dict,
                )
            )
        )
```

### 5.3 エンタープライズ統合パターン

#### マルチテナント OAuth2 管理
```python
class MultiTenantOAuth2Integration:
    def __init__(self):
        self.tenant_configs = {}
        
    def register_tenant(self, tenant_id: str, oauth_config: dict):
        """テナント別OAuth2設定の登録"""
        
        self.tenant_configs[tenant_id] = {
            "client_id": oauth_config["client_id"],
            "client_secret": oauth_config["client_secret"],
            "scopes": oauth_config["scopes"],
            "redirect_uri": oauth_config["redirect_uri"]
        }
    
    def create_tenant_agent(self, tenant_id: str) -> Agent:
        """テナント固有の統合エージェント作成"""
        
        config = self.tenant_configs[tenant_id]
        
        # テナント固有のOAuth2スキーム
        oauth_scheme = OAuth2(
            flows=OAuthFlows(
                authorizationCode=OAuthFlowAuthorizationCode(
                    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
                    tokenUrl="https://oauth2.googleapis.com/token",
                    scopes=config["scopes"],
                )
            )
        )
        
        # テナント固有の認証クレデンシャル
        auth_credential = AuthCredential(
            auth_type=AuthCredentialTypes.OAUTH2,
            oauth2=OAuth2Auth(
                client_id=config["client_id"],
                client_secret=config["client_secret"]
            )
        )
        
        # テナント固有のツールセット
        toolset = ApplicationIntegrationToolset(
            project=os.getenv("CONNECTION_PROJECT"),
            location=os.getenv("CONNECTION_LOCATION"),
            connection=f"tenant-{tenant_id}-connector",
            actions=["GET_calendars/%7BcalendarId%7D/events"],
            auth_scheme=oauth_scheme,
            auth_credential=auth_credential
        )
        
        return Agent(
            name=f"tenant_{tenant_id}_agent",
            tools=[toolset],
            instruction=f"You are the integration agent for tenant {tenant_id}"
        )
```

### 5.4 トークンライフサイクル管理

#### 自動トークンリフレッシュ
```python
class OAuth2TokenManager:
    def __init__(self):
        self.token_cache = {}
        self.refresh_threshold = 300  # 5分前にリフレッシュ
    
    async def get_valid_token(self, user_id: str, toolset: ApplicationIntegrationToolset):
        """有効なトークンの取得（必要に応じてリフレッシュ）"""
        
        if user_id not in self.token_cache:
            # 新規認証が必要
            return await self.initiate_oauth_flow(user_id, toolset)
        
        token_info = self.token_cache[user_id]
        
        # トークンの有効期限チェック
        if self.is_token_expiring(token_info):
            # トークンリフレッシュ
            return await self.refresh_token(user_id, token_info, toolset)
        
        return token_info["access_token"]
    
    def is_token_expiring(self, token_info: dict) -> bool:
        """トークンの有効期限チェック"""
        
        expires_at = token_info.get("expires_at", 0)
        current_time = time.time()
        
        return (expires_at - current_time) < self.refresh_threshold
    
    async def refresh_token(self, user_id: str, token_info: dict, toolset: ApplicationIntegrationToolset):
        """トークンのリフレッシュ"""
        
        refresh_token = token_info.get("refresh_token")
        
        if not refresh_token:
            # リフレッシュトークンがない場合は再認証
            return await self.initiate_oauth_flow(user_id, toolset)
        
        # リフレッシュリクエストの実行
        # (実装は OAuth2 標準リフレッシュフローに従う)
        pass
```

## 6. トラブルシューティング

### 6.1 OAuth2 認証の問題

#### 問題: "OAuth2 client credentials not found"
**原因と解決法**:
```bash
# 環境変数の確認
echo $CLIENT_ID
echo $CLIENT_SECRET

# Secret Manager での確認
gcloud secrets versions access latest --secret="oauth-client-credentials"

# 正しい形式での設定
export CLIENT_ID=your-actual-client-id
export CLIENT_SECRET=your-actual-client-secret
```

#### 問題: "Redirect URI mismatch"
**解決方法**:
```bash
# Google Cloud Console での設定確認
# 1. OAuth2 クライアント設定を開く
# 2. 承認済みのリダイレクト URI を確認
# 3. 以下のURIが設定されているか確認:
#    http://localhost/dev-ui/

# 環境に応じた設定例
# Development: http://localhost:8080/dev-ui/
# Staging: https://staging.company.com/dev-ui/
# Production: https://app.company.com/dev-ui/
```

### 6.2 Integration Connector (EUC) の問題

#### 問題: "EUC token exchange failed"
**解決方法**:
```bash
# EUC有効化の確認
gcloud integration connections describe calendar-euc-connector \
    --location=us-central1 \
    --format="value(eucConfig.enabled)"

# EUC設定の更新
gcloud integration connections update calendar-euc-connector \
    --location=us-central1 \
    --enable-euc

# OAuth2 Client Credentials Secret の確認
gcloud secrets versions access latest --secret="oauth-client-credentials" \
    --format="value(payload.data)" | base64 -d
```

### 6.3 権限とスコープの問題

#### 問題: "Insufficient OAuth2 scope"
**解決方法**:
```python
# スコープの拡張
extended_scopes = {
    "https://www.googleapis.com/auth/calendar.readonly": "Read calendar events",
    "https://www.googleapis.com/auth/calendar.events": "Manage calendar events",
    "https://www.googleapis.com/auth/calendar": "Full calendar access"
}

# 既存認証の無効化
def clear_oauth_tokens(user_id: str):
    """既存のOAuth2トークンをクリア"""
    # セッション状態またはトークンキャッシュをクリア
    pass

# 新しいスコープでの再認証
def request_extended_permissions(user_id: str, additional_scopes: list[str]):
    """追加スコープでの再認証要求"""
    # 新しいスコープを含むOAuth2フローを開始
    pass
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### EUC OAuth2 統合パターン
- **エンドユーザー認証**: ユーザー固有の認証フロー
- **Application Integration**: OAuth2 + 統合プラットフォームの組み合わせ
- **セキュアな認証管理**: 認証情報の適切な管理

#### OAuth2 設計パターン
```python
class OAuth2IntegrationPattern:
    """OAuth2統合の標準パターン"""
    
    def __init__(self, client_config: dict):
        self.client_config = client_config
        
    def create_oauth_scheme(self, scopes: dict) -> OAuth2:
        """OAuth2スキームの標準作成パターン"""
        return OAuth2(
            flows=OAuthFlows(
                authorizationCode=OAuthFlowAuthorizationCode(
                    authorizationUrl=self.client_config["auth_url"],
                    tokenUrl=self.client_config["token_url"],
                    scopes=scopes,
                )
            )
        )
    
    def create_auth_credential(self) -> AuthCredential:
        """認証クレデンシャルの標準作成パターン"""
        return AuthCredential(
            auth_type=AuthCredentialTypes.OAUTH2,
            oauth2=OAuth2Auth(
                client_id=self.client_config["client_id"],
                client_secret=self.client_config["client_secret"]
            )
        )
```

### 7.2 セキュリティベストプラクティス

#### 認証情報の保護
```python
class SecureCredentialManager:
    def __init__(self):
        self.secret_client = secretmanager.SecretManagerServiceClient()
        
    def get_oauth_credentials(self, project_id: str, secret_name: str) -> dict:
        """Secret Managerから安全にOAuth認証情報を取得"""
        
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = self.secret_client.access_secret_version(request={"name": name})
        
        secret_data = response.payload.data.decode("UTF-8")
        return json.loads(secret_data)
    
    def rotate_oauth_credentials(self, project_id: str, secret_name: str, new_credentials: dict):
        """OAuth認証情報のローテーション"""
        
        # 新しいバージョンのシークレット作成
        parent = f"projects/{project_id}/secrets/{secret_name}"
        payload = json.dumps(new_credentials).encode("UTF-8")
        
        self.secret_client.add_secret_version(
            request={
                "parent": parent,
                "payload": {"data": payload}
            }
        )
```

#### スコープの最小化
```python
class MinimalScopeManager:
    """最小スコープ管理"""
    
    SCOPE_DEFINITIONS = {
        "calendar_read": ["https://www.googleapis.com/auth/calendar.readonly"],
        "calendar_write": [
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events"
        ],
        "calendar_full": ["https://www.googleapis.com/auth/calendar"]
    }
    
    def get_minimal_scopes(self, required_operations: list[str]) -> list[str]:
        """必要な操作に対する最小スコープの決定"""
        
        required_scopes = set()
        
        for operation in required_operations:
            if operation in ["read_events", "list_calendars"]:
                required_scopes.update(self.SCOPE_DEFINITIONS["calendar_read"])
            elif operation in ["create_event", "update_event"]:
                required_scopes.update(self.SCOPE_DEFINITIONS["calendar_write"])
            elif operation in ["delete_calendar", "manage_permissions"]:
                required_scopes.update(self.SCOPE_DEFINITIONS["calendar_full"])
        
        return list(required_scopes)
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **最小スコープ**: 必要最小限のOAuth2スコープを要求
- **セキュアな保存**: 認証情報のSecret Manager使用
- **トークン管理**: 適切なトークンライフサイクル管理
- **エラーハンドリング**: OAuth2エラーの適切な処理

#### 注意点
- **プライバシー**: ユーザーデータの適切な取り扱い
- **同意**: ユーザーへの明確な権限説明
- **セキュリティ**: 認証情報の適切な保護
- **可用性**: 認証サービス障害時の対応

### 7.4 他のプロジェクトへの応用

#### SaaS統合プラットフォーム
```python
class SaaSIntegrationPlatform:
    """SaaS統合プラットフォーム"""
    
    def __init__(self):
        self.oauth_providers = {
            "google": GoogleOAuth2Provider(),
            "microsoft": MicrosoftOAuth2Provider(),
            "salesforce": SalesforceOAuth2Provider(),
            "slack": SlackOAuth2Provider()
        }
    
    async def create_user_integration(self, user_id: str, provider: str, scopes: list[str]):
        """ユーザー固有のSaaS統合作成"""
        
        oauth_provider = self.oauth_providers[provider]
        
        # プロバイダー固有のOAuth2フロー
        auth_scheme = oauth_provider.create_oauth_scheme(scopes)
        auth_credential = oauth_provider.create_auth_credential()
        
        # 統合ツールセット作成
        toolset = ApplicationIntegrationToolset(
            project=os.getenv("CONNECTION_PROJECT"),
            location=os.getenv("CONNECTION_LOCATION"),
            connection=oauth_provider.connection_name,
            auth_scheme=auth_scheme,
            auth_credential=auth_credential
        )
        
        return Agent(
            name=f"{user_id}_{provider}_agent",
            tools=[toolset],
            instruction=f"You are the {provider} integration agent for user {user_id}"
        )
```

この integration_connector_euc_agent は、OAuth2エンドユーザー認証を使用した安全で標準的な外部API統合パターンを学ぶのに最適な例です。Google Cloud Application Integration との組み合わせにより、エンタープライズレベルのセキュリティ要件を満たしながら、柔軟なSaaS統合を実現する方法を習得できます。