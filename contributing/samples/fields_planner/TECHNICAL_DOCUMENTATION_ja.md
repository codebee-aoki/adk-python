# プランナー機能デモエージェント - 技術ドキュメント

## 概要

プランナー機能デモエージェント（`fields_planner`）は、ADK フレームワークの高度なプランニング機能を実演するエージェントです。BuiltInPlanner と思考機能（Thinking Config）を活用し、サイコロ転がしと素数判定を通じて、エージェントの計画的思考プロセスと段階的推論を可視化します。

## 技術仕様

### アーキテクチャ

```python
# プランナー対応エージェント
root_agent = Agent(
    model='gemini-2.5-pro-preview-03-25',
    name='data_processing_agent',
    tools=[roll_die, check_prime],
    
    # 高度なプランナー設定
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,  # 思考プロセスを出力に含める
        ),
    ),
    
    # 代替プランナー（コメントアウト）
    # planner=PlanReActPlanner(),
)
```

### 主要コンポーネント

#### 1. BuiltInPlanner
- **機能**: ADK の組み込みプランニングエンジン
- **特徴**: 思考プロセスの可視化
- **設定**: ThinkingConfig による思考出力制御

#### 2. 思考設定（ThinkingConfig）
```python
thinking_config=types.ThinkingConfig(
    include_thoughts=True,  # 思考プロセスを含める
)
```

#### 3. 代替プランナー
```python
# ReAct パターンベースのプランナー
# planner=PlanReActPlanner(),
```

### デモツール

#### 1. サイコロ転がしツール
```python
def roll_die(sides: int, tool_context: ToolContext) -> int:
    """サイコロを転がし、結果を履歴として保存"""
    result = random.randint(1, sides)
    
    # 履歴管理
    if not 'rolls' in tool_context.state:
        tool_context.state['rolls'] = []
    tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
    
    return result
```

#### 2. 素数判定ツール
```python
async def check_prime(nums: list[int]) -> str:
    """数値リストから素数を特定（非同期処理）"""
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

## プランニング機能

### 1. 思考プロセスの可視化

**実行前の思考例**:
```text
<thinking>
ユーザーは6面サイコロを転がして素数を確認したいと言っています。
これには以下のステップが必要です：

1. roll_die ツールを使って6面サイコロを転がす
2. その結果を待つ
3. check_prime ツールを使って結果が素数かどうか確認する

まず、roll_die(6) を呼び出します。
</thinking>
```

### 2. 段階的実行計画

**計画の実行順序**:
1. **ツール呼び出し計画**: 必要なツールの特定
2. **依存関係の解析**: ツール間の実行順序決定
3. **結果の統合**: 複数ツールの結果をまとめる
4. **応答の生成**: 最終的な回答の構築

### 3. 状態管理

**ツールコンテキストの活用**:
```python
# 履歴の保存と参照
tool_context.state['rolls'] = [3, 5, 2, 7]  # 過去の転がし結果
previous_rolls = tool_context.state.get('rolls', [])
```

## 実行フロー

### 基本的な実行パターン

**単一ツール実行**:
```text
ユーザー: "6面サイコロを転がしてください"

思考プロセス:
<thinking>
ユーザーはサイコロを転がすことを求めています。
roll_die ツールを sides=6 で呼び出します。
</thinking>

実行: roll_die(6)
結果: 4
応答: "6面サイコロを転がした結果、4が出ました。"
```

**複合ツール実行**:
```text
ユーザー: "8面サイコロを転がして、結果が素数か確認してください"

思考プロセス:
<thinking>  
これには2つのステップが必要です：
1. roll_die(8) でサイコロを転がす
2. その結果をcheck_prime で素数判定する

まず roll_die を実行し、結果を待ってから check_prime を呼び出します。
</thinking>

実行1: roll_die(8)
結果1: 7
実行2: check_prime([7])
結果2: "7 are prime numbers."
応答: "8面サイコロを転がした結果7が出ました。7は素数です。"
```

### 並列実行計画

**複数サイコロの同時処理**:
```text
ユーザー: "4面、6面、8面のサイコロを同時に転がしてください"

