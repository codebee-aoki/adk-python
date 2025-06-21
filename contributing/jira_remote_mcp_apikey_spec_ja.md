# Jira リモート MCP サーバーエージェント仕様書（APIキー認証）

## 概要

この仕様書は、APIキー認証を使用してAtlassianのリモートJira MCPサーバーに接続するADKエージェントを定義します。`jira_api_agent`のローカルMCPサーバーアプローチとは異なり、このエージェントは`https://mcp.atlassian.com/v1/sse`にあるAtlassianのホスティングMCPエンドポイントに直接接続します。

## アーキテクチャ

### 接続方法
- **プロトコル**: Server-Sent Events (SSE)
- **エンドポイント**: `https://mcp.atlassian.com/v1/sse`
- **接続タイプ**: ADKのMCPツールセットの`SseConnectionParams`

### 認証
- **方式**: HTTPヘッダーのAPIキー
- **必要な認証情報**:
  - JiraインスタンスURL（例：`https://yourcompany.atlassian.net`）
  - ユーザーのメールアドレス
  - Atlassian APIトークン（Atlassianアカウント設定から生成）

## 実装詳細

### ディレクトリ構造
```
contributing/samples/jira_remote_mcp_apikey_agent/
├── __init__.py
├── agent.py
├── .env.example
├── README.md
└── requirements.txt
```

### 環境設定

`.env.example`:
```env
# JiraインスタンスのURL
JIRA_URL=https://yourcompany.atlassian.net

# Atlassianアカウントのメールアドレス
JIRA_EMAIL=your.email@company.com

# Atlassian APIトークン（生成元: https://id.atlassian.com/manage-profile/security/api-tokens）
JIRA_API_TOKEN=your_api_token_here
```

### エージェント実装

`agent.py`:
```python
import os
import base64
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# 環境変数の読み込み
load_dotenv()

# 設定の検証
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise ValueError(
        "必要な環境変数が不足しています。.envファイルを確認してください。"
    )

# Basic認証ヘッダーの作成
auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

# 認証ヘッダー付きMCP接続の設定
jira_remote_tools = MCPToolset(
    connection_params=SseConnectionParams(
        url="https://mcp.atlassian.com/v1/sse",
        headers={
            "Authorization": f"Basic {auth_b64}",
            "X-Atlassian-Instance-URL": JIRA_URL,
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        },
        timeout=10.0,
        sse_read_timeout=300.0  # 長時間実行操作用に5分
    )
)

# エージェントの作成
root_agent = Agent(
    name="jira_remote_mcp_agent",
    model="gemini-2.0-flash",
    instruction="""あなたはリモートAtlassian MCPサーバーに接続されたJiraプロジェクト管理アシスタントです。

利用可能な機能:
1. Jira課題の検索とフィルタリング
2. 課題の詳細情報取得
3. 新規課題の作成
4. 課題へのコメント追加
5. 課題フィールドとトランジションの更新
6. JQLクエリの実行
7. プロジェクト情報の管理
8. ユーザーとチームの作業

AtlassianのMCPサーバーを通じて組織のJiraインスタンスに直接アクセスできます。
常に明確で整理された応答を提供し、Jiraの全機能を活用してプロジェクト管理タスクを支援してください。
""",
    tools=[jira_remote_tools],
)
```

## 利用可能なツール

リモートMCPサーバーは以下を含むJira操作へのアクセスを提供します：

### 課題管理
- `jira_search_issues` - JQLを使用した課題検索
- `jira_get_issue` - 課題の詳細情報取得
- `jira_create_issue` - 新規課題作成
- `jira_update_issue` - 課題フィールドの更新
- `jira_transition_issue` - 課題ステータスの変更
- `jira_add_comment` - 課題へのコメント追加

### プロジェクト操作
- `jira_get_projects` - 利用可能なプロジェクト一覧
- `jira_get_project` - プロジェクト詳細の取得
- `jira_get_project_components` - プロジェクトコンポーネント一覧
- `jira_get_project_versions` - プロジェクトバージョン一覧

