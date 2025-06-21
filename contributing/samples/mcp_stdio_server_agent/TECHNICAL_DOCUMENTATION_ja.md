# MCP STDIO サーバーエージェント - 技術ドキュメント

## 概要

MCP STDIO サーバーエージェント（`mcp_stdio_server_agent`）は、Model Context Protocol（MCP）の STDIO 接続を使用してファイルシステム操作を行うエージェントです。外部プロセスとしてファイルシステム MCP サーバーを起動し、安全な読み取り専用アクセスでファイル操作を実現します。プロセス間通信とセキュリティ制御の実装パターンを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# MCP STDIO サーバーエージェント
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='enterprise_assistant',
    instruction=f"Help user accessing their file systems. Allowed directory: {_allowed_path}",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',                                              # Node.js 実行環境
                    args=['-y', '@modelcontextprotocol/server-filesystem', _allowed_path],  # MCP サーバー起動
                ),
                timeout=5,  # 接続タイムアウト
            ),
            tool_filter=[...],  # セキュリティフィルタ
        )
    ],
)
```

### 主要コンポーネント

#### 1. STDIO 接続パラメータ
```python
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

connection_params = StdioConnectionParams(
    server_params=StdioServerParameters(
        command='npx',                                    # Node.js パッケージランナー
        args=[                                           # サーバー起動引数
            '-y',                                        # 自動インストール許可
            '@modelcontextprotocol/server-filesystem',   # ファイルシステム MCP サーバー
            _allowed_path,                               # 許可ディレクトリパス
        ],
    ),
    timeout=5,  # 接続タイムアウト（秒）
)
```

#### 2. 許可ディレクトリ制限
```python
import os

_allowed_path = os.path.dirname(os.path.abspath(__file__))
# エージェント実行ディレクトリのみアクセス許可
```

#### 3. セキュリティフィルタ
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

## STDIO 通信フロー

### 1. プロセス起動と接続

**MCP サーバープロセス起動**:
```text
Parent Process (ADK Agent)
↓
spawn: npx -y @modelcontextprotocol/server-filesystem /allowed/path
↓
Child Process (MCP Server)
↓
STDIO 双方向通信チャネル確立
```

**通信チャネル**:
```text
ADK Agent ←→ STDIN/STDOUT ←→ MCP Server
          ←→ STDERR (ログ)   ←→
```

### 2. ツール実行フロー

**ファイル読み取りリクエスト**:
```text
User: "agent.py の内容を確認してください"
↓
Agent: read_file ツール呼び出し
↓
STDOUT → MCP Server: {"method": "read_file", "params": {"path": "agent.py"}}
↓
MCP Server: ファイル読み取り実行
↓
STDIN ← MCP Server: {"result": "ファイル内容..."}
↓
Agent: 結果を解析して応答生成
```

### 3. エラーハンドリング

**プロセスエラー処理**:
```text
Process Error
↓
STDERR からエラー情報取得
↓
適切なエラーメッセージを生成
↓
ユーザーへのフレンドリーな応答
```

## 実行例

### 基本的なファイル操作

**単一ファイルの読み取り**:
```python
response = await root_agent.invoke("このディレクトリの agent.py ファイルの内容を教えてください")

# 実行フロー:
# 1. MCP サーバープロセス起動
# 2. read_file ツール呼び出し（path: agent.py）
# 3. STDIO 経由でファイル内容取得
# 4. 内容の要約と説明
# 5. プロセス終了
```

**ディレクトリ構造の確認**:
```python
response = await root_agent.invoke("このディレクトリの構造を視覚的に表示してください")

# 実行フロー:
# 1. directory_tree ツール呼び出し
# 2. 許可ディレクトリのツリー構造取得
# 3. 階層構造の視覚的表示
```

### 高度なファイル操作

**複数ファイルの分析**:
```python
query = "このディレクトリの Python ファイルをすべて検索し、各ファイルの概要を教えてください"
response = await root_agent.invoke(query)

