# MCP StreamableHTTP エージェント - 技術ドキュメント

## 概要

MCP StreamableHTTP エージェント（`mcp_streamablehttp_agent`）は、Model Context Protocol（MCP）の StreamableHTTP 接続を通じてファイルシステム操作を行うエージェントです。HTTP ベースの MCP サーバーとの通信により、安全な読み取り専用ファイルアクセス機能を提供し、ネットワーク経由での MCP プロトコル利用パターンを実演します。

## 技術仕様

### アーキテクチャ

```python
# MCP StreamableHTTP エージェント
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='enterprise_assistant',
    instruction=f"Help user accessing their file systems. Allowed directory: {_allowed_path}",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPServerParams(
                url='http://localhost:3000/mcp',  # HTTP MCP エンドポイント
            ),
            tool_filter=[...],  # セキュリティフィルタ
        )
    ],
)
```

### 主要コンポーネント

#### 1. StreamableHTTP 接続パラメータ
```python
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

connection_params = StreamableHTTPServerParams(
    url='http://localhost:3000/mcp',  # MCP サーバーの HTTP エンドポイント
)
```

#### 2. 許可ディレクトリ制限
```python
import os

_allowed_path = os.path.dirname(os.path.abspath(__file__))
# エージェント実行ディレクトリのみアクセス許可
```

#### 3. 読み取り専用セキュリティフィルタ
```python
tool_filter = [
    'read_file',                # ファイル読み取り
    'read_multiple_files',      # 複数ファイル読み取り
    'list_directory',           # ディレクトリ一覧
    'directory_tree',           # ディレクトリツリー
    'search_files',             # ファイル検索
    'get_file_info',            # ファイル情報取得
    'list_allowed_directories', # 許可ディレクトリ一覧
]

# 危険な操作は除外（コメントアウト例）
# tool_filter=lambda tool, ctx=None: tool.name not in [
#     'write_file',        # ファイル書き込み（禁止）
#     'edit_file',         # ファイル編集（禁止）
#     'create_directory',  # ディレクトリ作成（禁止）
#     'move_file',         # ファイル移動（禁止）
# ],
```

## HTTP MCP 通信フロー

### 1. HTTP 接続確立

**接続シーケンス**:
```text
ADK Agent
↓ HTTP Request
POST http://localhost:3000/mcp
Content-Type: application/json
↓
MCP HTTP Server
↓ HTTP Response  
200 OK
Content-Type: application/json
↓
双方向 HTTP ストリーム確立
```

### 2. ツール実行リクエスト

**ファイル読み取り HTTP リクエスト**:
```json
POST http://localhost:3000/mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "path": "agent.py"
    }
  },
  "id": "request-001"
}
```

**HTTP レスポンス**:
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "result": {
    "content": "# ファイルの内容...",
    "isText": true
  },
  "id": "request-001"
}
```

### 3. ストリーミング応答

**長時間実行操作のストリーミング**:
```text
HTTP Request: directory_tree (大きなディレクトリ)
↓
HTTP Response (chunked transfer encoding):
{"partial": true, "data": "📁 root/\n"}
{"partial": true, "data": "├── 📄 file1.py\n"}
{"partial": true, "data": "├── 📄 file2.py\n"}
{"partial": false, "data": "└── 📁 subfolder/\n"}
```

## 実行例

### 基本的なファイル操作

**ファイル内容の確認**:
```python
response = await root_agent.invoke("agent.py ファイルの内容を確認してください")

# HTTP 通信フロー:
# 1. POST /mcp → read_file ツール呼び出し
# 2. MCP サーバー: ファイル読み取り実行
# 3. HTTP レスポンス: ファイル内容返却
# 4. エージェント: 内容分析と応答生成
```

**ディレクトリ探索**:
```python
response = await root_agent.invoke("このディレクトリの構造を表示してください")

# HTTP 通信フロー:
# 1. POST /mcp → directory_tree ツール呼び出し
# 2. ストリーミング応答でツリー構造を段階的取得
# 3. 完全なディレクトリ構造の表示
```

### 高度なファイル操作

**複数ファイルの並列読み取り**:
```python
query = "Python ファイルをすべて検索し、それぞれの内容を要約してください"
response = await root_agent.invoke(query)

# HTTP 通信フロー:
# 1. POST /mcp → search_files (*.py)
# 2. 検索結果取得
# 3. 各ファイルに対して並列 HTTP リクエスト
# 4. read_multiple_files による一括読み取り
# 5. 統合分析レポート生成
```

**ファイル詳細情報の取得**:
```python
response = await root_agent.invoke("README.md のファイル情報（サイズ、更新日時）を確認してください")

