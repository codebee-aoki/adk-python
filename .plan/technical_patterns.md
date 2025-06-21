# ADK 技術パターン ガイド

このドキュメントは、ADK サンプルエージェント全体で使用されている技術パターンを体系化したリファレンスです。

## 1. エージェント アーキテクチャ パターン

### 1.1 単一エージェント パターン
```python
# 基本的な単一エージェント
root_agent = Agent(
    model='gemini-2.0-flash',
    name='agent_name',
    description='Agent description',
    instruction='Detailed instructions...',
    tools=[tool1, tool2],
)
```

**特徴:**
- 単一の責任を持つ
- シンプルな構造
- 初心者に理解しやすい

**使用例:** hello_world, bigquery, google_search_agent

### 1.2 マルチエージェント パターン
```python
# 複数のサブエージェントを持つエージェント
coordinator_agent = Agent(
    name='coordinator',
    sub_agents=[agent1, agent2, agent3],
    # 自動的なエージェント転送処理
)
```

**特徴:**
- 複数の専門エージェントを統合
- 複雑なワークフローを分割
- エージェント間の転送を自動処理

**使用例:** hello_world_ma, adk_triaging_agent

### 1.3 逐次エージェント パターン
```python
# 順番に実行されるエージェント
sequential_agent = SequentialAgent(
    name='pipeline_agent',
    sub_agents=[step1_agent, step2_agent, step3_agent],
    # 前のエージェントの出力が次の入力になる
)
```

**特徴:**
- ステップバイステップ処理
- 各ステップが専門化
- 状態が次のステップに引き継がれる

**使用例:** workflow_agent_seq, simple_sequential_agent

## 2. ツール統合パターン

### 2.1 カスタム Python 関数ツール
```python
def custom_tool(param: str, tool_context: ToolContext) -> str:
    """カスタムツールの実装"""
    # ビジネスロジック
    result = process_data(param)
    
    # 状態の更新
    tool_context.state['key'] = value
    
    return result

# エージェントでの使用
root_agent = Agent(
    tools=[custom_tool],
    # ...
)
```

**特徴:**
- 完全なカスタマイズ可能
- ツールコンテキストで状態管理
- 同期・非同期両方サポート

**使用例:** hello_world (roll_die, check_prime), callbacks

### 2.2 Google サービス統合パターン
```python
# BigQuery 統合例
from google.adk.tools.bigquery import BigQueryToolset

# 認証設定
credentials_config = BigQueryCredentialsConfig(
    client_id=os.getenv("OAUTH_CLIENT_ID"),
    client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
)

# ツールセット作成
bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config,
    bigquery_tool_config=tool_config
)

root_agent = Agent(
    tools=[bigquery_toolset],
    # ...
)
```

**特徴:**
- Google Cloud サービスとの統合
- 複数の認証方法サポート
- 設定ベースの柔軟性

**使用例:** bigquery, oauth_calendar_agent

### 2.3 MCP (Model Context Protocol) パターン
```python
# MCP SSE 統合例
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

root_agent = LlmAgent(
    tools=[
        MCPToolset(
            connection_params=SseConnectionParams(
                url='http://localhost:3000/sse',
                headers={'Accept': 'text/event-stream'},
            ),
            tool_filter=['allowed_tool1', 'allowed_tool2'],
        )
    ],
)
```

**特徴:**
- 外部 MCP サーバーとの通信
- 複数の接続タイプ (SSE, STDIO, HTTP)
- ツールフィルタリング機能

**使用例:** mcp_sse_agent, mcp_stdio_notion_agent

### 2.4 Application Integration パターン
```python
# JIRA 統合例
from google.adk.tools.application_integration_tool import ApplicationIntegrationToolset

jira_tool = ApplicationIntegrationToolset(
    project="your-gcp-project-id",
    location="your-regions",
    connection="your-integration-connection-name",
    entity_operations={"Issues": ["GET", "LIST"]},
    actions=["get_issue_by_key"],
)
```