# 実行フロー:
# 1. search_files ツール（*.py パターン）
# 2. 見つかった各ファイルに対して read_file 実行
# 3. 各ファイルの内容分析
# 4. 統合レポート生成
```

**ファイル情報の詳細確認**:
```python
response = await root_agent.invoke("README.md ファイルの詳細情報（サイズ、更新日時など）を確認してください")

# 実行フロー:
# 1. get_file_info ツール呼び出し
# 2. ファイルメタデータ取得
# 3. 人間が読みやすい形式で情報整理
```

## 高度な実装例

### 1. コードベース分析エージェント

```python
class CodebaseAnalyzer:
    def __init__(self, mcp_agent):
        self.agent = mcp_agent
    
    async def analyze_project_structure(self):
        """プロジェクト構造分析"""
        # ディレクトリツリー取得
        tree = await self.agent.invoke("directory_tree")
        
        # Python ファイル検索
        python_files = await self.agent.invoke("search_files *.py")
        
        # 設定ファイル検索
        config_files = await self.agent.invoke("search_files *.json *.yaml *.toml")
        
        # ドキュメント検索
        docs = await self.agent.invoke("search_files *.md *.rst *.txt")
        
        return {
            'structure': tree,
            'source_files': python_files,
            'config_files': config_files,
            'documentation': docs,
        }
    
    async def generate_code_metrics(self):
        """コードメトリクス生成"""
        python_files = await self.agent.invoke("search_files *.py")
        
        metrics = {}
        for file_path in python_files:
            content = await self.agent.invoke(f"read_file {file_path}")
            file_info = await self.agent.invoke(f"get_file_info {file_path}")
            
            metrics[file_path] = {
                'size_bytes': file_info['size'],
                'line_count': len(content.split('\n')),
                'function_count': content.count('def '),
                'class_count': content.count('class '),
                'import_count': content.count('import '),
            }
        
        return metrics
```

### 2. ドキュメント管理システム

```python
class DocumentationManager:
    async def organize_documentation(self):
        """ドキュメント整理"""
        # マークダウンファイル検索
        md_files = await self.agent.invoke("search_files *.md")
        
        doc_structure = {}
        for md_file in md_files:
            content = await self.agent.invoke(f"read_file {md_file}")
            
            # ヘッダー抽出
            headers = self.extract_headers(content)
            
            doc_structure[md_file] = {
                'headers': headers,
                'word_count': len(content.split()),
                'sections': len([h for h in headers if h.startswith('#')]),
            }
        
        return doc_structure
    
    async def validate_documentation(self):
        """ドキュメント検証"""
        # README 存在確認
        readme_exists = await self.agent.invoke("get_file_info README.md")
        
        # ライセンスファイル確認
        license_exists = await self.agent.invoke("search_files LICENSE*")
        
        # 貢献ガイド確認
        contributing_exists = await self.agent.invoke("search_files CONTRIBUTING*")
        
        return {
            'readme': readme_exists is not None,
            'license': len(license_exists) > 0,
            'contributing': len(contributing_exists) > 0,
        }
```

### 3. セキュリティ監査エージェント

```python
class SecurityAuditor:
    async def scan_for_secrets(self):
        """機密情報スキャン"""
        all_files = await self.agent.invoke("search_files *")
        
        potential_secrets = []
        secret_patterns = [
            r'api[_-]?key',
            r'secret[_-]?key', 
            r'password',
            r'token',
            r'private[_-]?key',
        ]
        
        for file_path in all_files:
            if self.is_text_file(file_path):
                content = await self.agent.invoke(f"read_file {file_path}")
                
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        potential_secrets.append({
                            'file': file_path,
                            'pattern': pattern,
                            'line_numbers': self.find_line_numbers(content, pattern)
                        })
        
        return potential_secrets
    
    async def check_file_permissions(self):
        """ファイル権限チェック"""
        all_files = await self.agent.invoke("list_directory .")
        
        permission_report = {}
        for file_path in all_files:
            file_info = await self.agent.invoke(f"get_file_info {file_path}")
            
            # 権限分析
            if 'permissions' in file_info:
                perms = file_info['permissions']
                if self.is_overly_permissive(perms):
                    permission_report[file_path] = {
                        'current_permissions': perms,
                        'recommended': self.recommend_permissions(file_path),
                        'risk_level': self.assess_risk(perms)
                    }
        
        return permission_report