思考プロセス:
<thinking>
3つのサイコロを並列で転がすことができます：
- roll_die(4)
- roll_die(6) 
- roll_die(8)

これらは並列実行可能です。
</thinking>

並列実行: roll_die(4), roll_die(6), roll_die(8)
結果: [2, 5, 3]
応答: "4面サイコロ: 2, 6面サイコロ: 5, 8面サイコロ: 3"
```

## 高度なプランニング機能

### 1. 依存関係の解析

```python
# ツール間の依存関係を自動判定
# roll_die の結果 → check_prime の入力
planning_graph = {
    'roll_die': [],  # 依存なし
    'check_prime': ['roll_die']  # roll_die の結果に依存
}
```

### 2. エラー処理とリプランニング

```text
<thinking>
roll_die が失敗した場合、check_prime は実行できません。
代替計画として、以前の転がし結果を使用できます。
</thinking>
```

### 3. 最適化計画

```text
<thinking>
複数の過去の転がし結果がある場合、
それらすべてを check_prime で一度に処理する方が効率的です。
</thinking>
```

## 設定とカスタマイズ

### プランナーの選択

#### 1. BuiltInPlanner（デフォルト）
```python
planner=BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,  # 思考プロセス表示
    ),
)
```

#### 2. PlanReActPlanner（代替）
```python  
planner=PlanReActPlanner()
# ReAct パターン: Reasoning + Acting
```

### 安全設定
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

## 使用例

### 基本的な使用方法

```python
# エージェントの実行
response = await root_agent.invoke("10面サイコロを転がして素数を確認してください")

# 思考プロセスが含まれた出力
"""
<thinking>
10面サイコロを転がして、その結果が素数かどうかを確認する必要があります。

1. まず roll_die(10) を呼び出します
2. 結果を待ちます  
3. その結果を check_prime([result]) で確認します
</thinking>

10面サイコロを転がします...
結果: 7
素数判定を行います...
7は素数です！
"""
```

### 複雑なクエリの処理

```python
response = await root_agent.invoke(
    "過去の転がし結果と新しい6面サイコロの結果をまとめて素数判定してください"
)

# プランナーによる複合処理
"""
<thinking>
これには以下の処理が必要です：
1. 過去の転がし結果を tool_context.state から取得
2. 新しく6面サイコロを転がす
3. すべての結果をまとめて素数判定する

効率的な実行順序を計画します。
</thinking>
"""
```

## 実践的な応用

### 1. 複雑なワークフロー管理
```python
# 多段階タスクの自動プランニング
task = "データを取得し、前処理を行い、分析して結果を保存"
# プランナーが自動的にステップを分解し実行順序を決定
```

### 2. 条件分岐を含む処理
```python
# 条件に応じた動的なプラン変更
if previous_result > threshold:
    # プランA を実行
else:
    # プランB を実行
```

### 3. リソース制約下での最適化
```python
# 利用可能なツールとリソースに基づく最適なプラン選択
available_tools = get_available_tools()
optimal_plan = planner.create_plan(task, available_tools)
```

## トラブルシューティング

### 1. 思考プロセスが表示されない
```python
# ThinkingConfig の確認
thinking_config=types.ThinkingConfig(
    include_thoughts=True,  # この設定を確認
)
```

### 2. プランナーの切り替え
```python
# 異なるプランナーの試行
# planner=BuiltInPlanner(...)
planner=PlanReActPlanner()
```

### 3. パフォーマンス問題
```python
# 思考プロセスの無効化でパフォーマンス向上
thinking_config=types.ThinkingConfig(
    include_thoughts=False,
)
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `main.py`: 実行エントリーポイント

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.planners`: プランナーモジュール
- `google.adk.tools.tool_context`: ツールコンテキスト
- `google.genai.types`: Google AI タイプ定義
- `random`: 乱数生成（サイコロ機能）