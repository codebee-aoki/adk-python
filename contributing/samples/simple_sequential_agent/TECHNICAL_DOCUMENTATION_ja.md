# シンプルシーケンシャルエージェント - 技術ドキュメント

## 概要

シンプルシーケンシャルエージェント（`simple_sequential_agent`）は、専門化された2つのサブエージェント（サイコロ転がしエージェントと素数判定エージェント）を順次実行するマルチエージェントシステムです。役割分担による機能分離、エージェント間のデータ受け渡し、シーケンシャル実行パターンなど、実用的なマルチエージェント連携の基本パターンを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# シンプルシーケンシャルエージェント構成
root_agent = SequentialAgent(
    name="simple_sequential_agent",
    sub_agents=[roll_agent, prime_agent],  # 順次実行: roll_agent → prime_agent
)
```

### 主要コンポーネント

#### 1. サイコロ転がしエージェント
```python
roll_agent = LlmAgent(
    name="roll_agent",
    description="Handles rolling dice of different sizes.",
    model="gemini-2.0-flash",
    instruction="You are responsible for rolling dice based on the user's request...",
    tools=[roll_die],  # サイコロ転がしツール
)

def roll_die(sides: int) -> int:
    """サイコロを転がして結果を返す"""
    return random.randint(1, sides)
```

#### 2. 素数判定エージェント
```python
prime_agent = LlmAgent(
    name="prime_agent", 
    description="Handles checking if numbers are prime.",
    model="gemini-2.0-flash",
    instruction="You are responsible for checking whether numbers are prime...",
    tools=[check_prime],  # 素数判定ツール
)

def check_prime(nums: list[int]) -> str:
    """数値リストから素数を特定"""
    primes = set()
    for number in nums:
        # 素数判定ロジック
        ...
    return "結果文字列"
```

#### 3. 安全設定
```python
generate_content_config=types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.OFF,  # サイコロ転がしの誤検知回避
        ),
    ]
)
```

## 実行フロー

### 1. シーケンシャル実行パターン

**基本実行フロー**:
```text
User: "6面サイコロを転がして、結果が素数か確認してください"

1. roll_agent 実行
   ├─ ユーザーリクエスト受信
   ├─ roll_die(6) ツール呼び出し
   ├─ 結果: 5
   ├─ 出力: "6面サイコロを転がした結果、5が出ました"
   
2. prime_agent 実行  
   ├─ roll_agent の出力 + 元のリクエストを受信
   ├─ 数値5を抽出
   ├─ check_prime([5]) ツール呼び出し
   ├─ 結果: "5 are prime numbers."
   ├─ 出力: "5は素数です"

3. 統合結果
   ├─ roll_agent の結果: "5が出ました"
   ├─ prime_agent の結果: "5は素数です"
   ├─ 最終応答: 両エージェントの結果を統合
```

### 2. エージェント間のデータ受け渡し

**データフロー**:
```text
User Input: "サイコロを転がして素数判定"
↓
roll_agent
├─ 入力: ユーザーリクエスト
├─ 処理: roll_die() 実行
├─ 出力: "結果は5です"
↓
prime_agent
├─ 入力: "結果は5です" + 元のユーザーリクエスト
├─ 処理: 出力から数値抽出 → check_prime([5])
├─ 出力: "5は素数です"
↓
Final Result: 統合された回答
```

## 使用例

### 基本的な実行

**サイコロ転がしと素数判定**:
```python
response = await root_agent.invoke("8面サイコロを転がして、結果が素数かどうか教えてください")

# 実行フロー:
# 1. roll_agent: roll_die(8) → 例: 7
# 2. prime_agent: check_prime([7]) → "7 are prime numbers."
# 
# 期待される最終応答:
# "8面サイコロを転がした結果7が出ました。7は素数です。"
```

**複数サイコロの処理**:
```python
response = await root_agent.invoke("4面と6面のサイコロを両方転がして、それぞれが素数か確認してください")

