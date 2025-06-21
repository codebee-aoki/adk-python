# ADK Issue トリアージエージェント - 技術ドキュメント

## 概要

ADK Issue トリアージエージェント（`adk_triaging_agent`）は、GitHub の adk-python リポジトリの Issue を自動的にトリアージし、適切なラベルを付与するボット機能を提供するエージェントです。未ラベルの Issue を検索し、内容に基づいて適切なカテゴリーラベルを推薦・適用します。

## 技術仕様

### アーキテクチャ

```python
# エージェント定義
root_agent = Agent(
    model="gemini-2.5-pro-preview-05-06",  # LLM モデル
    name="adk_triaging_assistant",         # エージェント名
    description="Triage ADK issues.",      # 説明
    instruction="...",                     # トリアージルール
    tools=[list_issues, add_label_to_issue]  # ツール群
)
```

### 主要コンポーネント

#### 1. Issue 検索機能
- **関数**: `list_issues(issue_count: int)`
- **機能**: GitHub API を使用して未ラベルの Issue を取得
- **実装**: GitHub Search API を使用した検索クエリ
- **戻り値**: 未ラベル Issue のリスト

#### 2. ラベル付与機能
- **関数**: `add_label_to_issue(issue_number: str, label: str)`
- **機能**: Issue に指定されたラベルを付与
- **検証**: 許可されたラベルのみ適用
- **実装**: GitHub Issues API を使用

### 環境設定

#### 必須環境変数
```bash
GITHUB_TOKEN=<GitHub Personal Access Token>  # 必須
OWNER=google                                 # デフォルト値
REPO=adk-python                             # デフォルト値
BOT_LABEL=bot_triaged                       # デフォルト値
INTERACTIVE=1                               # インタラクティブモード
```

#### 許可ラベル一覧
```python
ALLOWED_LABELS = [
    "documentation",  # ドキュメント関連
    "services",      # セッション、メモリサービス
    "question",      # 質問
    "tools",         # ツール関連
    "eval",          # エージェント評価
    "live",          # ストリーミング・ライブ
    "models",        # モデルサポート
    "tracing",       # トレーシング
    "core",          # エージェント オーケストレーション
    "web",           # UI・Web 関連
]
```

## 実行フロー

### 1. Issue の検索と分析
1. GitHub API を使用して未ラベルの Issue を検索
2. Issue の内容を分析し、カテゴリーを判定
3. 適切なラベルを推薦

### 2. ラベリング処理
```python
# インタラクティブモード（デフォルト）
approval_instruction = "Only label them when the user approves the labeling!"

# 自動モード
approval_instruction = "Do not ask for user approval for labeling!"
```

### 3. ラベル判定ルール

| Issue 内容 | 適用ラベル | 判定基準 |
|------------|------------|----------|
| ドキュメント関連質問 | `documentation` | ドキュメントについての質問 |
| セッション・メモリサービス | `services` | セッション、メモリサービス関連 |
| UI・Web関連 | `web` | UI/web について |
| 一般的な質問 | `question` | ユーザーからの質問 |
| ツール関連 | `tools` | ツールに関連する内容 |
| エージェント評価 | `eval` | エージェント評価について |
| ストリーミング・ライブ | `live` | ストリーミング/ライブ機能 |
| モデルサポート | `models` | 非Geminiモデル（LiteLLM、Ollama等） |
| トレーシング | `tracing` | トレーシング機能 |
| コア機能 | `core` | エージェント定義・オーケストレーション |

## セキュリティ考慮事項

### 認証
- GitHub Personal Access Token による API 認証
- Repository への適切な権限が必要（Issues: Write）

### アクセス制御
- 許可されたラベルのみ適用可能
- 環境変数による設定の保護

## 使用例

### 基本的な使用方法

```python
# エージェントの実行
from contributing.samples.adk_triaging_agent.agent import root_agent

# Issue 検索とラベリング
response = await root_agent.invoke("最新の10件の未ラベル Issues を確認してください")
```

### インタラクティブモード
```bash
# 環境変数設定
export GITHUB_TOKEN="your_token_here"
export INTERACTIVE="1"

# エージェント実行（ユーザー承認が必要）
```

### 自動モード
```bash
# 環境変数設定
export GITHUB_TOKEN="your_token_here"  
export INTERACTIVE="0"

# エージェント実行（自動ラベリング）
```

## 技術的制約

### API制限
- GitHub API レート制限に準拠
- 認証済みリクエスト: 5,000/時間

### 処理制限
- 一度に処理可能な Issue 数に制限あり
- タイムアウト設定: 60秒

## 拡張可能性

### カスタムラベル
- `ALLOWED_LABELS` 配列の変更で新しいラベルカテゴリーを追加可能

### 判定ロジック
- `instruction` での判定ルールのカスタマイズ
- LLM モデルの変更による精度向上

## 関連ファイル

- `agent.py`: メインエージェント実装
- `main.py`: 実行エントリーポイント（存在する場合）
- `README.md`: 英語版ドキュメント
- `README_ja.md`: 日本語版ドキュメント

## 依存関係

- `google.adk`: ADK フレームワーク
- `requests`: HTTP クライアント
- GitHub API v3 対応