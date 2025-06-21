# Toolbox 統合エージェント - 技術ドキュメント

## 概要

Toolbox 統合エージェント（`toolbox_agent`）は、ADK フレームワークと外部 Toolbox サーバーとの統合を実演するエージェントです。HTTP API 経由でのツール呼び出し、外部ツールセットの動的読み込み、分散ツール管理など、拡張可能なツールエコシステムの構築パターンを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# Toolbox 統合エージェント
root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction="You are a helpful assistant",
    tools=[
        ToolboxToolset(
            server_url="http://127.0.0.1:5000",  # Toolbox サーバーURL
            toolset_name="my-toolset",           # ツールセット名
        )
    ],
)
```

### 主要コンポーネント

#### 1. ToolboxToolset
```python
from google.adk.tools.toolbox_toolset import ToolboxToolset

toolbox_toolset = ToolboxToolset(
    server_url="http://127.0.0.1:5000",  # Toolbox サーバーのエンドポイント
    toolset_name="my-toolset",           # 利用するツールセット名
)
```

#### 2. Toolbox サーバー設定
- **サーバーURL**: `http://127.0.0.1:5000`
- **ツールセット**: `my-toolset`
- **通信プロトコル**: HTTP REST API

## Toolbox システム概要

### 1. Toolbox アーキテクチャ

**システム構成**:
```text
ADK Agent
↓ HTTP Request
ToolboxToolset
↓ REST API Call
Toolbox Server (http://127.0.0.1:5000)
├─ ツールセット管理
├─ ツール実行エンジン
├─ 設定管理
└─ ログ・監視

Toolbox Server
├─ /toolsets/{toolset_name}/tools  # ツール一覧
├─ /toolsets/{toolset_name}/execute # ツール実行
├─ /toolsets/{toolset_name}/config  # 設定取得
└─ /health                          # ヘルスチェック
```

### 2. ツールセット構成

**my-toolset の例**:
```yaml
# tools.yaml
toolset_name: "my-toolset"
version: "1.0.0"
description: "カスタムツールセット"

tools:
  - name: "calculator"
    description: "数学計算を実行"
    parameters:
      - name: "expression"
        type: "string"
        required: true
    
  - name: "file_reader"
    description: "ファイル内容を読み取り"
    parameters:
      - name: "file_path"
        type: "string"
        required: true
    
  - name: "web_scraper"
    description: "ウェブページをスクレイピング"
    parameters:
      - name: "url"
        type: "string"
        required: true
      - name: "selector"
        type: "string"
        required: false
```

## 実行フロー

### 1. ツールセット初期化

**初期化シーケンス**:
```text
1. ADK Agent 起動
   ↓
2. ToolboxToolset 初期化
   ↓ GET /toolsets/my-toolset/tools
3. Toolbox Server からツール一覧取得
   ↓
4. ツールスキーマの ADK エージェントへの登録
   ↓
5. エージェント実行準備完了
```

### 2. ツール実行フロー

**ツール呼び出しの流れ**:
```text
User: "2 + 3 を計算してください"
↓
ADK Agent: ツール選択 (calculator)
↓ POST /toolsets/my-toolset/execute
{
  "tool_name": "calculator",
  "parameters": {
    "expression": "2 + 3"
  }
}
↓
Toolbox Server: calculator ツール実行
↓ HTTP Response
{
  "result": 5,
  "success": true,
  "execution_time": 0.001
}
↓
ADK Agent: 結果を統合して応答生成
```

## 使用例

### 基本的なツール利用

**計算ツールの使用**:
```python
response = await root_agent.invoke("15 × 23 を計算してください")

# 実行フロー:
# 1. calculator ツール呼び出し
# 2. Toolbox サーバーで "15 * 23" 計算
# 3. 結果 345 を受信
# 4. "15 × 23 の計算結果は 345 です"
```

