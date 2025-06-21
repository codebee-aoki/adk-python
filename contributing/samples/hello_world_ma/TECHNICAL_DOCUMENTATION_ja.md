# hello_world_ma - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`hello_world_ma` エージェントは、ADK のマルチエージェントアーキテクチャを学習するための最も基本的なサンプル実装です。複数の専門エージェントを統合し、タスクを適切に委譲する階層的なエージェント構造を通じて、複雑なワークフローの分散処理パターンを示します。

### 主要機能
- **マルチエージェント統合**: 専門エージェントによる責務分離
- **タスク委譲**: ルートエージェントによる適切なサブエージェント選択
- **Example Tool**: 入出力例による学習支援機能
- **階層的な安全設定**: 各レベルでの適切な安全設定

### 対象ユースケース
- マルチエージェントシステムの基本理解
- タスク分散と専門化の学習
- 階層的エージェント設計パターン
- Example Tool を活用した応答品質向上

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (複合タスク)
[root_agent] (DicePrimeBot)
    ├── global_instruction による全体指示
    ├── ExampleTool による学習例提供
    └── sub_agents による専門処理
        ├── [roll_agent] → roll_die() ツール
        └── [prime_agent] → check_prime() ツール
```

### エージェント階層
```
root_agent (coordinater)
├── 役割: タスク分析・委譲・結果統合
├── ツール: ExampleTool (学習例)
└── sub_agents:
    ├── roll_agent (specialist)
    │   ├── 専門: サイコロ振り
    │   └── ツール: roll_die()
    └── prime_agent (specialist)
        ├── 専門: 素数判定
        └── ツール: check_prime()
```

### データフロー
1. ユーザーが複合タスクを要求（例：「サイコロを振って素数かチェック」）
2. `root_agent` がタスクを分析し、適切なサブエージェントを特定
3. `roll_agent` にサイコロ振りタスクを委譲
4. 結果を取得後、`prime_agent` に素数チェックタスクを委譲
5. 両方の結果を統合してユーザーに回答

### コンポーネント構成
- **Root Agent**: タスク調整とエージェント管理
- **Roll Agent**: サイコロ振り専門エージェント
- **Prime Agent**: 素数判定専門エージェント
- **Example Tool**: 入出力例による応答品質向上
- **安全設定**: 各エージェントでの危険コンテンツフィルタ

## 3. コード詳細解説

### 3.1 専門エージェントの実装

#### Roll Agent（サイコロ振り専門）
```python
def roll_die(sides: int) -> int:
    """Roll a die and return the rolled result."""
    return random.randint(1, sides)

