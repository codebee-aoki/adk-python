# MCP SSE 統合エージェント - 技術ドキュメント

## 概要

MCP SSE 統合エージェント（`mcp_sse_agent`）は、Model Context Protocol（MCP）の Server-Sent Events（SSE）接続を通じてファイルシステム操作を行うエージェントです。安全な読み取り専用ファイルアクセス、ディレクトリツリー探索、ファイル検索など、MCP プロトコルを使用した外部ツールとの統合パターンを実演します。

## 技術仕様

### アーキテクチャ

```python
# MCP SSE 統合エージェント
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='enterprise_assistant', 
    instruction=f"Help user accessing their file systems. Allowed directory: {_allowed_path}",
    tools=[
        MCPToolset(
            connection_params=SseConnectionParams(
                url='http://localhost:3000/sse',           # SSE エンドポイント
                headers={'Accept': 'text/event-stream'},   # SSE ヘッダー
            ),
            tool_filter=[...],  # 許可ツールのフィルタリング
        )
    ],
)
```

### 主要コンポーネント

#### 1. SSE 接続パラメータ
```python
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

connection_params = SseConnectionParams(
    url='http://localhost:3000/sse',              # MCP サーバーの SSE エンドポイント
    headers={'Accept': 'text/event-stream'},      # SSE 必須ヘッダー
)
```

#### 2. MCP ツールセット
```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

toolset = MCPToolset(
    connection_params=connection_params,
    tool_filter=[...],  # セキュリティフィルタ
)
```

#### 3. 許可ディレクトリ制限
```python
import os

_allowed_path = os.path.dirname(os.path.abspath(__file__))
# エージェントのディレクトリのみアクセス許可
```

## セキュリティ設計

### 1. 読み取り専用アクセス

**許可されたツール**:
```python
tool_filter=[
    'read_file',                # ファイル読み取り
    'read_multiple_files',      # 複数ファイル読み取り
    'list_directory',           # ディレクトリ一覧
    'directory_tree',           # ディレクトリツリー
    'search_files',             # ファイル検索
    'get_file_info',            # ファイル情報取得
    'list_allowed_directories', # 許可ディレクトリ一覧
]
```

**禁止されたツール（コメントアウト例）**:
```python
# tool_filter=lambda tool, ctx=None: tool.name not in [
#     'write_file',        # ファイル書き込み（禁止）
#     'edit_file',         # ファイル編集（禁止）
#     'create_directory',  # ディレクトリ作成（禁止）
#     'move_file',         # ファイル移動（禁止）
# ],
```

### 2. ディレクトリアクセス制限

**アクセス制御**:
```python
# エージェント実行ディレクトリのみ許可
_allowed_path = os.path.dirname(os.path.abspath(__file__))

instruction = f"""
Help user accessing their file systems.

Allowed directory: {_allowed_path}
"""
```

## MCP SSE 通信フロー

### 1. 接続確立

**SSE 接続開始**:
```text
Client (ADK Agent) → MCP Server
GET http://localhost:3000/sse
Accept: text/event-stream

MCP Server → Client
Content-Type: text/event-stream
Cache-Control: no-cache

data: {"type": "connection_established"}
```

### 2. ツール実行リクエスト

**ファイル読み取りリクエスト**:
```text
Client → MCP Server (SSE)
data: {
  "type": "tool_call",
  "tool": "read_file", 
  "args": {"file_path": "/allowed/path/example.txt"}
}

MCP Server → Client (SSE)
data: {
  "type": "tool_response",
  "result": "ファイルの内容..."
}
```

### 3. ディレクトリ探索

**ディレクトリツリー取得**:
```text
Client → MCP Server
data: {
  "type": "tool_call",
  "tool": "directory_tree",
  "args": {"path": "/allowed/path"}
}

MCP Server → Client  
data: {
  "type": "tool_response",
  "result": {
    "tree": "📁 allowed/\n├── 📄 file1.txt\n└── 📁 subfolder/"
  }
}
```

## 実行例

### 基本的なファイル操作

**ファイル内容の読み取り**:
```python
response = await root_agent.invoke("agent.py ファイルの内容を教えてください")

# 実行フロー:
# 1. read_file ツール呼び出し
# 2. MCP サーバーにSSE経由でリクエスト
# 3. ファイル内容を取得
# 4. 内容要約を応答
```

**ディレクトリ構造の確認**:
```python
response = await root_agent.invoke("このディレクトリの構造を教えてください")

# 実行フロー:
# 1. directory_tree ツール呼び出し
# 2. 許可ディレクトリのツリー構造取得
# 3. 視覚的なツリー表示で応答
```

### 高度なファイル操作

**複数ファイルの一括読み取り**:
```python
query = "agent.py と README.md の両方の内容を比較してください"
response = await root_agent.invoke(query)

# 実行フロー:
# 1. read_multiple_files ツール呼び出し
# 2. 複数ファイルを並列取得
# 3. 内容比較と分析
# 4. 比較結果の報告
```

**ファイル検索**:
```python
response = await root_agent.invoke("Python ファイルを検索してください")

# 実行フロー:
# 1. search_files ツール呼び出し（*.py パターン）
# 2. 許可ディレクトリ内を再帰検索
# 3. 見つかったファイル一覧を返却
```