# 実行フロー:
# 1. roll_agent: 4面と6面の両方を処理
# 2. prime_agent: 両方の結果に対して素数判定
```

### 各エージェントの専門性

**roll_agent の責任範囲**:
- サイコロの面数の解釈
- roll_die ツールの呼び出し
- 結果の報告

**prime_agent の責任範囲**:
- 前のエージェントの出力から数値抽出
- check_prime ツールの呼び出し  
- 素数判定結果の報告

## 高度な実装例

### 1. エラーハンドリング付きシーケンシャルエージェント

```python
class RobustSequentialAgent:
    def __init__(self):
        self.roll_agent = self.create_robust_roll_agent()
        self.prime_agent = self.create_robust_prime_agent()
        
        self.sequential_agent = SequentialAgent(
            name="robust_sequential_agent",
            sub_agents=[self.roll_agent, self.prime_agent],
        )
    
    def create_robust_roll_agent(self):
        def safe_roll_die(sides: int) -> dict:
            """エラーハンドリング付きサイコロ転がし"""
            try:
                if sides < 1:
                    return {"error": "サイコロの面数は1以上である必要があります"}
                if sides > 1000:
                    return {"error": "サイコロの面数が大きすぎます"}
                
                result = random.randint(1, sides)
                return {"success": True, "result": result}
            except Exception as e:
                return {"error": f"サイコロ転がし中にエラーが発生: {str(e)}"}
        
        return LlmAgent(
            name="robust_roll_agent",
            model="gemini-2.0-flash",
            instruction="""
            サイコロ転がしを安全に実行してください。
            エラーが発生した場合は適切にエラーメッセージを返してください。
            """,
            tools=[safe_roll_die],
        )
    
    def create_robust_prime_agent(self):
        def safe_check_prime(nums: list[int]) -> dict:
            """エラーハンドリング付き素数判定"""
            try:
                if not nums:
                    return {"error": "判定する数値が指定されていません"}
                
                if any(num < 1 or num > 10000 for num in nums):
                    return {"error": "数値は1以上10000以下である必要があります"}
                
                primes = []
                for number in nums:
                    if number <= 1:
                        continue
                    is_prime = True
                    for i in range(2, int(number**0.5) + 1):
                        if number % i == 0:
                            is_prime = False
                            break
                    if is_prime:
                        primes.append(number)
                
                return {
                    "success": True,
                    "primes": primes,
                    "message": f"{', '.join(map(str, primes))} は素数です" if primes else "素数はありませんでした"
                }
                
            except Exception as e:
                return {"error": f"素数判定中にエラーが発生: {str(e)}"}
        
        return LlmAgent(
            name="robust_prime_agent",
            model="gemini-2.0-flash", 
            instruction="""
            素数判定を安全に実行してください。
            前のエージェントの出力から数値を正確に抽出し、エラーハンドリングを行ってください。
            """,
            tools=[safe_check_prime],
        )
```

### 2. ログ機能付きシーケンシャルエージェント

```python
class LoggingSequentialAgent:
    def __init__(self):
        self.execution_log = []
        
        self.roll_agent = self.create_logging_roll_agent()
        self.prime_agent = self.create_logging_prime_agent()
        
        self.sequential_agent = SequentialAgent(
            name="logging_sequential_agent",
            sub_agents=[self.roll_agent, self.prime_agent],
        )
    
    def create_logging_roll_agent(self):
        def logged_roll_die(sides: int) -> int:
            """ログ付きサイコロ転がし"""
            result = random.randint(1, sides)
            
            log_entry = {
                'agent': 'roll_agent',
                'action': 'roll_die',
                'input': {'sides': sides},
                'output': result,
                'timestamp': datetime.now().isoformat(),
            }
            self.execution_log.append(log_entry)
            
            return result
        
        return LlmAgent(
            name="logging_roll_agent",
            model="gemini-2.0-flash",
            instruction="サイコロを転がし、結果をログに記録してください。",
            tools=[logged_roll_die],
        )
    
    def create_logging_prime_agent(self):
        def logged_check_prime(nums: list[int]) -> str:
            """ログ付き素数判定"""
            primes = set()
            for number in nums:
                if number <= 1:
                    continue
                is_prime = True
                for i in range(2, int(number**0.5) + 1):
                    if number % i == 0:
                        is_prime = False
                        break
                if is_prime:
                    primes.add(number)
            
            result = (
                'No prime numbers found.'
                if not primes
                else f"{', '.join(str(num) for num in primes)} are prime numbers."
            )
            
            log_entry = {
                'agent': 'prime_agent',
                'action': 'check_prime',
                'input': {'numbers': nums},
                'output': result,
                'primes_found': list(primes),
                'timestamp': datetime.now().isoformat(),
            }
            self.execution_log.append(log_entry)
            
            return result
        
        return LlmAgent(
            name="logging_prime_agent",
            model="gemini-2.0-flash",
            instruction="素数判定を行い、結果をログに記録してください。",
            tools=[logged_check_prime],
        )
    
    def get_execution_summary(self):
        """実行サマリーの取得"""
        return {
            'total_steps': len(self.execution_log),
            'agents_used': list(set(log['agent'] for log in self.execution_log)),
            'actions_performed': [log['action'] for log in self.execution_log],
            'execution_timeline': self.execution_log,
        }