### ユーザーとチーム管理
- `jira_get_user` - ユーザー情報の取得
- `jira_search_users` - ユーザー検索
- `jira_get_groups` - ユーザーグループ一覧

### 高度な機能
- `jira_execute_jql` - カスタムJQLクエリの実行
- `jira_get_fields` - 利用可能なカスタムフィールドの取得
- `jira_get_issue_types` - 課題タイプ一覧
- `jira_get_priorities` - 優先度レベル一覧

## セキュリティに関する考慮事項

### APIトークン管理
- APIトークンは環境変数に保存し、コードには含めない
- ローカルでは適切な`.gitignore`設定で`.env`ファイルを使用
- 本番環境では、安全なシークレット管理サービスを使用
- APIトークンを定期的にローテーション

### ネットワークセキュリティ
- すべての接続はHTTPS/TLSを使用
- リクエストレート制限の実装を検討
- Atlassian管理コンソールでAPI使用状況を監視

### アクセス制御
- APIトークンは関連付けられたユーザーの権限を継承
- 適切な権限を持つ専用のサービスアカウントを作成
- 最小権限の原則に従う

## エラーハンドリング

エージェントは一般的なエラーシナリオを処理する必要があります：

```python
# 接続エラー
try:
    await jira_remote_tools.get_tools()
except ConnectionError as e:
    logger.error(f"Jira MCPサーバーへの接続に失敗しました: {e}")
    # リトライロジックまたはフォールバックの実装

# 認証エラー (401)
# MCPツールセットが内部的に認証エラーを処理
# 認証失敗のログを監視

# レート制限 (429)
# レート制限エラーに対して指数バックオフを実装
```

## テストガイドライン

### ユニットテスト
```python
# 接続設定のテスト
def test_sse_connection_params():
    params = SseConnectionParams(
        url="https://mcp.atlassian.com/v1/sse",
        headers={"Authorization": "Basic test_token"}
    )
    assert params.url == "https://mcp.atlassian.com/v1/sse"
    assert "Authorization" in params.headers

# 認証ヘッダー生成のテスト
def test_auth_header_generation():
    email = "test@example.com"
    token = "test_token"
    auth_string = f"{email}:{token}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    assert auth_b64 == "dGVzdEBleGFtcGxlLmNvbTp0ZXN0X3Rva2Vu"
```

### 統合テスト
- サンドボックスJiraインスタンスでテスト
- すべてのツール操作が正しく動作することを確認
- エラーハンドリングとエッジケースのテスト
- パフォーマンスとレイテンシの監視

## デプロイメントに関する考慮事項

### 環境固有の設定
```python
# 複数環境のサポート
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    SSE_TIMEOUT = 300.0  # 本番環境では5分
    CONNECTION_TIMEOUT = 30.0
else:
    SSE_TIMEOUT = 60.0  # 開発環境では1分
    CONNECTION_TIMEOUT = 10.0
```

### モニタリングとロギング
```python
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 重要なイベントのログ
logger.info(f"インスタンス用のJira MCPサーバーに接続中: {JIRA_URL}")
```

## ローカルMCPサーバーからの移行

ローカルのDockerベースのアプローチから移行するには：

1. Docker依存関係を削除
2. 接続パラメータを`StdioConnectionParams`から`SseConnectionParams`に更新
3. 認証ヘッダーを追加
4. MCPサーバーURLを更新
5. 既存のすべての機能をテスト

## 制限事項と考慮事項

1. **ネットワーク依存性**: 安定したインターネット接続が必要
2. **レイテンシ**: リモート接続はローカルサーバーよりも高いレイテンシがある可能性
3. **レート制限**: Atlassian APIレート制限の対象
4. **機能の同等性**: リモートMCPサーバーが必要なすべての操作をサポートしていることを確認

## 参考資料

- [Atlassian APIトークン](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- [Jira REST APIドキュメント](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [MCP仕様](https://modelcontextprotocol.io/specification)
- [ADK MCPドキュメント](https://github.com/google/adk-python/blob/main/docs/tools.md#mcp-tools)