```

## プロセス管理とモニタリング

### 1. プロセスライフサイクル

**起動シーケンス**:
```python
async def start_mcp_server():
    """MCP サーバー起動"""
    process = await asyncio.create_subprocess_exec(
        'npx', '-y', '@modelcontextprotocol/server-filesystem', allowed_path,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    return process

async def monitor_process_health(process):
    """プロセス健全性監視"""
    while process.returncode is None:
        # プロセス状態チェック
        if process.poll() is not None:
            print(f"MCP サーバープロセス終了: {process.returncode}")
            break
        
        await asyncio.sleep(1)
```

### 2. エラー処理とリカバリ

**プロセス再起動**:
```python
class MCPServerManager:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.retry_count = 0
    
    async def start_with_retry(self):
        """リトライ付きサーバー起動"""
        while self.retry_count < self.max_retries:
            try:
                self.process = await self.start_mcp_server()
                self.retry_count = 0  # 成功時はカウントリセット
                return self.process
            except Exception as e:
                self.retry_count += 1
                wait_time = 2 ** self.retry_count
                print(f"MCP サーバー起動失敗: {e}. {wait_time}秒後にリトライ")
                await asyncio.sleep(wait_time)
        
        raise Exception("MCP サーバーの起動に失敗しました")
```

### 3. パフォーマンス最適化

**接続プール**:
```python
class MCPConnectionPool:
    def __init__(self, pool_size=5):
        self.pool_size = pool_size
        self.available_connections = asyncio.Queue()
        self.active_connections = set()
    
    async def get_connection(self):
        """接続取得"""
        if not self.available_connections.empty():
            connection = await self.available_connections.get()
        else:
            if len(self.active_connections) < self.pool_size:
                connection = await self.create_new_connection()
            else:
                # プールが満杯の場合は待機
                connection = await self.available_connections.get()
        
        self.active_connections.add(connection)
        return connection
    
    async def return_connection(self, connection):
        """接続返却"""
        self.active_connections.discard(connection)
        await self.available_connections.put(connection)
```

## トラブルシューティング

### 1. プロセス起動失敗

```python
# 一般的な問題:
# - Node.js が未インストール
# - npm パッケージの問題
# - 権限不足
# - ネットワーク接続問題

async def diagnose_startup_issues():
    """起動問題の診断"""
    checks = {
        'node_available': await check_node_installation(),
        'npm_access': await check_npm_access(),
        'network': await check_network_connectivity(),
        'permissions': await check_directory_permissions(),
    }
    
    return checks
```

### 2. STDIO 通信エラー

```python
async def handle_stdio_errors(error):
    """STDIO エラーハンドリング"""
    if "broken pipe" in str(error).lower():
        print("プロセス間通信が切断されました。サーバーを再起動します。")
        await restart_mcp_server()
    elif "timeout" in str(error).lower():
        print("通信タイムアウトが発生しました。タイムアウト値を調整します。")
        # タイムアウト値を増加
    else:
        print(f"未知の STDIO エラー: {error}")
```

## 関連ファイル

- `agent.py`: メインエージェント実装

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.tools.mcp_tool`: MCP ツール統合
- `mcp`: MCP プロトコル実装
- `@modelcontextprotocol/server-filesystem`: ファイルシステム MCP サーバー（npm）
- **Node.js**: 外部プロセス実行環境