## 高度な実装例

### 1. ファイル分析エージェント

```python
class FileAnalyzer:
    def __init__(self, mcp_agent):
        self.agent = mcp_agent
    
    async def analyze_codebase(self):
        """コードベース分析"""
        # Python ファイル検索
        python_files = await self.agent.invoke("search_files", pattern="*.py")
        
        analysis = {}
        for file_path in python_files:
            # ファイル情報取得
            file_info = await self.agent.invoke("get_file_info", path=file_path)
            
            # ファイル内容読み取り
            content = await self.agent.invoke("read_file", path=file_path)
            
            analysis[file_path] = {
                'size': file_info['size'],
                'lines': len(content.split('\n')),
                'functions': self.count_functions(content),
                'classes': self.count_classes(content),
            }
        
        return analysis
```

### 2. ドキュメント生成エージェント

```python
class DocumentationGenerator:
    async def generate_project_docs(self, project_path):
        """プロジェクトドキュメント生成"""
        # プロジェクト構造取得
        tree = await self.get_directory_tree(project_path)
        
        # README ファイル確認
        readme_files = await self.search_readme_files(project_path)
        
        # ソースコード分析
        source_analysis = await self.analyze_source_files(project_path)
        
        # 包括的ドキュメント生成
        return self.compile_documentation(tree, readme_files, source_analysis)
```

### 3. セキュリティ監査エージェント

```python
class SecurityAuditor:
    async def audit_file_permissions(self):
        """ファイル権限監査"""
        # 許可ディレクトリ一覧取得
        allowed_dirs = await self.agent.invoke("list_allowed_directories")
        
        security_report = {}
        for directory in allowed_dirs:
            # ディレクトリ内ファイル一覧
            files = await self.agent.invoke("list_directory", path=directory)
            
            for file_path in files:
                # ファイル情報とセキュリティチェック
                file_info = await self.agent.invoke("get_file_info", path=file_path)
                security_issues = self.check_security_issues(file_info)
                
                if security_issues:
                    security_report[file_path] = security_issues
        
        return security_report
```

## MCP サーバー設定

### 1. ローカル MCP サーバーの起動

**基本設定**:
```bash
# MCP ファイルシステムサーバー起動
mcp-server-filesystem --port 3000 --sse-endpoint /sse
```

**Docker での起動**:
```dockerfile
FROM node:18
RUN npm install -g @modelcontextprotocol/server-filesystem
EXPOSE 3000
CMD ["mcp-server-filesystem", "--port", "3000", "--sse-endpoint", "/sse"]
```

### 2. カスタム MCP サーバー

**Python での実装例**:
```python
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio

app = FastAPI()

@app.get("/sse")
async def sse_endpoint(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            
            # MCP メッセージの処理
            message = await process_mcp_request()
            yield f"data: {json.dumps(message)}\n\n"
            
            await asyncio.sleep(0.1)
    
    return EventSourceResponse(event_generator())
```

## エラーハンドリング

### 1. 接続エラー

```python
try:
    response = await mcp_agent.invoke("read_file", path="example.txt")
except MCPConnectionError as e:
    print(f"MCP 接続エラー: {e}")
    # フォールバック処理
except MCPTimeoutError as e:
    print(f"MCP タイムアウト: {e}")
    # リトライ処理
```

### 2. 権限エラー

```python
try:
    response = await mcp_agent.invoke("read_file", path="/forbidden/path")
except MCPPermissionError as e:
    print(f"アクセス権限なし: {e}")
    # 許可ディレクトリの案内
```

### 3. ファイル不存在エラー

```python
try:
    response = await mcp_agent.invoke("read_file", path="nonexistent.txt")
except MCPFileNotFoundError as e:
    print(f"ファイルが見つかりません: {e}")
    # ファイル検索の提案
```

## パフォーマンス最適化

### 1. 接続プーリング

```python
class MCPConnectionPool:
    def __init__(self, max_connections=10):
        self.pool = asyncio.Queue(maxsize=max_connections)
    
    async def get_connection(self):
        return await self.pool.get()
    
    async def return_connection(self, connection):
        await self.pool.put(connection)
```

### 2. キャッシュ機能

```python
from functools import lru_cache
import time

class MCPCache:
    def __init__(self, ttl=300):  # 5分間キャッシュ
        self.cache = {}
        self.ttl = ttl
    
    async def get_cached_result(self, operation, args):
        key = f"{operation}:{hash(str(args))}"
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
        
        # キャッシュミス: 実際の操作実行
        result = await self.execute_mcp_operation(operation, args)
        self.cache[key] = (result, time.time())
        return result
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `filesystem_server.py`: MCP ファイルシステムサーバー実装
- `README.md`: 英語版ドキュメント
- `README_ja.md`: 日本語版ドキュメント

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.tools.mcp_tool`: MCP ツール統合
- `google.adk.tools.mcp_tool.mcp_session_manager`: セッション管理
- `google.adk.tools.mcp_tool.mcp_toolset`: ツールセット
- **MCP サーバー**: ファイルシステム操作用の外部サーバー
- **SSE ライブラリ**: Server-Sent Events 通信