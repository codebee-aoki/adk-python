# oauth_calendar_agent - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`oauth_calendar_agent` エージェントは、ADK における OAuth2 認証フローの実装と Google Calendar API との統合を学習するための包括的なサンプルです。カスタムツールとビルドインツールの組み合わせにより、認証からAPI呼び出しまでの完全なワークフローを実装しています。

### 主要機能
- **カスタム OAuth2 実装**: 手動での認証フロー管理
- **カレンダーイベント検索**: 時間範囲指定でのイベント取得
- **イベント詳細取得**: ビルドインツールによる詳細情報取得
- **セッション状態管理**: 認証トークンの永続化
- **動的時刻更新**: コールバックによる現在時刻の提供

### 対象ユースケース
- OAuth2 認証フローの学習と実装
- Google API との安全な統合
- 認証状態の管理パターン
- カスタムツールとビルドインツールの組み合わせ

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (カレンダー操作要求)
[oauth_calendar_agent] 
    ↓ (OAuth2 認証フロー)
┌─────────────────────────────────────────────────────────┐
│ OAuth2 認証フロー                                        │
│ 1. 認証情報チェック                                      │
│ 2. 認証URL生成とリダイレクト                             │
│ 3. 認証コード受信                                        │
│ 4. アクセストークン取得                                  │
│ 5. トークンのセッション保存                              │
└─────────────────────────────────────────────────────────┘
    ↓ (認証済みAPI呼び出し)
[Google Calendar API]
    ├── Events.list - イベント一覧取得
    └── Events.get - イベント詳細取得
    ↓ (カレンダーデータ)
[ユーザーのGoogleカレンダー]
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス + Calendar 機能)
- **カスタムツール**: `list_calendar_events` (手動OAuth2実装)
- **ビルドインツール**: `calendar_events_get` (CalendarToolset)
- **認証管理**: OAuth2Auth + AuthConfig
- **セッション管理**: ToolContext.state でのトークン保存
- **時刻管理**: before_agent_callback での動的時刻更新

### OAuth2 認証フロー詳細
```python
1. 認証状態チェック
   └── tool_context.state["calendar_tool_tokens"] の確認

2. トークン有効性検証
   ├── アクセストークンの有効期限確認
   └── リフレッシュトークンによる更新

3. 新規認証フロー
   ├── OAuth2スキーム定義
   ├── AuthCredential 作成
   ├── tool_context.request_credential() 呼び出し
   └── ユーザー認証完了待機

4. トークン取得と保存
   ├── auth_response から token 抽出
   ├── Credentials オブジェクト作成
   └── セッション状態への保存
```

### 依存関係
```python
# OAuth2 認証
from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows

# Google API クライアント
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ADK コンポーネント
from google.adk import Agent
from google.adk.tools.google_api_tool import CalendarToolset
from google.adk.tools import ToolContext
```

## 3. コード詳細解説

### 3.1 カスタム OAuth2 実装

#### list_calendar_events ツール
```python
def list_calendar_events(
    start_time: str,
    end_time: str,
    limit: int,
    tool_context: ToolContext,
) -> list[dict]:
```

**OAuth2 認証フローの詳細実装**:

#### ステップ1: 認証状態の確認
```python
# セッション状態からトークンを確認
if "calendar_tool_tokens" in tool_context.state:
    creds = Credentials.from_authorized_user_info(
        tool_context.state["calendar_tool_tokens"], SCOPES
    )
```

#### ステップ2: トークンリフレッシュ
```python
if not creds or not creds.valid:
    # 期限切れの場合はリフレッシュ
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
```

#### ステップ3: 新規認証フロー
```python
else:
    # OAuth2スキーム定義
    auth_scheme = OAuth2(
        flows=OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl="https://accounts.google.com/o/oauth2/auth",
                tokenUrl="https://oauth2.googleapis.com/token",
                scopes={
                    "https://www.googleapis.com/auth/calendar": (
                        "See, edit, share, and permanently delete all the"
                        " calendars you can access using Google Calendar"
                    )
                },
            )
        )
    )
    
    # 認証クレデンシャル作成
    auth_credential = AuthCredential(
        auth_type=AuthCredentialTypes.OAUTH2,
        oauth2=OAuth2Auth(
            client_id=oauth_client_id, 
            client_secret=oauth_client_secret
        ),
    )
```

#### ステップ4: 認証レスポンス処理
```python
# 認証レスポンスの確認
auth_response = tool_context.get_auth_response(
    AuthConfig(
        auth_scheme=auth_scheme, 
        raw_auth_credential=auth_credential
    )
)

if auth_response:
    # トークン取得成功
    access_token = auth_response.oauth2.access_token
    refresh_token = auth_response.oauth2.refresh_token
    
    # Credentials オブジェクト作成
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=auth_scheme.flows.authorizationCode.tokenUrl,
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        scopes=list(auth_scheme.flows.authorizationCode.scopes.keys()),
    )
else:
    # 認証が必要
    tool_context.request_credential(
        AuthConfig(
            auth_scheme=auth_scheme,
            raw_auth_credential=auth_credential,
        )
    )
    return "Need User Authorization to access their calendar."
```