**ファイル読み取りツールの使用**:
```python
response = await root_agent.invoke("config.txt ファイルの内容を教えてください")

# 実行フロー:
# 1. file_reader ツール呼び出し
# 2. Toolbox サーバーで config.txt 読み取り
# 3. ファイル内容を受信
# 4. 内容の要約と説明
```

### 高度なツール連携

**複数ツールの組み合わせ**:
```python
query = """
https://example.com のページから価格情報をスクレイピングして、
その値を使って消費税込み価格を計算してください
"""

response = await root_agent.invoke(query)

# 実行フロー:
# 1. web_scraper ツール: ページから価格抽出
# 2. calculator ツール: 消費税計算
# 3. 統合結果の提示
```

## 高度な実装例

### 1. 動的ツールセット管理

```python
class DynamicToolboxManager:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.loaded_toolsets = {}
        
    async def load_toolset(self, toolset_name: str):
        """ツールセットの動的読み込み"""
        if toolset_name in self.loaded_toolsets:
            return self.loaded_toolsets[toolset_name]
        
        # ツールセット情報の取得
        toolset_info = await self.get_toolset_info(toolset_name)
        
        # ToolboxToolset の作成
        toolbox_toolset = ToolboxToolset(
            server_url=self.server_url,
            toolset_name=toolset_name,
        )
        
        # エージェントの作成
        agent = Agent(
            model="gemini-2.0-flash",
            name=f"{toolset_name}_agent",
            instruction=f"You have access to {toolset_name} toolset",
            tools=[toolbox_toolset],
        )
        
        self.loaded_toolsets[toolset_name] = {
            'toolset': toolbox_toolset,
            'agent': agent,
            'info': toolset_info,
        }
        
        return self.loaded_toolsets[toolset_name]
    
    async def get_available_toolsets(self) -> list[str]:
        """利用可能なツールセット一覧"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.server_url}/toolsets") as response:
                data = await response.json()
                return data.get('toolsets', [])
    
    async def route_request(self, user_query: str) -> str:
        """クエリに最適なツールセットを選択"""
        # 利用可能なツールセット取得
        available_toolsets = await self.get_available_toolsets()
        
        # クエリ内容分析
        best_toolset = await self.analyze_query_requirements(user_query, available_toolsets)
        
        # 適切なエージェントで実行
        toolset_data = await self.load_toolset(best_toolset)
        return await toolset_data['agent'].invoke(user_query)
```

### 2. ツールセット構成管理

```python
class ToolsetConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """設定ファイルの読み込み"""
        with open(self.config_path, 'r') as f:
            if self.config_path.endswith('.yaml'):
                import yaml
                return yaml.safe_load(f)
            else:
                import json
                return json.load(f)
    
    def get_toolset_config(self, toolset_name: str) -> dict:
        """特定ツールセットの設定取得"""
        return self.config.get('toolsets', {}).get(toolset_name, {})
    
    def validate_toolset(self, toolset_name: str) -> bool:
        """ツールセット設定の検証"""
        config = self.get_toolset_config(toolset_name)
        
        required_fields = ['name', 'version', 'tools']
        for field in required_fields:
            if field not in config:
                return False
        
        # ツール定義の検証
        for tool in config['tools']:
            if 'name' not in tool or 'description' not in tool:
                return False
        
        return True
    
    async def deploy_toolset(self, toolset_name: str, server_url: str):
        """ツールセットのデプロイ"""
        config = self.get_toolset_config(toolset_name)
        
        if not self.validate_toolset(toolset_name):
            raise ValueError(f"Invalid toolset configuration: {toolset_name}")
        
        # サーバーへの設定送信
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{server_url}/toolsets/{toolset_name}/deploy",
                json=config
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to deploy toolset: {await response.text()}")
```

### 3. Toolbox サーバー実装例

