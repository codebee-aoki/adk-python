# Jira接続エージェント実装仕様書

## 目次
1. [概要](#概要)
2. [アーキテクチャ比較](#アーキテクチャ比較)
3. [パターン1: APIキー認証パターン](#パターン1-apiキー認証パターン)
4. [パターン2: OAuth2 MCP リモートサーバーパターン](#パターン2-oauth2-mcp-リモートサーバーパターン)
5. [パターン3: Google Cloud Application Integration パターン](#パターン3-google-cloud-application-integration-パターン)
6. [パターン4: MCP STDIO ローカルサーバーパターン](#パターン4-mcp-stdio-ローカルサーバーパターン)
7. [パターン5: 直接API統合パターン](#パターン5-直接api統合パターン)
8. [パターン選択ガイド](#パターン選択ガイド)
9. [セキュリティ考慮事項](#セキュリティ考慮事項)
10. [実装のベストプラクティス](#実装のベストプラクティス)

## 概要

本仕様書は、ADK (Agent Development Kit) を使用して Jira に接続するエージェントを実装するための包括的なガイドです。5つの異なる実装パターンを提供し、それぞれの用途、利点、実装方法を詳細に解説します。

### 対象読者
- ADK を使用して Jira 統合を実装する開発者
- エンタープライズシステム統合を検討しているアーキテクト
- セキュアな認証パターンを学習したいエンジニア

### 前提条件
- Python 3.11+ および ADK の基本的な理解
- Jira Cloud アカウントまたは Jira Server へのアクセス
- 各パターンに応じた追加要件（後述）

## アーキテクチャ比較

### 各パターンの概要

| パターン | 認証方式 | 複雑度 | セキュリティ | 適用場面 |
|---------|---------|--------|------------|----------|
| 1. APIキー | API Token | 低 | 基本 | 個人開発、プロトタイプ |
| 2. OAuth2 MCP | OAuth 2.0 | 高 | 高 | エンタープライズ、本番環境 |
| 3. GCP統合 | GCP管理 | 中 | 高 | Google Cloud 環境 |
| 4. MCP STDIO | API Token | 中 | 基本 | ローカル開発環境 |
| 5. 直接API | 任意 | 低〜高 | 可変 | カスタム要件 |

### アーキテクチャ図

```
┌─────────────────────────────────────────────────────────┐
│                     ADK エージェント                      │
├─────────────────────────────────────────────────────────┤
│ パターン1 │ パターン2 │ パターン3 │ パターン4 │ パターン5 │
│  API Key  │  OAuth2   │   GCP     │MCP STDIO │ Direct  │
├───────────┼───────────┼───────────┼──────────┼─────────┤
│  直接API  │MCP Remote │App Integ. │MCP Local │Custom   │
└───────────┴───────────┴───────────┴──────────┴─────────┘
                           ↓
                     Jira Cloud/Server
```

## パターン1: APIキー認証パターン

### 概要
最もシンプルで迅速に実装可能なパターン。Atlassian API Token を使用して直接 Jira REST API を呼び出します。

### 実装仕様

#### 必要な認証情報
```bash
# .env ファイル
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-generated-api-token
```

#### エージェント実装
```python
import os
import base64
import json
from typing import Dict, List, Optional
from google.adk import Agent
from google.adk.tools import ToolContext
import httpx

# 認証情報の読み込み
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# 認証ヘッダーの作成
auth_string = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
auth_bytes = auth_string.encode("ascii")
auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

HEADERS = {
    "Authorization": f"Basic {auth_b64}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# カスタムツール実装
def search_jira_issues(
    jql: str = "project = PROJ ORDER BY created DESC",
    max_results: int = 50,
    tool_context: ToolContext = None
) -> List[Dict]:
    """JQL を使用して Jira 課題を検索"""
    
    async def _search():
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{JIRA_URL}/rest/api/3/search",
                headers=HEADERS,
                params={
                    "jql": jql,
                    "maxResults": max_results,
                    "fields": "key,summary,status,assignee,priority,created,updated"
                }
            )
            response.raise_for_status()
            return response.json()
    
    import asyncio
    result = asyncio.run(_search())
    
    issues = []
    for issue in result.get("issues", []):
        issues.append({
            "key": issue["key"],
            "summary": issue["fields"]["summary"],
            "status": issue["fields"]["status"]["name"],
            "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned",
            "priority": issue["fields"]["priority"]["name"] if issue["fields"]["priority"] else "None",
            "created": issue["fields"]["created"],
            "updated": issue["fields"]["updated"]
        })
    
    return issues

def get_jira_issue(
    issue_key: str,
    tool_context: ToolContext = None
) -> Dict:
    """特定の Jira 課題の詳細を取得"""
    
    async def _get_issue():
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{JIRA_URL}/rest/api/3/issue/{issue_key}",
                headers=HEADERS
            )
            response.raise_for_status()
            return response.json()
    
    import asyncio
    issue = asyncio.run(_get_issue())
    
    return {
        "key": issue["key"],
        "summary": issue["fields"]["summary"],
        "description": issue["fields"]["description"],
        "status": issue["fields"]["status"]["name"],
        "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned",
        "reporter": issue["fields"]["reporter"]["displayName"],
        "priority": issue["fields"]["priority"]["name"] if issue["fields"]["priority"] else "None",
        "created": issue["fields"]["created"],
        "updated": issue["fields"]["updated"],
        "comments": len(issue["fields"]["comment"]["comments"])
    }

def create_jira_issue(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    priority: str = "Medium",
    tool_context: ToolContext = None
) -> Dict:
    """新しい Jira 課題を作成"""
    
    issue_data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": issue_type},
            "priority": {"name": priority}
        }
    }
    
    async def _create_issue():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{JIRA_URL}/rest/api/3/issue",
                headers=HEADERS,
                json=issue_data
            )
            response.raise_for_status()
            return response.json()
    
    import asyncio
    result = asyncio.run(_create_issue())
    
    return {
        "key": result["key"],
        "id": result["id"],
        "self": result["self"],
        "status": "Created successfully"
    }

# エージェント定義
jira_api_agent = Agent(
    name="jira_api_agent",
    model="gemini-2.0-flash",
    instruction="""あなたは Jira プロジェクト管理アシスタントです。
    
    以下の機能を提供します：
    1. JQL を使用した課題検索
    2. 特定の課題の詳細取得
    3. 新しい課題の作成
    
    ユーザーの要求に応じて適切なツールを使用し、明確で整理された情報を提供してください。
    """,
    tools=[search_jira_issues, get_jira_issue, create_jira_issue]
)
```

### 利点
- **実装が簡単**: 数分で動作確認可能
- **直接的**: 中間レイヤーが不要
- **低レイテンシー**: API への直接アクセス
- **完全な制御**: カスタムロジックの実装が容易

### 制限事項
- API Token は個人に紐づく
- Token の手動管理が必要
- 複数ユーザーでの共有に不適

### セットアップ手順
1. [Atlassian API Token 管理ページ](https://id.atlassian.com/manage-profile/security/api-tokens) でトークンを生成
2. 環境変数を設定
3. エージェントを実行

## パターン2: OAuth2 MCP リモートサーバーパターン

### 概要
MCP (Model Context Protocol) を使用して Atlassian のリモートサーバーに接続し、OAuth2 認証でユーザーの代理として Jira にアクセスするパターン。エンタープライズ環境に最適。

### 実装仕様

#### 必要な設定
```python
# OAuth2 アプリケーションの設定
OAUTH_CLIENT_ID = os.getenv("ATLASSIAN_OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("ATLASSIAN_OAUTH_CLIENT_SECRET")
OAUTH_REDIRECT_URI = "http://localhost:8080/callback"
```

#### エージェント実装
```python
import os
import json
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, HttpServerParameters
from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows

# OAuth2 設定
OAUTH_CLIENT_ID = os.getenv("ATLASSIAN_OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("ATLASSIAN_OAUTH_CLIENT_SECRET")

# OAuth2 スキーム定義
oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://auth.atlassian.com/authorize",
            tokenUrl="https://auth.atlassian.com/oauth/token",
            scopes={
                "read:jira-user": "View user information",
                "read:jira-work": "View Jira issues and projects",
                "write:jira-work": "Create and update Jira issues",
                "offline_access": "Maintain access when offline"
            }
        )
    )
)

# 認証クレデンシャル
auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET
    )
)

# MCP 接続設定
mcp_connection = HttpServerParameters(
    url="https://mcp.atlassian.com/jira",  # 仮想的なMCPエンドポイント
    auth_config=AuthConfig(
        auth_scheme=oauth2_scheme,
        raw_auth_credential=auth_credential
    )
)

# MCPツールセット
jira_mcp_toolset = MCPToolset(
    connection_params=mcp_connection,
    tool_filter=[
        "search_issues",
        "get_issue",
        "create_issue",
        "update_issue",
        "add_comment",
        "get_projects",
        "get_issue_types"
    ]
)

# OAuth2 認証フローを処理するカスタムツール
def handle_oauth_authentication(tool_context: ToolContext) -> str:
    """OAuth2 認証フローを処理"""
    
    # 既存のトークンをチェック
    if "jira_oauth_tokens" in tool_context.state:
        tokens = tool_context.state["jira_oauth_tokens"]
        # トークンの有効性を確認
        if tokens.get("access_token"):
            return "Already authenticated"
    
    # 新規認証フロー
    auth_response = tool_context.get_auth_response(
        AuthConfig(
            auth_scheme=oauth2_scheme,
            raw_auth_credential=auth_credential
        )
    )
    
    if auth_response:
        # トークンを保存
        tool_context.state["jira_oauth_tokens"] = {
            "access_token": auth_response.oauth2.access_token,
            "refresh_token": auth_response.oauth2.refresh_token,
            "expires_at": auth_response.oauth2.expires_at
        }
        return "Authentication successful"
    else:
        # 認証をリクエスト
        tool_context.request_credential(
            AuthConfig(
                auth_scheme=oauth2_scheme,
                raw_auth_credential=auth_credential
            )
        )
        return "Authentication required. Please authorize access to Jira."

# エージェント定義
jira_oauth_mcp_agent = Agent(
    name="jira_oauth_mcp_agent",
    model="gemini-2.0-flash",
    instruction="""あなたは OAuth2 認証を使用する高度な Jira アシスタントです。
    
    初回使用時は認証が必要です。以下の機能を提供します：
    - プロジェクトとイシューの検索
    - イシューの作成と更新
    - コメントの追加
    - プロジェクト情報の取得
    
    セキュアな認証により、組織全体の Jira データに安全にアクセスできます。
    """,
    tools=[handle_oauth_authentication] + jira_mcp_toolset.get_tools()
)
```

### OAuth2 セットアップ手順

#### 1. Atlassian Developer Console での設定
```bash
# 1. https://developer.atlassian.com/console/myapps/ にアクセス
# 2. "Create" → "OAuth 2.0 (3LO) integration" を選択
# 3. アプリ情報を入力

# 必要なスコープ:
- read:jira-user
- read:jira-work  
- write:jira-work
- offline_access

# コールバックURL:
http://localhost:8080/callback
```

#### 2. Docker での認証セットアップ
```bash
# OAuth セットアップウィザードの実行
docker run --rm -i \
  -p 8080:8080 \
  -v "${HOME}/.mcp-atlassian:/home/app/.mcp-atlassian" \
  ghcr.io/sooperset/mcp-atlassian:latest --oauth-setup -v
```

### 利点
- **エンタープライズグレード**: 組織のセキュリティポリシーに準拠
- **自動トークン更新**: リフレッシュトークンによる継続的アクセス
- **細かい権限制御**: スコープベースのアクセス制御
- **監査可能**: すべてのアクセスが追跡可能

### 制限事項
- セットアップが複雑
- 初期設定に時間がかかる
- OAuth2 の理解が必要

## パターン3: Google Cloud Application Integration パターン

### 概要
Google Cloud Platform の Application Integration と Integration Connectors を使用して Jira と統合するパターン。既存の `jira_agent` サンプルと同様のアプローチ。

### 実装仕様

```python
from google.adk import Agent
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

# Application Integration 設定
jira_integration_tool = ApplicationIntegrationToolset(
    project="your-gcp-project-id",
    location="us-central1",
    connection="jira-prod-connection",
    entity_operations={
        "Issues": ["GET", "LIST", "CREATE", "UPDATE"],
        "Projects": ["GET", "LIST"],
        "Comments": ["CREATE", "LIST"]
    },
    actions=[
        "get_issue_by_key",
        "search_issues_by_jql",
        "create_issue_with_details",
        "transition_issue_status"
    ],
    tool_name="jira_gcp_integration_tool",
    tool_instructions="""
    Google Cloud Application Integration を使用して Jira と連携します。
    セキュアで管理された接続により、エンタープライズレベルの統合を実現します。
    """
)

# エージェント定義
jira_gcp_agent = Agent(
    name="jira_gcp_integration_agent",
    model="gemini-2.0-flash",
    instruction="""あなたは Google Cloud 統合を使用する Jira アシスタントです。
    
    Application Integration により以下を提供します：
    - 高可用性とスケーラビリティ
    - 統合されたセキュリティとログ
    - エンタープライズレベルの信頼性
    
    すべての操作は Google Cloud のインフラストラクチャを通じて実行されます。
    """,
    tools=jira_integration_tool.get_tools()
)
```

### GCP セットアップ手順
1. Application Integration API を有効化
2. Integration Connectors で Jira 接続を作成
3. ExecuteConnection 統合を作成・公開
4. IAM 権限を設定

### 利点
- **Google Cloud 統合**: 既存の GCP インフラとの統合
- **管理されたセキュリティ**: Google による認証管理
- **スケーラビリティ**: 自動スケーリング対応
- **監視とログ**: Cloud Monitoring/Logging との統合

### 制限事項
- Google Cloud 環境が必要
- 追加のインフラコスト
- GCP の知識が必要

## パターン4: MCP STDIO ローカルサーバーパターン

### 概要
ローカルで MCP サーバーを起動し、STDIO (標準入出力) 経由で通信するパターン。開発環境での使用に適している。

### 実装仕様

```python
import os
import json
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Jira 認証情報
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# 認証ヘッダー
jira_headers = json.dumps({
    "Authorization": f"Basic {base64.b64encode(f'{JIRA_USERNAME}:{JIRA_API_TOKEN}'.encode()).decode()}",
    "Accept": "application/json",
    "Content-Type": "application/json"
})

# MCP STDIO 設定
stdio_params = StdioServerParameters(
    command="npx",
    args=["-y", "@atlassian/jira-mcp-server"],  # 仮想的なMCPサーバー
    env={
        "JIRA_URL": JIRA_URL,
        "JIRA_HEADERS": jira_headers
    }
)

# MCPツールセット
jira_stdio_toolset = MCPToolset(
    connection_params=stdio_params,
    tool_filter=[
        "search_issues",
        "get_issue", 
        "create_issue",
        "update_issue",
        "add_comment"
    ]
)

# エージェント定義
jira_stdio_agent = Agent(
    name="jira_stdio_mcp_agent",
    model="gemini-2.0-flash",
    instruction="""あなたはローカル MCP サーバーを使用する Jira アシスタントです。
    
    STDIO 経由での通信により：
    - 低レイテンシーな操作
    - ローカル環境での完全な制御
    - デバッグの容易さ
    
    を実現します。
    """,
    tools=jira_stdio_toolset.get_tools()
)
```

### カスタム MCP サーバー実装例
```javascript
// jira-mcp-server.js
const { MCPServer } = require('@modelcontextprotocol/server');
const axios = require('axios');

class JiraMCPServer extends MCPServer {
    constructor() {
        super();
        this.jiraUrl = process.env.JIRA_URL;
        this.headers = JSON.parse(process.env.JIRA_HEADERS);
    }

    async searchIssues({ jql, maxResults = 50 }) {
        const response = await axios.get(
            `${this.jiraUrl}/rest/api/3/search`,
            {
                headers: this.headers,
                params: { jql, maxResults }
            }
        );
        return response.data;
    }

    async getIssue({ issueKey }) {
        const response = await axios.get(
            `${this.jiraUrl}/rest/api/3/issue/${issueKey}`,
            { headers: this.headers }
        );
        return response.data;
    }

    // その他のメソッド実装...
}

// サーバー起動
const server = new JiraMCPServer();
server.start();
```

### 利点
- **ローカル制御**: 完全なカスタマイズが可能
- **デバッグ容易**: ローカルでのログ確認
- **低レイテンシー**: ネットワーク遅延なし
- **開発効率**: 迅速なイテレーション

### 制限事項
- Node.js 環境が必要
- ローカル実行のみ
- プロダクション環境には不適

## パターン5: 直接API統合パターン

### 概要
ADK のカスタムツールとして直接 Jira API を統合する最も柔軟なパターン。特殊な要件やカスタマイズが必要な場合に適している。

### 実装仕様

```python
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import httpx
from google.adk import Agent
from google.adk.tools import ToolContext

@dataclass
class JiraConfig:
    """Jira 接続設定"""
    url: str
    username: str
    api_token: str
    timeout: int = 30
    max_retries: int = 3

class JiraClient:
    """Jira API クライアント"""
    
    def __init__(self, config: JiraConfig):
        self.config = config
        self.session = httpx.AsyncClient(
            base_url=config.url,
            auth=(config.username, config.api_token),
            timeout=config.timeout
        )
    
    async def search_issues(self, jql: str, fields: List[str] = None, max_results: int = 50) -> Dict:
        """JQL で課題を検索"""
        params = {
            "jql": jql,
            "maxResults": max_results
        }
        if fields:
            params["fields"] = ",".join(fields)
        
        response = await self.session.get("/rest/api/3/search", params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_issue(self, issue_key: str, expand: List[str] = None) -> Dict:
        """課題の詳細を取得"""
        params = {}
        if expand:
            params["expand"] = ",".join(expand)
        
        response = await self.session.get(f"/rest/api/3/issue/{issue_key}", params=params)
        response.raise_for_status()
        return response.json()
    
    async def create_issue(self, fields: Dict[str, Any]) -> Dict:
        """新しい課題を作成"""
        response = await self.session.post("/rest/api/3/issue", json={"fields": fields})
        response.raise_for_status()
        return response.json()
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> None:
        """課題を更新"""
        response = await self.session.put(f"/rest/api/3/issue/{issue_key}", json={"fields": fields})
        response.raise_for_status()
    
    async def add_comment(self, issue_key: str, body: str) -> Dict:
        """課題にコメントを追加"""
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": body}]
                    }
                ]
            }
        }
        response = await self.session.post(f"/rest/api/3/issue/{issue_key}/comment", json=comment_data)
        response.raise_for_status()
        return response.json()
    
    async def get_transitions(self, issue_key: str) -> List[Dict]:
        """利用可能な遷移を取得"""
        response = await self.session.get(f"/rest/api/3/issue/{issue_key}/transitions")
        response.raise_for_status()
        return response.json()["transitions"]
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> None:
        """課題のステータスを遷移"""
        response = await self.session.post(
            f"/rest/api/3/issue/{issue_key}/transitions",
            json={"transition": {"id": transition_id}}
        )
        response.raise_for_status()
    
    async def close(self):
        """セッションをクローズ"""
        await self.session.aclose()

# グローバルクライアントインスタンス
jira_config = JiraConfig(
    url=os.getenv("JIRA_URL"),
    username=os.getenv("JIRA_USERNAME"),
    api_token=os.getenv("JIRA_API_TOKEN")
)
jira_client = JiraClient(jira_config)

# カスタムツール実装
def advanced_jira_search(
    query: str,
    project: Optional[str] = None,
    status: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    created_after: Optional[str] = None,
    updated_after: Optional[str] = None,
    order_by: str = "created DESC",
    limit: int = 50,
    tool_context: ToolContext = None
) -> Dict:
    """高度な Jira 検索機能"""
    
    # JQL クエリの構築
    jql_parts = []
    
    if query:
        jql_parts.append(f'text ~ "{query}"')
    
    if project:
        jql_parts.append(f'project = {project}')
    
    if status:
        status_query = " OR ".join([f'status = "{s}"' for s in status])
        jql_parts.append(f"({status_query})")
    
    if assignee:
        if assignee == "currentUser()":
            jql_parts.append("assignee = currentUser()")
        else:
            jql_parts.append(f'assignee = "{assignee}"')
    
    if created_after:
        jql_parts.append(f'created >= "{created_after}"')
    
    if updated_after:
        jql_parts.append(f'updated >= "{updated_after}"')
    
    jql = " AND ".join(jql_parts) if jql_parts else "ORDER BY created DESC"
    jql += f" ORDER BY {order_by}"
    
    import asyncio
    result = asyncio.run(jira_client.search_issues(jql, max_results=limit))
    
    # 結果の整形
    issues = []
    for issue in result.get("issues", []):
        fields = issue["fields"]
        issues.append({
            "key": issue["key"],
            "summary": fields["summary"],
            "status": fields["status"]["name"],
            "priority": fields.get("priority", {}).get("name", "None"),
            "assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
            "reporter": fields["reporter"]["displayName"],
            "created": fields["created"],
            "updated": fields["updated"],
            "description": fields.get("description", ""),
            "labels": fields.get("labels", []),
            "components": [c["name"] for c in fields.get("components", [])]
        })
    
    return {
        "total": result["total"],
        "issues": issues,
        "query": jql
    }

def create_jira_workflow(
    workflow_type: str,
    details: Dict[str, Any],
    tool_context: ToolContext = None
) -> Dict:
    """定義済みワークフローで Jira 課題を作成"""
    
    workflows = {
        "bug": {
            "issuetype": {"name": "Bug"},
            "priority": {"name": "High"},
            "labels": ["bug", "needs-triage"]
        },
        "feature": {
            "issuetype": {"name": "Story"},
            "priority": {"name": "Medium"},
            "labels": ["feature", "enhancement"]
        },
        "task": {
            "issuetype": {"name": "Task"},
            "priority": {"name": "Medium"},
            "labels": ["task"]
        }
    }
    
    if workflow_type not in workflows:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    # ワークフローのデフォルト値を適用
    fields = workflows[workflow_type].copy()
    fields.update({
        "project": {"key": details["project_key"]},
        "summary": details["summary"],
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": details["description"]}]
                }
            ]
        }
    })
    
    # オプションフィールド
    if "assignee" in details:
        fields["assignee"] = {"accountId": details["assignee"]}
    
    if "components" in details:
        fields["components"] = [{"name": c} for c in details["components"]]
    
    import asyncio
    result = asyncio.run(jira_client.create_issue(fields))
    
    return {
        "key": result["key"],
        "id": result["id"],
        "url": f"{jira_config.url}/browse/{result['key']}",
        "workflow": workflow_type
    }

def manage_issue_lifecycle(
    issue_key: str,
    action: str,
    comment: Optional[str] = None,
    tool_context: ToolContext = None
) -> Dict:
    """課題のライフサイクル管理"""
    
    async def _manage():
        # 現在の課題情報を取得
        issue = await jira_client.get_issue(issue_key)
        current_status = issue["fields"]["status"]["name"]
        
        # 利用可能な遷移を取得
        transitions = await jira_client.get_transitions(issue_key)
        
        # アクションに基づいて遷移を選択
        transition_map = {
            "start": ["In Progress", "開始", "Start Progress"],
            "resolve": ["Resolved", "解決済み", "Resolve"],
            "close": ["Closed", "完了", "Close"],
            "reopen": ["Reopened", "再オープン", "Reopen"]
        }
        
        target_transitions = transition_map.get(action, [])
        selected_transition = None
        
        for transition in transitions:
            if transition["name"] in target_transitions:
                selected_transition = transition
                break
        
        if not selected_transition:
            return {
                "status": "error",
                "message": f"No valid transition found for action '{action}' from status '{current_status}'"
            }
        
        # 遷移を実行
        await jira_client.transition_issue(issue_key, selected_transition["id"])
        
        # コメントを追加
        if comment:
            await jira_client.add_comment(issue_key, comment)
        
        return {
            "status": "success",
            "issue_key": issue_key,
            "previous_status": current_status,
            "new_status": selected_transition["to"]["name"],
            "action": action
        }
    
    import asyncio
    return asyncio.run(_manage())

# エージェント定義
jira_advanced_agent = Agent(
    name="jira_advanced_agent",
    model="gemini-2.0-flash",
    instruction="""あなたは高度な Jira 統合機能を持つプロジェクト管理アシスタントです。
    
    以下の高度な機能を提供します：
    1. 複雑な検索クエリの構築と実行
    2. ワークフロー定義に基づく課題作成
    3. 課題のライフサイクル管理
    
    すべての操作は最適化されたAPIクライアントを通じて実行され、
    エラーハンドリングとリトライ機能により高い信頼性を保証します。
    """,
    tools=[advanced_jira_search, create_jira_workflow, manage_issue_lifecycle]
)
```

### 利点
- **完全な柔軟性**: あらゆるカスタマイズが可能
- **パフォーマンス最適化**: 直接的なAPI呼び出し
- **詳細なエラー制御**: カスタムエラーハンドリング
- **特殊要件対応**: 独自のビジネスロジック実装

### 制限事項
- 実装の複雑さ
- メンテナンスコスト
- API変更への対応が必要

## パターン選択ガイド

### 意思決定フローチャート

```
スタート
    ↓
個人/プロトタイプ? → Yes → パターン1 (API Key)
    ↓ No
エンタープライズ環境?
    ↓ Yes
    Google Cloud 使用? → Yes → パターン3 (GCP)
    ↓ No              ↓ No
    OAuth2 必要? → Yes → パターン2 (OAuth2 MCP)
    ↓ No
ローカル開発のみ? → Yes → パターン4 (MCP STDIO)
    ↓ No
パターン5 (直接API)
```

### 詳細な比較マトリックス

| 評価項目 | パターン1 | パターン2 | パターン3 | パターン4 | パターン5 |
|---------|-----------|-----------|-----------|-----------|-----------|
| **実装速度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **セキュリティ** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **スケーラビリティ** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **メンテナンス** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **カスタマイズ性** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **コスト** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## セキュリティ考慮事項

### 共通のセキュリティ対策

#### 1. 認証情報の管理
```python
# 環境変数での管理（推奨）
import os
from cryptography.fernet import Fernet

class SecureCredentialManager:
    def __init__(self, encryption_key: str = None):
        self.key = encryption_key or os.getenv("ENCRYPTION_KEY")
        self.cipher = Fernet(self.key.encode()) if self.key else None
    
    def encrypt_credential(self, credential: str) -> str:
        """認証情報を暗号化"""
        if not self.cipher:
            raise ValueError("Encryption key not set")
        return self.cipher.encrypt(credential.encode()).decode()
    
    def decrypt_credential(self, encrypted: str) -> str:
        """認証情報を復号化"""
        if not self.cipher:
            raise ValueError("Encryption key not set")
        return self.cipher.decrypt(encrypted.encode()).decode()
```

#### 2. アクセス制御
```python
class JiraAccessController:
    def __init__(self, allowed_operations: List[str]):
        self.allowed_operations = allowed_operations
    
    def validate_operation(self, operation: str) -> bool:
        """操作の妥当性を検証"""
        return operation in self.allowed_operations
    
    def create_readonly_agent(self) -> Agent:
        """読み取り専用エージェントの作成"""
        return Agent(
            name="jira_readonly_agent",
            tools=[search_jira_issues, get_jira_issue],  # 読み取りツールのみ
            instruction="読み取り専用モードで動作します。"
        )
```

#### 3. 監査ログ
```python
import logging
from datetime import datetime

class JiraAuditLogger:
    def __init__(self, log_file: str = "jira_audit.log"):
        self.logger = logging.getLogger("jira_audit")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_operation(self, user: str, operation: str, details: Dict):
        """操作を監査ログに記録"""
        self.logger.info(f"User: {user}, Operation: {operation}, Details: {json.dumps(details)}")
```

### パターン別セキュリティ推奨事項

#### パターン1 (API Key)
- API Token を環境変数で管理
- Token のローテーション計画
- IP 制限の設定（可能な場合）

#### パターン2 (OAuth2)
- リフレッシュトークンの安全な保存
- スコープの最小化
- トークンの定期的な検証

#### パターン3 (GCP)
- IAM ロールの最小権限原則
- VPC Service Controls の活用
- 監査ログの有効化

#### パターン4 (MCP STDIO)
- ローカル実行環境の保護
- プロセス間通信の暗号化
- ファイルシステム権限の適切な設定

#### パターン5 (直接API)
- カスタム認証ミドルウェア
- レート制限の実装
- 入力検証の徹底

## 実装のベストプラクティス

### 1. エラーハンドリング

```python
from typing import Union, Optional
import time

class JiraErrorHandler:
    @staticmethod
    def with_retry(func):
        """リトライ機能付きデコレータ"""
        async def wrapper(*args, **kwargs):
            max_retries = 3
            delay = 1
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:  # Rate limit
                        wait_time = int(e.response.headers.get("Retry-After", delay))
                        print(f"Rate limited. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    elif e.response.status_code >= 500:  # Server error
                        if attempt < max_retries - 1:
                            time.sleep(delay * (2 ** attempt))
                            continue
                    raise e
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        continue
                    raise e
            
        return wrapper
```

### 2. パフォーマンス最適化

```python
from functools import lru_cache
import asyncio

class JiraPerformanceOptimizer:
    def __init__(self, cache_size: int = 128):
        self.cache_size = cache_size
    
    @lru_cache(maxsize=128)
    def cache_project_info(self, project_key: str) -> Dict:
        """プロジェクト情報をキャッシュ"""
        # API 呼び出しの結果をキャッシュ
        pass
    
    async def batch_operations(self, operations: List[Dict]) -> List[Any]:
        """複数の操作をバッチ処理"""
        tasks = []
        for op in operations:
            if op["type"] == "search":
                tasks.append(self.search_issues_async(op["params"]))
            elif op["type"] == "update":
                tasks.append(self.update_issue_async(op["params"]))
        
        return await asyncio.gather(*tasks)
```

### 3. テストとモック

```python
import pytest
from unittest.mock import Mock, patch

class MockJiraClient:
    """テスト用モッククライアント"""
    
    def __init__(self):
        self.issues = {
            "TEST-1": {
                "key": "TEST-1",
                "fields": {
                    "summary": "Test Issue",
                    "status": {"name": "Open"},
                    "assignee": {"displayName": "Test User"}
                }
            }
        }
    
    async def search_issues(self, jql: str, **kwargs) -> Dict:
        return {
            "total": 1,
            "issues": list(self.issues.values())
        }
    
    async def get_issue(self, issue_key: str) -> Dict:
        if issue_key in self.issues:
            return self.issues[issue_key]
        raise httpx.HTTPStatusError("Not found", request=None, response=None)

@pytest.fixture
def mock_jira_client():
    """テスト用フィクスチャ"""
    return MockJiraClient()

def test_search_issues(mock_jira_client):
    """検索機能のテスト"""
    result = asyncio.run(
        mock_jira_client.search_issues("project = TEST")
    )
    assert result["total"] == 1
    assert result["issues"][0]["key"] == "TEST-1"
```

### 4. ドキュメント化

```python
class JiraAgentDocumentation:
    """エージェントのドキュメント生成"""
    
    @staticmethod
    def generate_tool_docs(tools: List[callable]) -> str:
        """ツールのドキュメントを自動生成"""
        docs = []
        for tool in tools:
            doc = f"### {tool.__name__}\n"
            doc += f"{tool.__doc__}\n"
            doc += f"Parameters:\n"
            # 関数シグネチャから パラメータを抽出
            import inspect
            sig = inspect.signature(tool)
            for param_name, param in sig.parameters.items():
                if param_name != "tool_context":
                    doc += f"- {param_name}: {param.annotation.__name__ if param.annotation else 'Any'}\n"
            docs.append(doc)
        
        return "\n".join(docs)
```

## まとめ

本仕様書では、ADK を使用した Jira 接続エージェントの5つの実装パターンを詳細に解説しました。各パターンには独自の利点と制限があり、プロジェクトの要件に応じて適切なパターンを選択することが重要です。

### 推奨事項
1. **開発開始時**: パターン1（API Key）でプロトタイプ作成
2. **本番移行時**: セキュリティ要件に応じてパターン2または3へ移行
3. **特殊要件**: パターン5でカスタマイズ

### 次のステップ
1. 選択したパターンの実装
2. セキュリティ対策の実施
3. パフォーマンステストの実行
4. 本番環境へのデプロイ

この仕様書が、効果的な Jira 統合エージェントの実装に役立つことを願っています。