```

### 3. 条件分岐付きシーケンシャルエージェント

```python
class ConditionalSequentialAgent:
    def __init__(self):
        self.roll_agent = self.create_roll_agent()
        self.prime_agent = self.create_prime_agent()
        self.statistics_agent = self.create_statistics_agent()
        
        # 基本シーケンス: roll → prime
        self.basic_sequence = SequentialAgent(
            name="basic_sequence",
            sub_agents=[self.roll_agent, self.prime_agent],
        )
        
        # 拡張シーケンス: roll → prime → statistics
        self.extended_sequence = SequentialAgent(
            name="extended_sequence", 
            sub_agents=[self.roll_agent, self.prime_agent, self.statistics_agent],
        )
    
    async def execute_conditional(self, user_input: str):
        """条件に基づくシーケンス選択"""
        # 統計分析が必要かどうか判定
        needs_statistics = any(keyword in user_input.lower() for keyword in [
            '統計', 'statistics', '分析', 'analysis', '確率', 'probability'
        ])
        
        if needs_statistics:
            return await self.extended_sequence.invoke(user_input)
        else:
            return await self.basic_sequence.invoke(user_input)
    
    def create_statistics_agent(self):
        def calculate_statistics(numbers: list[int]) -> dict:
            """数値の統計情報計算"""
            if not numbers:
                return {"error": "統計計算用の数値がありません"}
            
            import statistics
            
            stats = {
                'count': len(numbers),
                'sum': sum(numbers),
                'mean': statistics.mean(numbers),
                'median': statistics.median(numbers),
                'max': max(numbers),
                'min': min(numbers),
            }
            
            if len(numbers) > 1:
                stats['stdev'] = statistics.stdev(numbers)
            
            return stats
        
        return LlmAgent(
            name="statistics_agent",
            model="gemini-2.0-flash",
            instruction="""
            前のエージェントの結果から数値を抽出し、統計情報を計算してください。
            平均値、中央値、標準偏差などを含む詳細な分析を提供してください。
            """,
            tools=[calculate_statistics],
        )
```

## パフォーマンス最適化

### 1. 並列化の検討

```python
# 独立性があるタスクの場合は並列実行も可能
from google.adk.agents import ParallelAgent

# 例: 複数の独立したサイコロを同時に転がす場合
parallel_rolls = ParallelAgent(
    name="parallel_dice_rolling",
    sub_agents=[
        create_die_agent(4),  # 4面サイコロ専用
        create_die_agent(6),  # 6面サイコロ専用  
        create_die_agent(8),  # 8面サイコロ専用
    ]
)
```

### 2. キャッシュ機能

```python
class CachedSequentialAgent:
    def __init__(self):
        self.cache = {}
        self.sequential_agent = SequentialAgent(...)
    
    async def invoke_with_cache(self, input_text: str):
        """キャッシュ付き実行"""
        cache_key = hash(input_text)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self.sequential_agent.invoke(input_text)
        self.cache[cache_key] = result
        
        return result
```

### 3. エージェント間通信の最適化

```python
class OptimizedDataPassing:
    def __init__(self):
        self.shared_context = {}
    
    def create_context_aware_agent(self, name: str, tools: list):
        """コンテキスト共有エージェント"""
        def context_aware_tool_wrapper(original_tool):
            def wrapped_tool(*args, **kwargs):
                # 共有コンテキストにアクセス
                result = original_tool(*args, **kwargs)
                
                # 結果を共有コンテキストに保存
                self.shared_context[f"{name}_last_result"] = result
                
                return result
            return wrapped_tool
        
        wrapped_tools = [context_aware_tool_wrapper(tool) for tool in tools]
        
        return LlmAgent(
            name=name,
            model="gemini-2.0-flash",
            tools=wrapped_tools,
            instruction=f"共有コンテキストを活用してタスクを実行してください。"
        )
```

## トラブルシューティング

### 1. エージェント間データ受け渡しの問題

```python
def debug_agent_communication(sequential_agent, test_input: str):
    """エージェント間通信のデバッグ"""
    print(f"Input: {test_input}")
    
    for i, agent in enumerate(sequential_agent.sub_agents):
        print(f"\n--- Agent {i+1}: {agent.name} ---")
        
        # 各エージェントの入力を確認
        if i == 0:
            agent_input = test_input
        else:
            # 前のエージェントの出力を使用
            agent_input = previous_output + "\n\nOriginal request: " + test_input
        
        print(f"Agent input: {agent_input}")
        
        # エージェント実行
        output = await agent.invoke(agent_input)
        print(f"Agent output: {output}")
        
        previous_output = output
    
    return output
```

### 2. パフォーマンス問題の診断

```python
import time

class PerformanceDiagnostics:
    def __init__(self):
        self.timing_data = []
    
    async def timed_execution(self, sequential_agent, input_text: str):
        """実行時間測定"""
        start_time = time.time()
        
        agent_timings = []
        for i, agent in enumerate(sequential_agent.sub_agents):
            agent_start = time.time()
            
            # エージェント実行（実際の実装に依存）
            result = await agent.invoke(input_text)
            
            agent_end = time.time()
            agent_timings.append({
                'agent': agent.name,
                'duration': agent_end - agent_start,
            })
        
        total_time = time.time() - start_time
        
        self.timing_data.append({
            'input': input_text,
            'total_duration': total_time,
            'agent_timings': agent_timings,
            'timestamp': datetime.now(),
        })
        
        return {
            'result': result,
            'performance': {
                'total_time': total_time,
                'agent_breakdown': agent_timings,
            }
        }
```

## 関連ファイル

- `agent.py`: メインエージェント実装

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.agents.sequential_agent`: シーケンシャルエージェント
- `google.genai.types`: Google AI タイプ定義
- `random`: 乱数生成（サイコロ機能）