roll_agent = Agent(
    name="roll_agent",
    description="Handles rolling dice of different sizes.",
    instruction="""
      You are responsible for rolling dice based on the user's request.
      When asked to roll a die, you must call the roll_die tool with the number of sides as an integer.
    """,
    tools=[roll_die],
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

#### Prime Agent（素数判定専門）
```python
def check_prime(nums: list[int]) -> str:
    """Check if a given list of numbers are prime."""
    primes = set()
    for number in nums:
        number = int(number)
        if number <= 1:
            continue
        is_prime = True
        for i in range(2, int(number**0.5) + 1):
            if number % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.add(number)
    return (
        "No prime numbers found."
        if not primes
        else f"{', '.join(str(num) for num in primes)} are prime numbers."
    )

prime_agent = Agent(
    name="prime_agent",
    description="Handles checking if numbers are prime.",
    instruction="""
      You are responsible for checking whether numbers are prime.
      When asked to check primes, you must call the check_prime tool with a list of integers.
      Never attempt to determine prime numbers manually.
      Return the prime number results to the root agent.
    """,
    tools=[check_prime],
    # 安全設定も同様に設定
)
```

### 3.2 Example Tool の実装

```python
from google.adk.examples.example import Example
from google.adk.tools.example_tool import ExampleTool

example_tool = ExampleTool(
    examples=[
        Example(
            input=types.UserContent(
                parts=[types.Part(text="Roll a 6-sided die.")]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="I rolled a 4 for you.")]
                )
            ],
        ),
        Example(
            input=types.UserContent(
                parts=[types.Part(text="Is 7 a prime number?")]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="Yes, 7 is a prime number.")]
                )
            ],
        ),
        Example(
            input=types.UserContent(
                parts=[
                    types.Part(
                        text="Roll a 10-sided die and check if it's prime."
                    )
                ]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="I rolled an 8 for you.")]
                ),
                types.ModelContent(
                    parts=[types.Part(text="8 is not a prime number.")]
                ),
            ],
        ),
    ]
)
```

**Example Tool の重要な機能:**
- **応答品質向上**: 期待される応答パターンを学習
- **一貫性確保**: 複数のエージェント間での応答スタイル統一
- **複合タスク処理**: 複数ステップのタスク処理例を提供

### 3.3 Root Agent の統合

```python
root_agent = Agent(
    model="gemini-1.5-flash",
    name="root_agent",
    instruction="""
      You are a helpful assistant that can roll dice and check if numbers are prime.
      You delegate rolling dice tasks to the roll_agent and prime checking tasks to the prime_agent.
      Follow these steps:
      1. If the user asks to roll a die, delegate to the roll_agent.
      2. If the user asks to check primes, delegate to the prime_agent.
      3. If the user asks to roll a die and then check if the result is prime, call roll_agent first, then pass the result to prime_agent.
      Always clarify the results before proceeding.
    """,
    global_instruction=(
        "You are DicePrimeBot, ready to roll dice and check prime numbers."
    ),
    sub_agents=[roll_agent, prime_agent],
    tools=[example_tool],
    # 安全設定も含む
)
```

**重要な設計ポイント:**

#### 1. 明確な責務分離
- `roll_agent`: サイコロ振りのみ
- `prime_agent`: 素数判定のみ  
- `root_agent`: 調整と統合

#### 2. global_instruction
- 全体的なエージェントのキャラクター設定
- すべてのサブエージェントで共有される指示

#### 3. 段階的タスク処理
- 複合タスクを順次実行
- 前のタスクの結果を次のタスクの入力として使用

## 4. 設定・環境構築

### 4.1 必要な環境変数
```bash
# .env ファイルまたは環境変数
GOOGLE_API_KEY=your_google_api_key
```

### 4.2 依存関係とインストール
```bash
# 基本依存関係は ADK に含まれる
pip install google-adk

# 特にマルチエージェント機能に追加依存関係は不要
```

### 4.3 実行方法
```bash
# CLI での実行
adk run contributing/samples/hello_world_ma

# Web UI での実行
adk web contributing/samples/hello_world_ma
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### 単一タスクの委譲
```
ユーザー: "Roll a 6-sided die"
root_agent: [roll_agent に委譲] 
roll_agent: [roll_die ツール実行] "I rolled a 4 for you."
```

#### 複合タスクの処理
```
ユーザー: "Roll a 10-sided die and check if it's prime"
root_agent: 
1. [roll_agent に委譲] "I rolled an 8 for you."
2. [prime_agent に8を渡して委譲] "8 is not a prime number."
統合応答: "I rolled an 8, and 8 is not a prime number."
```

### 5.2 マルチエージェント拡張パターン

#### 新しい専門エージェントの追加
```python
# 統計計算専門エージェント
def calculate_statistics(numbers: list[int]) -> dict:
    """Calculate basic statistics"""
    return {
        'mean': sum(numbers) / len(numbers),
        'median': sorted(numbers)[len(numbers)//2],
        'max': max(numbers),
        'min': min(numbers)
    }

stats_agent = Agent(
    name="stats_agent",
    description="Handles statistical calculations.",
    instruction="""
      You are responsible for calculating statistics.
      When asked for statistics, use the calculate_statistics tool.
    """,
    tools=[calculate_statistics],
)

# Root Agent に追加
enhanced_root_agent = Agent(
    # ... 既存設定 ...
    sub_agents=[roll_agent, prime_agent, stats_agent],
)
```

#### 階層の深いマルチエージェント
```python
# 数学専門のサブ統合エージェント
math_coordinator = Agent(
    name="math_coordinator",
    description="Coordinates mathematical operations",
    sub_agents=[prime_agent, stats_agent],
    instruction="Coordinate between prime checking and statistical calculations"
)

# ゲーム専門のサブ統合エージェント  
game_coordinator = Agent(
    name="game_coordinator",
    description="Coordinates game-related operations",
    sub_agents=[roll_agent],
    instruction="Handle all dice and game-related requests"
)

# 最上位の統合エージェント
super_root_agent = Agent(
    name="super_root",
    sub_agents=[math_coordinator, game_coordinator],
    instruction="Delegate to appropriate coordinators based on task type"
)
```

### 5.3 エージェント間通信の最適化

#### 状態共有パターン
```python
class SharedContext:
    def __init__(self):
        self.session_data = {}
        self.previous_results = []
    
    def add_result(self, agent_name: str, result: any):
        self.previous_results.append({
            'agent': agent_name,
            'result': result,
            'timestamp': datetime.now()
        })

# 状態を共有するエージェント
def roll_die_with_history(sides: int, shared_context: SharedContext) -> int:
    result = random.randint(1, sides)
    shared_context.add_result('roll_agent', result)
    return result
```

#### 結果のチェーン処理
```python
async def process_chain(root_agent, tasks: list[str]):
    """Process a chain of related tasks"""
    results = []
    context = {}
    
    for task in tasks:
        # 前のタスクの結果をコンテキストに含める
        enhanced_task = f"{task}\nPrevious results: {results}"
        result = await run_agent(root_agent, enhanced_task)
        results.append(result)
        
    return results
```

### 5.4 パフォーマンス監視

#### エージェント別パフォーマンス追跡
```python
class MultiAgentMonitor:
    def __init__(self):
        self.agent_stats = {}
    
    def track_agent_call(self, agent_name: str, duration: float, success: bool):
        if agent_name not in self.agent_stats:
            self.agent_stats[agent_name] = {
                'calls': 0,
                'total_duration': 0,
                'successes': 0
            }
        
        stats = self.agent_stats[agent_name]
        stats['calls'] += 1
        stats['total_duration'] += duration
        if success:
            stats['successes'] += 1
    
    def get_agent_performance(self, agent_name: str):
        stats = self.agent_stats.get(agent_name, {})
        if stats.get('calls', 0) == 0:
            return None
            
        return {
            'avg_duration': stats['total_duration'] / stats['calls'],
            'success_rate': stats['successes'] / stats['calls']
        }
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "Agent not found in sub_agents"
**原因**: 存在しないサブエージェントに委譲しようとした
**解決法**: サブエージェントの適切な定義と登録
```python
# 正しいサブエージェントの登録
root_agent = Agent(
    sub_agents=[roll_agent, prime_agent],  # 定義済みエージェントのみ
    # ...
)
```

#### エラー: "Circular dependency detected"
**原因**: エージェント間で循環参照が発生
**解決法**: 階層構造の見直し
```python
# 悪い例：循環参照
agent_a = Agent(sub_agents=[agent_b])  
agent_b = Agent(sub_agents=[agent_a])  # 循環参照

# 良い例：明確な階層
root = Agent(sub_agents=[child_a, child_b])
child_a = Agent(tools=[tool_a])
child_b = Agent(tools=[tool_b])
```

#### エラー: "Task delegation timeout"
**原因**: サブエージェントの応答が遅い
**解決法**: タイムアウト設定とエラーハンドリング
```python
import asyncio

async def safe_agent_call(agent, prompt, timeout=30):
    try:
        return await asyncio.wait_for(
            run_agent(agent, prompt), 
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return "Agent call timed out"
```

### 6.2 デバッグとトレーシング

#### エージェント実行のトレーシング
```python
class AgentTracer:
    def __init__(self):
        self.call_stack = []
    
    def trace_call(self, agent_name: str, task: str):
        self.call_stack.append({
            'agent': agent_name,
            'task': task,
            'timestamp': datetime.now(),
            'depth': len(self.call_stack)
        })
    
    def print_trace(self):
        for call in self.call_stack:
            indent = "  " * call['depth']
            print(f"{indent}{call['agent']}: {call['task']}")
```

### 6.3 パフォーマンス最適化

#### 並列エージェント実行
```python
async def parallel_agent_execution(tasks: list[tuple]):
    """Execute multiple agent tasks in parallel"""
    async_tasks = []
    
    for agent, task in tasks:
        async_task = run_agent(agent, task)
        async_tasks.append(async_task)
    
    results = await asyncio.gather(*async_tasks, return_exceptions=True)
    return results
```

#### エージェントプールの使用
```python
class AgentPool:
    def __init__(self, agent_configs: dict, pool_size: int = 5):
        self.pools = {}
        for agent_type, config in agent_configs.items():
            self.pools[agent_type] = [
                create_agent(config) for _ in range(pool_size)
            ]
        self.current_index = {agent_type: 0 for agent_type in agent_configs}
    
    def get_agent(self, agent_type: str):
        pool = self.pools[agent_type]
        agent = pool[self.current_index[agent_type]]
        self.current_index[agent_type] = (
            self.current_index[agent_type] + 1
        ) % len(pool)
        return agent
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### マルチエージェント設計原則
- **単一責任原則**: 各エージェントは特定の機能に特化
- **階層的構造**: 明確な指揮系統と責務分離
- **Example Tool 活用**: 応答品質の統一と向上

#### タスク委譲パターン
```python
# 良い委譲パターン
def delegate_task(self, task_type: str, task_data: any):
    if task_type == "calculation":
        return self.math_agent.process(task_data)
    elif task_type == "data_retrieval":
        return self.data_agent.process(task_data)
    else:
        raise ValueError(f"Unknown task type: {task_type}")
```

### 7.2 スケーラブルなマルチエージェントシステム

#### 動的エージェント管理
```python
class DynamicAgentManager:
    def __init__(self):
        self.agent_registry = {}
        self.agent_capabilities = {}
    
    def register_agent(self, agent_id: str, agent: Agent, capabilities: list):
        self.agent_registry[agent_id] = agent
        self.agent_capabilities[agent_id] = capabilities
    
    def find_suitable_agent(self, required_capability: str):
        suitable_agents = []
        for agent_id, capabilities in self.agent_capabilities.items():
            if required_capability in capabilities:
                suitable_agents.append(self.agent_registry[agent_id])
        return suitable_agents
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **明確な責務分離**: 各エージェントの役割を明確に定義
- **Example Tool 活用**: 応答品質向上のための例示
- **エラーハンドリング**: サブエージェントの失敗に対する適切な処理
- **監視とロギング**: エージェント間の相互作用の追跡

#### 注意点
- **複雑性管理**: 過度な階層化は理解を困難にする
- **パフォーマンス**: エージェント間通信のオーバーヘッド
- **デバッグ**: 分散処理でのトラブルシューティングの困難さ
- **一貫性**: 複数エージェント間での応答スタイルの統一

### 7.4 他のプロジェクトへの応用

#### カスタマーサービスシステム
```python
# FAQ処理エージェント
faq_agent = Agent(
    name="faq_agent",
    description="Handles frequently asked questions",
    tools=[search_faq_database]
)

# 技術サポートエージェント
tech_support_agent = Agent(
    name="tech_support_agent", 
    description="Handles technical support requests",
    tools=[run_diagnostics, create_ticket]
)

# 統合カスタマーサービス
customer_service_agent = Agent(
    name="customer_service",
    sub_agents=[faq_agent, tech_support_agent],
    instruction="Route customer requests to appropriate specialists"
)
```

この hello_world_ma エージェントは、ADK におけるマルチエージェントシステムの基本パターンを理解するのに最適なサンプルです。特に複雑なワークフローの分散処理と、専門エージェントによる責務分離の重要性を学ぶことができます。