# HTTP 通信フロー:
# 1. POST /mcp → get_file_info
# 2. ファイルメタデータ取得
# 3. 人間が読みやすい形式で情報表示
```

## 高度な実装例

### 1. 分散ファイル分析システム

```python
class DistributedFileAnalyzer:
    def __init__(self, mcp_agents: list):
        self.agents = mcp_agents  # 複数の HTTP MCP エージェント
    
    async def parallel_analysis(self, file_patterns: list[str]):
        """並列ファイル分析"""
        tasks = []
        
        for i, pattern in enumerate(file_patterns):
            agent = self.agents[i % len(self.agents)]  # ラウンドロビン
            task = agent.invoke(f"search and analyze files matching {pattern}")
            tasks.append(task)
        
        # 並列実行
        results = await asyncio.gather(*tasks)
        return self.consolidate_results(results)
    
    async def load_balanced_file_processing(self, file_list: list[str]):
        """負荷分散ファイル処理"""
        chunk_size = len(file_list) // len(self.agents)
        
        processing_tasks = []
        for i, agent in enumerate(self.agents):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < len(self.agents) - 1 else len(file_list)
            file_chunk = file_list[start_idx:end_idx]
            
            task = self.process_file_chunk(agent, file_chunk)
            processing_tasks.append(task)
        
        return await asyncio.gather(*processing_tasks)
```

### 2. HTTP キャッシュ機能付きエージェント

```python
import aiohttp
from aiohttp_cache import CacheBackend, setup_cache

class CachedMCPAgent:
    def __init__(self, base_url: str, cache_ttl: int = 300):
        self.base_url = base_url
        self.cache_ttl = cache_ttl
        self.session = None
    
    async def initialize(self):
        """キャッシュ付きHTTPセッション初期化"""
        cache = CacheBackend('memory', expire_after=self.cache_ttl)
        self.session = aiohttp.ClientSession()
        setup_cache(self.session, cache)
    
    async def cached_file_read(self, file_path: str):
        """キャッシュ付きファイル読み取り"""
        # キャッシュキー生成
        cache_key = f"file_content:{file_path}"
        
        # キャッシュ確認
        cached_content = await self.get_from_cache(cache_key)
        if cached_content:
            return cached_content
        
        # MCP サーバーから取得
        content = await self.mcp_read_file(file_path)
        
        # キャッシュに保存
        await self.save_to_cache(cache_key, content)
        return content
    
    async def smart_cache_invalidation(self, file_path: str):
        """スマートキャッシュ無効化"""
        # ファイル更新時刻確認
        file_info = await self.mcp_get_file_info(file_path)
        last_modified = file_info.get('last_modified')
        
        # キャッシュされた更新時刻と比較
        cached_modified = await self.get_cached_modified_time(file_path)
        
        if last_modified != cached_modified:
            # キャッシュ無効化
            await self.invalidate_cache(f"file_content:{file_path}")
            await self.save_modified_time(file_path, last_modified)
```

### 3. 高可用性 MCP クライアント

```python
class HighAvailabilityMCPClient:
    def __init__(self, server_urls: list[str]):
        self.server_urls = server_urls
        self.current_server = 0
        self.health_status = {url: True for url in server_urls}
    
    async def execute_with_failover(self, operation: str, params: dict):
        """フェイルオーバー付き操作実行"""
        attempts = 0
        max_attempts = len(self.server_urls)
        
        while attempts < max_attempts:
            current_url = self.server_urls[self.current_server]
            
            if not self.health_status[current_url]:
                # 不健全なサーバーをスキップ
                self.current_server = (self.current_server + 1) % len(self.server_urls)
                attempts += 1
                continue
            
            try:
                result = await self.execute_operation(current_url, operation, params)
                return result
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                # サーバーエラー: 健全性マーク更新
                self.health_status[current_url] = False
                print(f"Server {current_url} failed: {e}")
                
                # 次のサーバーに切り替え
                self.current_server = (self.current_server + 1) % len(self.server_urls)
                attempts += 1
        
        raise Exception("All MCP servers are unavailable")
    
    async def health_check_routine(self):
        """定期的な健全性チェック"""
        while True:
            for url in self.server_urls:
                try:
                    # 簡単な ping 操作
                    await self.ping_server(url)
                    self.health_status[url] = True
                except Exception:
                    self.health_status[url] = False
            
            await asyncio.sleep(30)  # 30秒間隔