#### ステップ5: トークン永続化
```python
# セッション状態への保存
tool_context.state["calendar_tool_tokens"] = json.loads(creds.to_json())
```

### 3.2 Google Calendar API 呼び出し

```python
# 認証済みサービス作成
service = build("calendar", "v3", credentials=creds)

# イベント一覧取得
events_result = (
    service.events()
    .list(
        calendarId="primary",
        timeMin=start_time + "Z" if start_time else None,
        timeMax=end_time + "Z" if end_time else None,
        maxResults=limit,
        singleEvents=True,
        orderBy="startTime",
    )
    .execute()
)

events = events_result.get("items", [])
return events
```

### 3.3 ビルドイン CalendarToolset 統合

```python
calendar_toolset = CalendarToolset(
    client_id=oauth_client_id,
    client_secret=oauth_client_secret,
    tool_filter=["calendar_events_get"],  # 詳細取得機能のみ
)
```

**設計の利点**:
- **機能分離**: カスタム実装とビルドイン機能の組み合わせ
- **学習価値**: 両方の実装アプローチを比較学習
- **実用性**: 用途に応じた最適な選択

### 3.4 時刻管理コールバック

```python
def update_time(callback_context: CallbackContext):
    # 現在時刻の取得とフォーマット
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    callback_context.state["_time"] = formatted_time

# エージェント設定でのコールバック使用
root_agent = Agent(
    before_agent_callback=update_time,
    instruction="Current time: {_time}",  # 動的時刻挿入
    # ...
)
```

## 4. 設定・環境構築

### 4.1 Google Cloud Console 設定

#### OAuth2 アプリケーション作成
1. **Google Cloud Console** → **API とサービス** → **認証情報**
2. **認証情報を作成** → **OAuth 2.0 クライアント ID**
3. **アプリケーションの種類**: ウェブアプリケーション
4. **承認済みのリダイレクト URI**:
   ```
   http://localhost/dev-ui/
   ```

#### Google Calendar API 有効化
```bash
# gcloud CLI での有効化
gcloud services enable calendar-json.googleapis.com

# スコープの確認
# https://www.googleapis.com/auth/calendar
```

### 4.2 環境変数設定

```bash
# .env ファイル設定
OAUTH_CLIENT_ID=your_oauth_client_id
OAUTH_CLIENT_SECRET=your_oauth_client_secret

# 追加設定（オプション）
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 4.3 権限とスコープ

#### 必要なスコープ
```python
SCOPES = ["https://www.googleapis.com/auth/calendar"]
```

**スコープの詳細**:
- `calendar`: カレンダーの読み取り・編集権限
- `calendar.readonly`: 読み取り専用権限（必要に応じて変更）

#### ユーザー同意画面の設定
1. **OAuth 同意画面** の設定
2. **スコープの追加**: Google Calendar API
3. **テストユーザー** の追加（開発時）

### 4.4 実行とテスト

```bash
# 開発環境での実行
adk web contributing/samples/oauth_calendar_agent

# ブラウザでの動作確認
# 1. 初回実行時: OAuth認証フローが開始
# 2. Google認証画面でのログイン
# 3. カレンダーアクセス許可
# 4. 認証完了後のツール実行
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### カレンダーイベントの検索
```
ユーザー: "List all my today's meeting from 7am to 7pm."
エージェント: [list_calendar_events を実行]
"I found 3 meetings today:
1. Team Standup (9:00-9:30)
2. Project Review (14:00-15:00)  
3. Client Call (16:00-17:00)"

ユーザー: "Get the details of the first event."
エージェント: [calendar_events_get を実行]
"Team Standup Details: Location: Conference Room A, Attendees: john@example.com, jane@example.com"
```

### 5.2 高度な認証パターン

#### マルチユーザー対応
```python
class MultiUserCalendarAgent:
    def __init__(self):
        self.user_agents = {}
    
    def create_user_agent(self, user_id: str, client_id: str, client_secret: str):
        """ユーザー固有のカレンダーエージェント作成"""
        
        def user_specific_list_events(start_time: str, end_time: str, limit: int, tool_context: ToolContext):
            # ユーザー固有の認証状態管理
            token_key = f"calendar_tokens_{user_id}"
            
            if token_key in tool_context.state:
                # ユーザー固有のトークンを使用
                pass
            
            # OAuth2 フロー実装...
            
        agent = Agent(
            name=f"calendar_agent_{user_id}",
            tools=[user_specific_list_events],
            # ...
        )
        
        self.user_agents[user_id] = agent
        return agent
```

