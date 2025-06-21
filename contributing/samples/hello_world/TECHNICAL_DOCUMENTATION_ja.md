# hello_world - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`hello_world` エージェントは、ADK (Agent Development Kit) の最も基本的なサンプル実装です。カスタム Python 関数をツールとして使用し、状態管理とツール間の連携を学習するための教育用エージェントです。

### 主要機能
- **サイコロ振り機能**: 指定された面数のサイコロを振る
- **素数判定機能**: 数値のリストから素数を特定する
- **状態管理**: サイコロの履歴をセッション状態で保持
- **並列ツール実行**: 複数のツールを一度のリクエストで実行可能

### 対象ユースケース
- ADK の基本概念学習
- カスタムツール開発の理解
- 状態管理パターンの学習
- エージェント-ツール間のインタラクション理解

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (質問/命令)
[hello_world_agent] 
    ↓ (ツール呼び出し)
[カスタムツール群]
    ├── roll_die() - サイコロ振り + 状態更新
    └── check_prime() - 素数判定
    ↓ (結果)
[ToolContext] - 状態管理
    └── state['rolls'] - サイコロ履歴保存
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス)
- **カスタムツール**: `roll_die`, `check_prime`
- **状態管理**: `ToolContext.state`
- **安全設定**: `SafetySetting` でサイコロ振りの誤検出を防止
- **実行環境**: `InMemoryRunner` + `Session`

### データフロー
1. ユーザーがサイコロ振りを要求
2. エージェントが `roll_die` ツールを呼び出し
3. `roll_die` が結果を `ToolContext.state['rolls']` に保存
4. ユーザーが素数チェックを要求
5. エージェントが `check_prime` ツールを呼び出し
6. 必要に応じて履歴から過去のサイコロ結果を参照

### 依存関係
```python
# 外部ライブラリ
import random  # サイコロ振り用
import asyncio  # 非同期実行用
from dotenv import load_dotenv  # 環境変数管理

# ADK コンポーネント
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.genai import types
```

## 3. コード詳細解説

### 3.1 カスタムツール実装

#### roll_die ツール
```python
def roll_die(sides: int, tool_context: ToolContext) -> int:
  """Roll a die and return the rolled result.

  Args:
    sides: The integer number of sides the die has.

  Returns:
    An integer of the result of rolling the die.
  """
  result = random.randint(1, sides)
  if not 'rolls' in tool_context.state:
    tool_context.state['rolls'] = []

  tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
  return result
```

**重要な実装ポイント:**
- `ToolContext` パラメータで状態管理にアクセス
- セッション状態への自動保存 (`tool_context.state`)
- リスト操作での状態更新 (不変性を考慮した実装)

#### check_prime ツール
```python
async def check_prime(nums: list[int]) -> str:
  """Check if a given list of numbers are prime.

  Args:
    nums: The list of numbers to check.

  Returns:
    A str indicating which number is prime.
  """
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
      'No prime numbers found.'
      if not primes
      else f"{', '.join(str(num) for num in primes)} are prime numbers."
  )
```

**重要な実装ポイント:**
- 非同期関数として実装 (`async def`)
- 効率的な素数判定アルゴリズム (平方根まで検査)
- 人間に読みやすい文字列形式で結果を返却

### 3.2 エージェント設定

#### 基本設定
```python
root_agent = Agent(
    model='gemini-2.0-flash',  # 使用するLLMモデル
    name='hello_world_agent',  # エージェント名
    description=(  # エージェントの説明
        'hello world agent that can roll a dice of 8 sides and check prime'
        ' numbers.'
    ),
    instruction="""...""",  # 詳細な指示
    tools=[roll_die, check_prime],  # 使用可能ツール
)
```

#### 詳細指示 (instruction)
エージェントには以下の動作パターンが指示されています:
- サイコロ振りは必ずツールを使用
- 素数チェックも必ずツールを使用
- 並列ツール実行の活用
- 過去のサイコロ結果を参照する場合の処理

#### 安全設定
```python
generate_content_config=types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.OFF,
        ),
    ]
),
```

サイコロ振りが「危険なコンテンツ」として誤検出されるのを防ぐため、該当カテゴリのフィルタを無効化しています。

### 3.3 実行環境 (main.py)

#### セッション管理
```python
runner = InMemoryRunner(
    agent=agent.root_agent,
    app_name=app_name,
)
session_11 = await runner.session_service.create_session(
    app_name=app_name, user_id=user_id_1
)
```

#### 実行パターン
1. **基本実行**: `run_prompt()` - テキストメッセージの送信
2. **バイト実行**: `run_prompt_bytes()` - バイナリデータの送信
3. **状態検証**: `check_rolls_in_state()` - セッション状態の確認

## 4. 設定・環境構築

### 4.1 必要な環境変数
```bash
# .env ファイルまたは環境変数
# Google GenAI API の設定が必要
GOOGLE_API_KEY=your_api_key
```

### 4.2 依存関係とインストール
```bash
# 基本依存関係は ADK に含まれる
pip install google-adk

# 追加依存関係
pip install python-dotenv  # 環境変数管理用
```