```python
from flask import Flask, request, jsonify
import importlib
import traceback

class ToolboxServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.toolsets = {}
        self.setup_routes()
    
    def setup_routes(self):
        """API ルートの設定"""
        
        @self.app.route('/toolsets/<toolset_name>/tools', methods=['GET'])
        def get_tools(toolset_name):
            """ツール一覧の取得"""
            if toolset_name not in self.toolsets:
                return jsonify({'error': 'Toolset not found'}), 404
            
            toolset = self.toolsets[toolset_name]
            tools = []
            
            for tool_name, tool_func in toolset['tools'].items():
                tool_info = {
                    'name': tool_name,
                    'description': tool_func.__doc__ or '',
                    'parameters': self.extract_parameters(tool_func),
                }
                tools.append(tool_info)
            
            return jsonify({'tools': tools})
        
        @self.app.route('/toolsets/<toolset_name>/execute', methods=['POST'])
        def execute_tool(toolset_name):
            """ツール実行"""
            if toolset_name not in self.toolsets:
                return jsonify({'error': 'Toolset not found'}), 404
            
            data = request.json
            tool_name = data.get('tool_name')
            parameters = data.get('parameters', {})
            
            toolset = self.toolsets[toolset_name]
            if tool_name not in toolset['tools']:
                return jsonify({'error': f'Tool {tool_name} not found'}), 404
            
            try:
                # ツール実行
                tool_func = toolset['tools'][tool_name]
                result = tool_func(**parameters)
                
                return jsonify({
                    'success': True,
                    'result': result,
                    'tool_name': tool_name,
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc(),
                }), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """ヘルスチェック"""
            return jsonify({
                'status': 'healthy',
                'toolsets': list(self.toolsets.keys()),
                'uptime': self.get_uptime(),
            })
    
    def register_toolset(self, toolset_name: str, tools: dict):
        """ツールセットの登録"""
        self.toolsets[toolset_name] = {
            'name': toolset_name,
            'tools': tools,
            'registered_at': time.time(),
        }
    
    def extract_parameters(self, func) -> list:
        """関数パラメータの抽出"""
        import inspect
        
        sig = inspect.signature(func)
        parameters = []
        
        for param_name, param in sig.parameters.items():
            param_info = {
                'name': param_name,
                'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'any',
                'required': param.default == inspect.Parameter.empty,
            }
            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default
            
            parameters.append(param_info)
        
        return parameters

# ツールセットの例
def calculator(expression: str) -> float:
    """数学式を計算します"""
    try:
        # 安全な数学式評価
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round})
        
        return eval(expression, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

def file_reader(file_path: str) -> str:
    """ファイルの内容を読み取ります"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise FileNotFoundError(f"Could not read file: {e}")

# サーバー起動例
if __name__ == '__main__':
    server = ToolboxServer()
    
    # ツールセット登録
    server.register_toolset('my-toolset', {
        'calculator': calculator,
        'file_reader': file_reader,
    })
    
    server.app.run(host='127.0.0.1', port=5000, debug=True)
```

## セキュリティとアクセス制御

### 1. 認証・認可

```python
class SecureToolboxToolset(ToolboxToolset):
    def __init__(self, server_url: str, toolset_name: str, api_key: str):
        super().__init__(server_url, toolset_name)
        self.api_key = api_key
        self.session_headers = {
            'Authorization': f'Bearer {api_key}',
            'X-API-Key': api_key,
        }
    
    async def make_request(self, endpoint: str, method: str = 'GET', data: dict = None):
        """認証付きリクエスト"""
        url = f"{self.server_url}{endpoint}"
        
        async with aiohttp.ClientSession(headers=self.session_headers) as session:
            if method == 'GET':
                async with session.get(url) as response:
                    return await response.json()
            elif method == 'POST':
                async with session.post(url, json=data) as response:
                    return await response.json()
```

### 2. ツール実行制限