#### 認証状態の監視と管理
```python
class AuthenticationManager:
    def __init__(self):
        self.token_monitor = {}
    
    def monitor_token_health(self, tool_context: ToolContext) -> dict:
        """認証トークンの健全性を監視"""
        
        if "calendar_tool_tokens" not in tool_context.state:
            return {"status": "no_auth", "action": "auth_required"}
        
        creds_data = tool_context.state["calendar_tool_tokens"]
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                return {"status": "expired", "action": "refresh_available"}
            else:
                return {"status": "invalid", "action": "reauth_required"}
        
        # トークンの有効期限確認
        expires_in = (creds.expiry - datetime.utcnow()).total_seconds()
        
        if expires_in < 300:  # 5分以内に期限切れ
            return {"status": "expiring_soon", "action": "proactive_refresh"}
        
        return {"status": "healthy", "action": "none"}
```

### 5.3 カレンダー操作の拡張

#### 高度なクエリ機能
```python
def advanced_calendar_search(
    query: str,
    start_time: str,
    end_time: str,
    calendar_ids: list[str],
    tool_context: ToolContext
) -> list[dict]:
    """高度なカレンダー検索機能"""
    
    # 認証処理...
    service = build("calendar", "v3", credentials=creds)
    
    all_events = []
    
    # 複数カレンダーの検索
    for calendar_id in calendar_ids:
        events_result = service.events().list(
            calendarId=calendar_id,
            q=query,  # テキスト検索
            timeMin=start_time + "Z",
            timeMax=end_time + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        for event in events:
            event["calendar_id"] = calendar_id
        
        all_events.extend(events)
    
    return all_events
```

#### イベント作成機能
```python
def create_calendar_event(
    title: str,
    start_datetime: str,
    end_datetime: str,
    description: str,
    attendees: list[str],
    tool_context: ToolContext
) -> dict:
    """カレンダーイベントの作成"""
    
    # 認証処理...
    service = build("calendar", "v3", credentials=creds)
    
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Asia/Tokyo',
        },
        'attendees': [{'email': email} for email in attendees],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    
    created_event = service.events().insert(
        calendarId='primary', 
        body=event
    ).execute()
    
    return {
        "status": "success",
        "event_id": created_event['id'],
        "event_link": created_event.get('htmlLink')
    }
```

## 6. トラブルシューティング

### 6.1 OAuth2 認証の問題

#### 問題: "認証フローが開始されない"
**原因と解決法**:
```bash
# 1. 環境変数の確認
echo $OAUTH_CLIENT_ID
echo $OAUTH_CLIENT_SECRET

# 2. リダイレクトURIの確認
# Google Cloud Console での設定を確認:
# - http://localhost/dev-ui/ が正確に設定されているか
# - アプリケーションタイプが「ウェブアプリケーション」か

# 3. ブラウザ設定
# ポップアップブロッカーの無効化
# Cookie とサイトデータの有効化
```

#### 問題: "invalid_grant エラー"
**解決方法**:
```python
# トークンをクリアして再認証
def clear_auth_state(tool_context: ToolContext):
    """認証状態をクリア"""
    if "calendar_tool_tokens" in tool_context.state:
        del tool_context.state["calendar_tool_tokens"]
    
    # セッション全体のクリア（必要に応じて）
    tool_context.state.clear()
```

### 6.2 API 呼び出しの問題

#### 問題: "Calendar API が有効化されていない"
```bash
# API の有効化
gcloud services enable calendar-json.googleapis.com

# 有効化状況の確認
gcloud services list --enabled | grep calendar
```

#### 問題: "権限不足エラー"
**解決方法**:
```python
# スコープの追加・変更
EXTENDED_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly"
]

# 既存認証の無効化と再認証
def upgrade_scopes(tool_context: ToolContext):
    # 古いトークンを削除
    if "calendar_tool_tokens" in tool_context.state:
        del tool_context.state["calendar_tool_tokens"]
    
    # 新しいスコープで認証フロー開始
    # ...
```

### 6.3 パフォーマンスとレート制限

#### API使用量の最適化
```python
# バッチリクエストの実装
def batch_calendar_operations(operations: list[dict], tool_context: ToolContext):
    """複数のカレンダー操作をバッチで実行"""
    
    service = build("calendar", "v3", credentials=creds)
    
    # バッチリクエストの作成
    batch = service.new_batch_http_request()
    
    for op in operations:
        if op["type"] == "get_event":
            batch.add(
                service.events().get(
                    calendarId=op["calendar_id"],
                    eventId=op["event_id"]
                )
            )
    
    # バッチ実行
    batch.execute()
```

