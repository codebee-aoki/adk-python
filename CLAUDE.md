# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際の Claude Code (claude.ai/code) へのガイダンスを提供します。

## プロジェクト概要

これは Agent Development Kit (ADK) - Google のオープンソース Python ツールキットで、AI エージェントを構築するためのものです。このコードベースは、洗練された AI エージェントの開発、評価、デプロイのための包括的なフレームワークを提供し、マルチエージェントオーケストレーション機能を備えています。

## 開発コマンド

### 開発環境のセットアップ
```bash
# uv のインストール (UV は依存関係管理に使用されます)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 仮想環境の作成とアクティベート
uv venv --python "python3.11" ".venv"
source .venv/bin/activate  # Windows の場合: source .\.venv\Scripts\activate

# 開発ツールを含むすべての依存関係をインストール
uv sync --all-extras
```

### ビルド
```bash
# wheel ファイルをビルド
uv build
```

### テスト
```bash
# すべてのユニットテストを実行
pytest ./tests/unittests

# 単一のテストファイルを実行
pytest tests/unittests/path/to/test_file.py

# 特定の extras のみでテストを実行（正確な失敗再現のため）
uv sync --extra test --extra eval
pytest ./tests/unittests

# 注意: Python 3.9 では MCP と A2A テストはスキップされます
```

### コードフォーマットとリンティング
```bash
# コードベース全体を自動フォーマット (isort + pyink を使用)
./autoformat.sh

# autoformat.sh が使用する手動フォーマットコマンド:
isort src/ tests/ contributing/
pyink --config pyproject.toml src/**/*.py tests/**/*.py contributing/**/*.py
```

### 型チェック
```bash
# mypy 型チェッカーを実行
mypy src/google/adk
```

### 開発サーバーの実行
```bash
# ADK Web インターフェースを開始
adk web <path_to_agent_dir>

# エージェントを評価
adk eval <agent_path> <evalset_path>
```

## アーキテクチャ概要

### コアモジュール構造
コードベースは `src/google/adk/` 配下でモジュラーアーキテクチャに従っています：

- **agents/** - LlmAgent（メインエージェントクラス）、SequentialAgent、ParallelAgent、マルチエージェントオーケストレーションを含むエージェント実装
- **models/** - LLM 統合（Google GenAI/Vertex AI、Anthropic、LiteLLM）
- **tools/** - Google サービス、OpenAPI、MCP、カスタム関数を含む広範なツールエコシステム
- **flows/llm_flows/** - ツール呼び出し、ストリーミング、エージェント転送を処理するコア実行フロー
- **sessions/** - インメモリ、データベース、Vertex AI バックエンドによる状態管理
- **evaluation/** - 軌跡と応答評価器を備えたエージェント評価フレームワーク
- **auth/** - 認証情報管理と OAuth2 サポートを備えた認証システム
- **cli/** - FastAPI ベースの開発サーバーと CLI コマンド

### 主要な設計パターン

1. **エージェント階層**: エージェントは sub_agents を持つことができ、階層的なマルチエージェントシステムを可能にします。LlmAgent は sub_agents 間のエージェント転送を自動的に処理します。

2. **ツールシステム**: ツールはメタデータでデコレートされた関数です。フレームワークは以下をサポートします：
   - シンプルな Python 関数をツールとして使用
   - OpenAPI 仕様
   - Google API ディスカバリードキュメント
   - MCP (Model Context Protocol) ツール
   - ツールごとの認証

3. **コールバックシステム**: カスタマイズと監視のための実行フロー全体での広範なコールバックサポート。

4. **非同期ファースト**: リアルタイムインタラクションのためのストリーミングサポートを備えた asyncio 上に構築。

### 重要な実装の詳細

- **バージョン管理**: バージョンは `src/google/adk/version.py` に保存されています
- **モデル登録**: モデルはグローバルレジストリに登録され、文字列名で参照できます
- **ツールフォーマッティング**: ツールは Google の pyink（Black のフォーク）を使用し、2 スペースインデント
- **テスト構造**: ユニットテストは `tests/unittests/` 配下でソース構造をミラーリング
- **デプロイメント**: ローカル開発、Cloud Run コンテナ化、Vertex AI Agent Engine をサポート

### 開発のヒント

- 新機能を追加する際は、類似モジュールの既存パターンに従ってください
- 組み込みの開発 UI (`adk web`) を使用してエージェントを対話的にテスト
- マルチエージェントシステムでは、sub_agents パラメータで親エージェントを定義
- ツールはテスト容易性のため、可能な限り純粋関数にすべきです
- 外部依存関係のモッキング例については既存のテストを確認してください

### 一般的なパターン

```python
# ツールを持つエージェントを定義
from google.adk import Agent
from google.adk.tools import google_search

agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="Your instructions here",
    tools=[google_search]
)

# マルチエージェントのセットアップ
coordinator = Agent(
    name="coordinator",
    model="gemini-2.0-flash",
    sub_agents=[agent1, agent2]  # 自動的なエージェント転送処理
)
```