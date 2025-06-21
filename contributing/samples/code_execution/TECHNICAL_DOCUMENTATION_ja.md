# コード実行エージェント - 技術ドキュメント

## 概要

コード実行エージェント（`code_execution`）は、データサイエンス分野に特化したコード実行機能を提供するエージェントです。Python コードを Colab ライクな環境で実行し、データ分析、可視化、数値計算を支援します。組み込みのコード実行エンジンにより、ステートフルな実行環境でのインタラクティブなデータ分析が可能です。

## 技術仕様

### アーキテクチャ

```python
# コード実行対応エージェント
root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="data_science_agent", 
    instruction=base_system_instruction() + "...",
    code_executor=BuiltInCodeExecutor(),  # 組み込みコード実行エンジン
)
```

### 主要コンポーネント

#### 1. BuiltInCodeExecutor
- **機能**: Python コードの実行とステート管理
- **実行環境**: Colab ライクなノートブック環境
- **特徴**: 変数の永続化、ライブラリの事前インポート

#### 2. システム指示（base_system_instruction）
- **目的**: データ分析タスクのガイドライン
- **重点**: 仮定の回避と精度の確保
- **アプローチ**: 段階的な分析手法

## 実行環境の特徴

### 事前インポート済みライブラリ
```python
# 以下のライブラリは既にインポート済み（再インポート不要）
import io
import math  
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
```

### ステートフル実行
- **変数の永続化**: 一度定義した変数は後続の実行で利用可能
- **ファイルの保持**: 読み込んだファイルやデータは再ロード不要
- **ライブラリ状態**: インポートしたライブラリは保持される

## システム指示の詳細

### 基本ガイドライン

#### 1. 目的指向アプローチ
```text
**Objective:** データ分析目標の達成を支援
- 段階的アプローチ（一度にすべて解決しない）
- 次のステップのみ生成
```

#### 2. 出力可視化の重要性
```python
# DataFrame の形状確認
print(df.shape)

# 数値計算結果の表示  
x = 10 ** 9 - 12 ** 5
print(f'{x=}')

# 変数の直接表示
print(f'{variable=}')
```

#### 3. 仮定回避の原則
```text
**No Assumptions:** データの性質や列名について仮定しない
- `explore_df` 結果に基づく分析
- データ自体から得られる情報のみ使用
```

### データ処理ガイドライン

#### 1. 利用可能ファイルの制限
```text
**Available files:** 指定されたファイルのみ使用
```

#### 2. プロンプト内データの処理
```text
**Data in prompt:** プロンプト内のデータを pandas DataFrame として解析
- すべてのデータを解析
- 与えられたデータの編集禁止
```

#### 3. 回答可能性の判断
```text
**Answerability:** 利用可能データで回答不可能な場合の対応
- 理由の説明
- 必要なデータタイプの提案
```

## 実行フロー

### 1. データ探索段階
```python
# データの基本情報確認
print(df.info())
print(df.describe())
print(df.head())
```

### 2. 分析段階
```python
# 必要な計算や処理
result = df.groupby('column').mean()
print(f'分析結果: {result}')
```

### 3. 可視化段階
```python
# グラフの作成（トレンド分析時のソート）
df_sorted = df.sort_values('x_axis_column')
plt.plot(df_sorted['x_axis_column'], df_sorted['y_axis_column'])
plt.show()
```

## 実行例

### 基本的なデータ分析

**ユーザー入力**:
```text
この売上データを分析して、月別の売上トレンドを教えてください。
```

**エージェントの実行**:
```python
# データの確認
print(df.shape)
print(df.columns.tolist())
print(df.head())

# 月別売上の集計
monthly_sales = df.groupby('month')['sales'].sum()
print(f'月別売上: {monthly_sales}')

# トレンドの可視化
monthly_sales.plot(kind='line')
plt.title('月別売上トレンド')
plt.xlabel('月')
plt.ylabel('売上')
plt.show()
```

### 複雑なデータ処理

**プロンプト内データの処理例**:
```text
以下のデータを分析してください：
名前,年齢,給与
田中,25,400000
佐藤,30,450000
高橋,35,500000
```

**エージェントの実行**:
```python
# プロンプトデータの DataFrame 化
import io
data = """名前,年齢,給与
田中,25,400000
佐藤,30,450000
高橋,35,500000"""

df = pd.read_csv(io.StringIO(data))
print(f'データ形状: {df.shape}')
print(df.head())

# 分析実行
print(f'平均年齢: {df["年齢"].mean()}')
print(f'平均給与: {df["給与"].mean()}')
```

## 高度な機能

### 1. 可視化のベストプラクティス
```python
# トレンド分析時の重要な処理
def plot_trend(df, x_col, y_col):
    # データをx軸でソート（重要）
    df_sorted = df.sort_values(x_col)
    plt.figure(figsize=(10, 6))
    plt.plot(df_sorted[x_col], df_sorted[y_col])
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f'{y_col} vs {x_col}')
    plt.show()
```

### 2. 段階的分析アプローチ
```python
# ステップ1: データ理解
print("=== データ基本情報 ===")
print(df.info())

# ステップ2: 探索的データ分析
print("=== 探索的分析 ===") 
print(df.describe())

# ステップ3: 具体的な分析
# （次のステップのみ実行）
```

### 3. エラーハンドリング
```python
# データの存在確認
if 'target_column' in df.columns:
    analysis_result = df['target_column'].analysis()
else:
    print("指定された列が存在しません。利用可能な列:")
    print(df.columns.tolist())
```

## 制約事項

### 1. パッケージインストール禁止
```text
**重要**: `pip install ...` の実行は禁止
- 事前インストール済みライブラリのみ使用
```

### 2. データソートの必須化
```text
**トレンド分析**: x軸によるデータソートが必須
- `df.sort_values(x_axis)` の実行
```

### 3. 段階的実行原則
```text
**実行方針**: 一度にすべてを解決しない
- 次のステップのみ生成
- ユーザーのフィードバックを待つ
```

## 実践的な応用

### 1. 売上データ分析
```python
# 売上トレンド分析
sales_trend = df.groupby('date')['sales'].sum().sort_index()
sales_trend.plot()
plt.title('売上トレンド')
plt.show()
```

### 2. 統計分析
```python
# 相関関係の分析
correlation_matrix = df.corr()
print('相関行列:')
print(correlation_matrix)
```

### 3. 異常値検出
```python
# 四分位数による異常値検出
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['value'] < (Q1 - 1.5 * IQR)) | (df['value'] > (Q3 + 1.5 * IQR))]
print(f'異常値の数: {len(outliers)}')
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- データ分析サンプルスクリプト（存在する場合）

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.code_executors.built_in_code_executor`: コード実行エンジン
- 事前インストール済みライブラリ:
  - `pandas`: データ処理
  - `numpy`: 数値計算
  - `matplotlib`: 可視化
  - `scipy`: 科学計算
  - `io`, `math`, `re`: 標準ライブラリ