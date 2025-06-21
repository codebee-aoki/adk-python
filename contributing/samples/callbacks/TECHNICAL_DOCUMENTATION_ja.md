# コールバック機能デモエージェント - 技術ドキュメント

## 概要

コールバック機能デモエージェント（`callbacks`）は、ADK フレームワークの包括的なコールバックシステムを実演するエージェントです。エージェント実行の各段階（エージェント処理前後、モデル呼び出し前後、ツール実行前後）でカスタムコールバック関数を実行し、実行フローの監視とカスタマイズを可能にします。

## 技術仕様

### アーキテクチャ

```python
# コールバック対応エージェント
root_agent = Agent(
    model='gemini-2.0-flash',
    name='data_processing_agent',
    tools=[roll_die, check_prime],
    
    # 各段階のコールバック設定
    before_agent_callback=[before_agent_cb1, before_agent_cb2, before_agent_cb3],
    after_agent_callback=[after_agent_cb1, after_agent_cb2, after_agent_cb3],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=[before_tool_cb1, before_tool_cb2, before_tool_cb3],
    after_tool_callback=[after_tool_cb1, after_tool_cb2, after_tool_cb3],
)
```

### コールバック種別

#### 1. エージェント処理コールバック

**実行前コールバック**:
```python
async def before_agent_callback(callback_context):
    print('@before_agent_callback')
    return None

def before_agent_cb1(callback_context):
    print('@before_agent_cb1')
```

**実行後コールバック**:
```python
async def after_agent_callback(callback_context):
    print('@after_agent_callback')
    return None

def after_agent_cb2(callback_context):
    print('@after_agent_cb2')
    # ModelContent を返すことで次のターンのコンテキストに含まれる
    return types.ModelContent(
        parts=[types.Part(text='(stopped) after_agent_cb2')],
    )
```

#### 2. モデル呼び出しコールバック

**モデル呼び出し前**:
```python
async def before_model_callback(callback_context, llm_request):
    print('@before_model_callback')
    return None
```

**モデル呼び出し後**:
```python
async def after_model_callback(callback_context, llm_response):
    print('@after_model_callback')
    return None
```

#### 3. ツール実行コールバック

**ツール実行前**:
```python
def before_tool_cb1(tool, args, tool_context):
    print('@before_tool_cb1')
```

**ツール実行後**:
```python
def after_tool_cb2(tool, args, tool_context, tool_response):
    print('@after_tool_cb2')
    return {'test': 'after_tool_cb2', 'response': tool_response}
```

### デモツール

#### 1. サイコロ転がしツール
```python
def roll_die(sides: int, tool_context: ToolContext) -> int:
    """サイコロを転がして結果を返す"""
    result = random.randint(1, sides)
    # ツールコンテキストの状態に履歴を保存
    if not 'rolls' in tool_context.state:
        tool_context.state['rolls'] = []
    tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
    return result
```

#### 2. 素数判定ツール
```python
async def check_prime(nums: list[int]) -> str:
    """数値リストから素数を特定"""
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
    return 'No prime numbers found.' if not primes else f"{', '.join(str(num) for num in primes)} are prime numbers."
```

## 実行フロー

### コールバック実行順序

1. **エージェント処理開始**
   - `before_agent_cb1`, `before_agent_cb2`, `before_agent_cb3`
   - `before_agent_callback`

2. **モデル呼び出し**
   - `before_model_callback`
   - LLM API 呼び出し
   - `after_model_callback`

3. **ツール実行**（必要な場合）
   - `before_tool_cb1`, `before_tool_cb2`, `before_tool_cb3`
   - ツール関数実行
   - `after_tool_cb1`, `after_tool_cb2`, `after_tool_cb3`

4. **エージェント処理終了**
   - `after_agent_cb1`, `after_agent_cb2`, `after_agent_cb3`
   - `after_agent_callback`

### 状態管理

**ツールコンテキスト**:
```python
# 状態の保存と参照
tool_context.state['rolls'] = []  # 履歴保存
previous_rolls = tool_context.state.get('rolls', [])  # 履歴参照
```

## 設定とカスタマイズ

### 安全設定
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

### プランナー設定（コメントアウト）
```python
# planner=BuiltInPlanner(
#     thinking_config=types.ThinkingConfig(
#         include_thoughts=True,
#     ),
# ),
```

## 使用例

### 基本的な実行
```python
# エージェントの実行
response = await root_agent.invoke("6面サイコロを転がして、その結果が素数かどうか確認してください")

# 実行中のコンソール出力例:
# @before_agent_cb1
# @before_agent_cb2  
# @before_agent_cb3
# @before_agent_callback
# @before_model_callback
# @after_model_callback
# @before_tool_cb1
# @before_tool_cb2
# @before_tool_cb3
# @after_tool_cb1
# @after_tool_cb2
# @after_tool_cb3
# @after_agent_cb1
# @after_agent_cb2
# @after_agent_cb3
# @after_agent_callback
```

### 複数ツール並列実行
```python
# 複数のサイコロを同時に転がす
response = await root_agent.invoke("4面、6面、8面のサイコロを同時に転がして、すべての結果の素数を確認してください")
```

## 高度な機能

### コールバック戻り値の処理

**ModelContent の返却**:
```python
def after_agent_cb2(callback_context):
    # ModelContent を返すと次のターンのコンテキストに含まれる
    return types.ModelContent(
        parts=[types.Part(text='(stopped) after_agent_cb2')],
    )
```

**ツール結果の変更**:
```python
def after_tool_cb2(tool, args, tool_context, tool_response):
    # ツール結果を変更して返す
    return {'test': 'after_tool_cb2', 'response': tool_response}
```

### 非同期コールバック
```python
# 非同期処理が必要な場合
async def before_agent_callback(callback_context):
    # 非同期処理を実行
    await some_async_operation()
    return None
```

## 監視とデバッグ

### ログ出力
- 各コールバックでの `print()` 出力
- 実行順序の可視化
- 状態変化の追跡

### デバッグ情報
- `callback_context`: コールバック実行時のコンテキスト
- `tool_context`: ツール実行時の状態
- `llm_request/llm_response`: モデル呼び出し情報

## 実践的な応用例

### 1. パフォーマンス監視
```python
import time

def before_model_callback(callback_context, llm_request):
    callback_context.start_time = time.time()

def after_model_callback(callback_context, llm_response):
    duration = time.time() - callback_context.start_time
    print(f"Model call took {duration:.2f} seconds")
```

### 2. ログ記録
```python
def after_tool_callback(tool, args, tool_context, tool_response):
    log_entry = {
        'tool': tool.__name__,
        'args': args,
        'response': tool_response,
        'timestamp': time.time()
    }
    # ログシステムに記録
    logger.info(log_entry)
```

### 3. エラーハンドリング
```python
def after_agent_callback(callback_context):
    if hasattr(callback_context, 'error'):
        # エラー処理
        handle_error(callback_context.error)
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `main.py`: 実行エントリーポイント

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.tools.tool_context`: ツールコンテキスト
- `google.genai.types`: Google AI タイプ定義
- `random`: 乱数生成