**特徴:**
- Google Cloud Application Integration 経由
- エンタープライズシステム統合
- 宣言的な操作定義

**使用例:** jira_agent, integration_connector_euc_agent

## 3. 認証パターン

### 3.1 OAuth2 認証
```python
CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2

credentials_config = ServiceCredentialsConfig(
    client_id=os.getenv("OAUTH_CLIENT_ID"),
    client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
)
```

### 3.2 Service Account 認証
```python
CREDENTIALS_TYPE = AuthCredentialTypes.SERVICE_ACCOUNT

creds, _ = google.auth.load_credentials_from_file("service_account_key.json")
credentials_config = ServiceCredentialsConfig(credentials=creds)
```

### 3.3 Application Default Credentials
```python
application_default_credentials, _ = google.auth.default()
credentials_config = ServiceCredentialsConfig(
    credentials=application_default_credentials
)
```

## 4. 状態管理パターン

### 4.1 ツールコンテキスト状態
```python
def tool_with_state(param: str, tool_context: ToolContext) -> str:
    # 状態の読み取り
    if 'counter' not in tool_context.state:
        tool_context.state['counter'] = 0
    
    # 状態の更新
    tool_context.state['counter'] += 1
    
    return f"Called {tool_context.state['counter']} times"
```

### 4.2 セッション状態永続化
```python
# before_agent_callback での状態設定
async def before_agent_callback(callback_context):
    callback_context.state['session_key'] = 'session_value'
    return None
```

### 4.3 エージェント間状態共有
```python
# SequentialAgent での状態引き継ぎ
code_writer_agent = LlmAgent(
    output_key="generated_code",  # 状態に保存
)

code_reviewer_agent = LlmAgent(
    instruction="Review this code: {generated_code}",  # 状態から読み取り
)
```

## 5. コールバックパターン

### 5.1 基本コールバック
```python
async def before_agent_callback(callback_context):
    print("エージェント実行前")
    return None

async def after_agent_callback(callback_context):
    print("エージェント実行後")
    return None

root_agent = Agent(
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)
```

### 5.2 複数コールバック
```python
root_agent = Agent(
    before_agent_callback=[callback1, callback2, callback3],
    after_agent_callback=[callback1, callback2, callback3],
    before_tool_callback=[tool_cb1, tool_cb2],
    after_tool_callback=[tool_cb1, tool_cb2],
)
```

## 6. 設定パターン

### 6.1 環境変数ベース
```python
# .env または環境変数
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret

# コードでの使用
client_id = os.getenv("OAUTH_CLIENT_ID")
```

### 6.2 設定ファイルベース (YAML)
```yaml
# tools.yaml
sources:
  my-sqlite-db:
    kind: "sqlite"
    database: "tool_box.db"

tools:
  search-data:
    kind: sqlite-sql
    source: my-sqlite-db
    statement: SELECT * FROM table WHERE name = $1;
```

### 6.3 設定ファイルベース (JSON)
```json
{
  "state": {},
  "queries": ["hello world!"]
}
```

## 7. ストリーミングパターン

### 7.1 双方向ストリーミング
```python
# Live bidirectional streaming
root_agent = LlmAgent(
    # ストリーミング設定
    streaming_config=StreamingConfig(
        enable_live_streaming=True,
        bidirectional=True,
    ),
)
```

## 8. エラーハンドリングパターン

### 8.1 Safety Settings
```python
root_agent = Agent(
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
```

### 8.2 Try-Catch パターン
```python
def robust_tool(param: str) -> str:
    try:
        # メイン処理
        result = external_api_call(param)
        return result
    except Exception as e:
        # エラーハンドリング
        return f"Error occurred: {str(e)}"
```

## 9. プランナーパターン

### 9.1 Built-in Planner
```python
root_agent = Agent(
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
        ),
    ),
)
```

### 9.2 ReAct Planner
```python
root_agent = Agent(
    planner=PlanReActPlanner(),
)
```

これらのパターンを理解することで、各エージェントの実装を迅速に把握し、新しいエージェント開発に活用できます。