```

## HTTP MCP サーバー設定

### 1. サーバー起動設定

**基本的な HTTP MCP サーバー**:
```bash
# Node.js での MCP サーバー起動
npx @modelcontextprotocol/server-filesystem --port 3000 --http-endpoint /mcp
```

**Docker での起動**:
```dockerfile
FROM node:18
RUN npm install -g @modelcontextprotocol/server-filesystem
EXPOSE 3000
CMD ["npx", "@modelcontextprotocol/server-filesystem", "--port", "3000", "--http-endpoint", "/mcp"]
```

### 2. カスタム HTTP MCP サーバー

**FastAPI での実装例**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

app = FastAPI()

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: str

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: dict = None
    error: dict = None
    id: str

@app.post("/mcp")
async def handle_mcp_request(request: MCPRequest):
    """MCP リクエスト処理"""
    try:
        if request.method == "tools/call":
            tool_name = request.params.get("name")
            tool_args = request.params.get("arguments", {})
            
            # ツール実行
            result = await execute_tool(tool_name, tool_args)
            
            return MCPResponse(result=result, id=request.id)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
    
    except Exception as e:
        return MCPResponse(
            error={"code": -1, "message": str(e)},
            id=request.id
        )

async def execute_tool(tool_name: str, args: dict):
    """ツール実行ロジック"""
    if tool_name == "read_file":
        return await read_file_implementation(args["path"])
    elif tool_name == "list_directory":
        return await list_directory_implementation(args.get("path", "."))
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
```

## パフォーマンス最適化

### 1. HTTP 接続プール

```python
import aiohttp

class MCPConnectionPool:
    def __init__(self, max_connections: int = 100):
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        self.session = aiohttp.ClientSession(connector=self.connector)
    
    async def make_request(self, url: str, data: dict):
        """プール化された接続でリクエスト実行"""
        async with self.session.post(url, json=data) as response:
            return await response.json()
    
    async def close(self):
        """接続プールのクリーンアップ"""
        await self.session.close()
```

### 2. レスポンス圧縮

```python
# クライアント側での圧縮対応
headers = {
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json',
}

# サーバー側での圧縮（FastAPI）
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 3. ストリーミング最適化

```python
async def stream_large_response(url: str, request_data: dict):
    """大きなレスポンスのストリーミング処理"""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=request_data) as response:
            content = ""
            async for chunk in response.content.iter_chunked(1024):
                chunk_text = chunk.decode('utf-8')
                content += chunk_text
                
                # 部分的な処理（必要に応じて）
                if self.should_process_partial(content):
                    await self.process_partial_content(content)
            
            return content
```

## エラーハンドリング

### 1. HTTP エラー処理

```python
async def robust_mcp_request(url: str, request_data: dict, max_retries: int = 3):
    """ロバストな MCP リクエスト"""
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(url, json=request_data) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limit
                        wait_time = int(response.headers.get('Retry-After', 60))
                        await asyncio.sleep(wait_time)
                        retry_count += 1
                    elif response.status >= 500:  # Server error
                        retry_count += 1
                        await asyncio.sleep(2 ** retry_count)
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
        
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            await asyncio.sleep(2 ** retry_count)
```

### 2. タイムアウト管理

```python
# リクエスト毎のタイムアウト設定
timeout_config = aiohttp.ClientTimeout(
    total=30,      # 総タイムアウト
    connect=5,     # 接続タイムアウト
    sock_read=10,  # 読み取りタイムアウト
)

async with aiohttp.ClientSession(timeout=timeout_config) as session:
    # タイムアウト付きリクエスト実行
    pass
```

## セキュリティ考慮事項

### 1. HTTPS 通信

```python
# HTTPS 通信の強制
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

connector = aiohttp.TCPConnector(ssl=ssl_context)
session = aiohttp.ClientSession(connector=connector)
```

### 2. 認証とアクセス制御

```python
# API キー認証
headers = {
    'Authorization': f'Bearer {api_key}',
    'X-API-Key': api_key,
}

# リクエスト署名
import hmac
import hashlib

def sign_request(secret: str, payload: str) -> str:
    """リクエスト署名生成"""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `filesystem_server.py`: HTTP MCP サーバー実装（存在する場合）

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.tools.mcp_tool`: MCP ツール統合
- `google.adk.tools.mcp_tool.mcp_session_manager`: セッション管理
- `aiohttp`: HTTP クライアント（推奨）
- **HTTP MCP サーバー**: ネットワーク経由でのファイルシステム操作