```python
class RestrictedToolboxServer(ToolboxServer):
    def __init__(self):
        super().__init__()
        self.execution_limits = {
            'max_execution_time': 30,      # 30秒
            'max_memory_usage': 100,       # 100MB
            'allowed_file_paths': ['/safe/'], # 許可ディレクトリ
            'blocked_functions': ['exec', 'eval', '__import__'],
        }
    
    def execute_with_limits(self, tool_func, parameters: dict):
        """制限付きツール実行"""
        import signal
        import resource
        
        # メモリ制限
        resource.setrlimit(
            resource.RLIMIT_AS,
            (self.execution_limits['max_memory_usage'] * 1024 * 1024, -1)
        )
        
        # タイムアウト設定
        def timeout_handler(signum, frame):
            raise TimeoutError("Tool execution timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.execution_limits['max_execution_time'])
        
        try:
            # ツール実行
            result = tool_func(**parameters)
            return result
        finally:
            signal.alarm(0)  # タイムアウト解除
```

## 監視とデバッグ

### 1. 実行ログ

```python
class LoggingToolboxToolset(ToolboxToolset):
    def __init__(self, server_url: str, toolset_name: str):
        super().__init__(server_url, toolset_name)
        self.execution_log = []
    
    async def execute_tool(self, tool_name: str, parameters: dict):
        """ログ付きツール実行"""
        start_time = time.time()
        
        try:
            result = await super().execute_tool(tool_name, parameters)
            execution_time = time.time() - start_time
            
            log_entry = {
                'timestamp': time.time(),
                'tool_name': tool_name,
                'parameters': parameters,
                'result': result,
                'execution_time': execution_time,
                'success': True,
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            log_entry = {
                'timestamp': time.time(),
                'tool_name': tool_name,
                'parameters': parameters,
                'error': str(e),
                'execution_time': execution_time,
                'success': False,
            }
            raise
        
        finally:
            self.execution_log.append(log_entry)
        
        return result
    
    def get_execution_stats(self) -> dict:
        """実行統計の取得"""
        if not self.execution_log:
            return {}
        
        successful_executions = [log for log in self.execution_log if log['success']]
        failed_executions = [log for log in self.execution_log if not log['success']]
        
        stats = {
            'total_executions': len(self.execution_log),
            'successful_executions': len(successful_executions),
            'failed_executions': len(failed_executions),
            'success_rate': len(successful_executions) / len(self.execution_log),
            'average_execution_time': sum(log['execution_time'] for log in self.execution_log) / len(self.execution_log),
        }
        
        return stats
```

### 2. パフォーマンス監視

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'total_execution_time': 0,
            'error_count': 0,
            'peak_memory_usage': 0,
        }
    
    def record_execution(self, execution_time: float, memory_usage: float, success: bool):
        """実行メトリクスの記録"""
        self.metrics['request_count'] += 1
        self.metrics['total_execution_time'] += execution_time
        
        if not success:
            self.metrics['error_count'] += 1
        
        if memory_usage > self.metrics['peak_memory_usage']:
            self.metrics['peak_memory_usage'] = memory_usage
    
    def get_performance_report(self) -> dict:
        """パフォーマンスレポート"""
        if self.metrics['request_count'] == 0:
            return {'message': 'No executions recorded'}
        
        return {
            'total_requests': self.metrics['request_count'],
            'average_execution_time': self.metrics['total_execution_time'] / self.metrics['request_count'],
            'error_rate': self.metrics['error_count'] / self.metrics['request_count'],
            'peak_memory_usage_mb': self.metrics['peak_memory_usage'],
        }
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `tools.yaml`: ツールセット設定ファイル
- `tool_box.db`: ツールボックスデータベース（存在する場合）
- `README.md`: 英語版ドキュメント
- `README_ja.md`: 日本語版ドキュメント

## 依存関係

- `google.adk.agents`: ADK エージェント基底クラス
- `google.adk.tools.toolbox_toolset`: Toolbox ツールセット統合
- **Toolbox サーバー**: 外部ツール実行サーバー
- **HTTP クライアント**: aiohttp、requests等
- **設定管理**: YAML、JSON パーサー