### 4.3 実行方法
```bash
# CLI での実行
adk run contributing/samples/hello_world

# Python スクリプトでの実行
cd contributing/samples/hello_world
python main.py

# Web UI での実行
adk web contributing/samples/hello_world
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### サイコロ振り
```
ユーザー: "Roll a die with 6 sides"
エージェント: [roll_die ツールを呼び出し] "I rolled a 4!"
```

#### 素数チェック
```
ユーザー: "Check if 17 and 18 are prime numbers"
エージェント: [check_prime ツールを呼び出し] "17 is a prime number."
```

#### 組み合わせ実行
```
ユーザー: "Roll a 20-sided die and check if the result is prime"
エージェント: 
1. [roll_die ツールを呼び出し]
2. [check_prime ツールを呼び出し] 
"I rolled a 13, and 13 is a prime number!"
```

### 5.2 カスタマイズポイント

#### 新しいツールの追加
```python
def calculate_factorial(n: int, tool_context: ToolContext) -> int:
    """Calculate factorial of n"""
    if n < 0:
        return -1
    result = 1
    for i in range(1, n + 1):
        result *= i
    
    # 状態に保存
    if 'calculations' not in tool_context.state:
        tool_context.state['calculations'] = []
    tool_context.state['calculations'].append(f"factorial({n}) = {result}")
    
    return result

# エージェントに追加
root_agent = Agent(
    tools=[roll_die, check_prime, calculate_factorial],
    # ...
)
```

#### 状態管理の拡張
```python
def enhanced_roll_die(sides: int, tool_context: ToolContext) -> dict:
    """Enhanced dice rolling with statistics"""
    result = random.randint(1, sides)
    
    # 詳細な状態管理
    if 'roll_history' not in tool_context.state:
        tool_context.state['roll_history'] = {
            'rolls': [],
            'total_rolls': 0,
            'sum': 0,
            'max': 0,
            'min': float('inf')
        }
    
    history = tool_context.state['roll_history']
    history['rolls'].append(result)
    history['total_rolls'] += 1
    history['sum'] += result
    history['max'] = max(history['max'], result)
    history['min'] = min(history['min'], result)
    
    return {
        'result': result,
        'average': history['sum'] / history['total_rolls'],
        'total_rolls': history['total_rolls']
    }
```

### 5.3 他のエージェントとの組み合わせ
```python
# マルチエージェント構成例
dice_agent = Agent(
    name="DiceAgent",
    tools=[roll_die],
    instruction="You are specialized in dice rolling"
)

math_agent = Agent(
    name="MathAgent", 
    tools=[check_prime],
    instruction="You are specialized in mathematical calculations"
)

coordinator_agent = Agent(
    name="Coordinator",
    sub_agents=[dice_agent, math_agent],
    instruction="Coordinate between dice and math specialists"
)
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "SafetyError: The response candidate content was flagged"
**原因**: サイコロ振りが危険なコンテンツとして誤検出
**解決法**: 安全設定を適切に設定
```python
generate_content_config=types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.OFF,
        ),
    ]
)
```

#### エラー: "KeyError: 'rolls'"
**原因**: 状態が初期化されていない
**解決法**: 適切な初期化チェック
```python
if 'rolls' not in tool_context.state:
    tool_context.state['rolls'] = []
```

#### エラー: "AttributeError: 'ToolContext' object has no attribute 'state'"
**原因**: ツール関数に `ToolContext` パラメータが不足
**解決法**: 関数シグネチャを確認
```python
# 正しい
def my_tool(param: str, tool_context: ToolContext) -> str:

# 間違い
def my_tool(param: str) -> str:
```

### 6.2 デバッグ方法

#### ログ出力の有効化
```python
from google.adk.cli.utils import logs
logs.log_to_tmp_folder()  # ログファイルに出力
```

#### 状態の確認
```python
async def debug_state():
    session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    print("Current state:", session.state)
```

### 6.3 パフォーマンス考慮事項

- **状態サイズ**: 大きなデータを状態に保存する場合は注意
- **ツール実行時間**: 重い計算処理は非同期化を検討
- **メモリ使用量**: InMemoryRunner は全データをメモリに保持

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### カスタムツール開発パターン
- 関数の docstring でツールの説明を記述
- `ToolContext` を活用した状態管理
- 同期・非同期両方のツール実装

#### 状態管理パターン
- セッション状態の初期化チェック
- 不変性を考慮した状態更新
- 状態の構造化（辞書やリストの活用）

#### エラーハンドリングパターン
- 安全設定による誤検出の回避
- 入力値の検証とエラー処理
- 人間に読みやすいエラーメッセージ

### 7.2 他のプロジェクトへの応用

#### 数値計算エージェント
```python
def calculate_stats(numbers: list[float], tool_context: ToolContext) -> dict:
    """Calculate basic statistics"""
    return {
        'mean': sum(numbers) / len(numbers),
        'median': sorted(numbers)[len(numbers)//2],
        'max': max(numbers),
        'min': min(numbers)
    }
```

#### ゲームエージェント
```python
def play_guess_number(guess: int, tool_context: ToolContext) -> str:
    """Number guessing game"""
    if 'target' not in tool_context.state:
        tool_context.state['target'] = random.randint(1, 100)
        tool_context.state['attempts'] = 0
    
    tool_context.state['attempts'] += 1
    target = tool_context.state['target']
    
    if guess == target:
        return f"Correct! You found {target} in {tool_context.state['attempts']} attempts!"
    elif guess < target:
        return "Too low! Try a higher number."
    else:
        return "Too high! Try a lower number."
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **明確な docstring**: ツールの目的と使用方法を明記
- **型ヒント**: 引数と戻り値の型を明示
- **状態初期化**: 状態アクセス前の存在チェック
- **エラーハンドリング**: 予期しない入力への対応
- **テスト実装**: main.py のような実行例を提供

#### 注意点
- **状態の可変性**: 状態更新時の副作用に注意
- **並行アクセス**: 複数ユーザーでの状態競合
- **メモリリーク**: 大きな状態データの蓄積に注意
- **セキュリティ**: ユーザー入力の検証

この hello_world エージェントは、ADK の基本概念を理解するための最適な出発点であり、カスタムツール開発とエージェント構築の基礎を学ぶのに適しています。