#### レート制限の処理
```python
import time
from googleapiclient.errors import HttpError

def rate_limited_api_call(api_function, *args, **kwargs):
    """レート制限を考慮したAPI呼び出し"""
    
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            return api_function(*args, **kwargs)
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                raise e
    
    raise Exception("Max retries exceeded for rate limited request")
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### カスタム OAuth2 実装パターン
- **段階的認証**: 状態確認 → リフレッシュ → 新規認証の流れ
- **セッション管理**: 認証状態の永続化とライフサイクル管理
- **エラーハンドリング**: 認証エラーの適切な処理と回復

#### 混合ツール戦略
```python
# カスタムとビルドインの組み合わせ
class HybridCalendarAgent:
    def __init__(self):
        # カスタムツール: 柔軟性重視
        self.custom_tools = [list_calendar_events]
        
        # ビルドインツール: 簡単さ重視
        self.builtin_toolset = CalendarToolset(
            client_id=oauth_client_id,
            client_secret=oauth_client_secret,
            tool_filter=["calendar_events_get", "calendar_events_insert"]
        )
    
    def get_optimal_tool(self, operation_type: str):
        """操作タイプに応じた最適なツール選択"""
        if operation_type == "complex_search":
            return self.custom_tools
        else:
            return self.builtin_toolset
```

### 7.2 セキュリティベストプラクティス

#### 認証情報の安全な管理
```python
class SecureTokenManager:
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key
    
    def store_tokens(self, tokens: dict, tool_context: ToolContext):
        """トークンの暗号化保存"""
        encrypted_tokens = self.encrypt_data(tokens)
        tool_context.state["encrypted_calendar_tokens"] = encrypted_tokens
    
    def retrieve_tokens(self, tool_context: ToolContext) -> dict:
        """トークンの復号化取得"""
        encrypted_tokens = tool_context.state.get("encrypted_calendar_tokens")
        if encrypted_tokens:
            return self.decrypt_data(encrypted_tokens)
        return None
    
    def encrypt_data(self, data: dict) -> str:
        """データの暗号化（実装は省略）"""
        pass
    
    def decrypt_data(self, encrypted_data: str) -> dict:
        """データの復号化（実装は省略）"""
        pass
```

#### スコープの最小化
```python
# 機能別スコープ設定
SCOPE_CONFIGS = {
    "read_only": ["https://www.googleapis.com/auth/calendar.readonly"],
    "read_write": ["https://www.googleapis.com/auth/calendar"],
    "events_only": ["https://www.googleapis.com/auth/calendar.events"]
}

def create_scoped_agent(access_level: str):
    """アクセスレベルに応じたエージェント作成"""
    scopes = SCOPE_CONFIGS.get(access_level, SCOPE_CONFIGS["read_only"])
    
    # スコープ制限されたエージェント実装
    # ...
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **段階的認証**: 認証フローの段階的な実装と検証
- **状態管理**: 適切なセッション状態管理とクリーンアップ
- **エラー処理**: 包括的なエラーハンドリングとユーザーフィードバック
- **セキュリティ**: 認証情報の暗号化と適切なスコープ設定

#### 注意点
- **トークン管理**: リフレッシュトークンの適切な管理
- **プライバシー**: ユーザーカレンダーデータの適切な取り扱い
- **API制限**: Google Calendar API の使用量制限への配慮
- **同期**: 複数デバイス・セッション間でのトークン同期問題

### 7.4 他のプロジェクトへの応用

#### エンタープライズカレンダー統合
```python
class EnterpriseCalendarIntegration:
    """企業向けカレンダー統合システム"""
    
    def __init__(self):
        self.service_accounts = {}
        self.user_delegates = {}
    
    async def setup_domain_wide_delegation(self, domain: str, service_account_path: str):
        """ドメイン全体の委任設定"""
        # サービスアカウント認証での実装
        pass
    
    async def sync_multi_calendar_systems(self, systems: list[str]):
        """複数カレンダーシステムの同期"""
        # Outlook, Slack, Zoom 等との統合
        pass
```

#### AI アシスタント統合
```python
class AICalendarAssistant:
    """AI駆動のカレンダーアシスタント"""
    
    def __init__(self, calendar_agent):
        self.calendar_agent = calendar_agent
        self.ai_scheduler = None
    
    async def intelligent_scheduling(self, meeting_request: str):
        """AIによるインテリジェントスケジューリング"""
        # 1. 自然言語の解析
        # 2. 空き時間の検索
        # 3. 最適な時間の提案
        # 4. 自動的な会議設定
        pass
    
    async def conflict_resolution(self, conflicts: list[dict]):
        """会議衝突の自動解決"""
        # 優先度ベースの自動調整
        pass
```

この oauth_calendar_agent は、OAuth2 認証の包括的な実装と Google API 統合の実用的なパターンを学ぶのに最適な例です。カスタム認証実装とビルドインツールの組み合わせにより、柔軟性と使いやすさの両方を実現する方法を学習できます。