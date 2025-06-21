# ADK 学習支援ツールキット

このツールキットは、ADK エージェント学習ガイドを効果的に進めるための実用的なサポートツール集です。

## 📋 学習進捗チェックリスト

### 🟢 基礎パス進捗

#### Week 1: ツール開発基礎
- [ ] **hello_world** 
  - [ ] エージェントを実行できた
  - [ ] カスタムツールの仕組みを理解した
  - [ ] 状態管理（ToolContext）を理解した
  - [ ] 安全設定の必要性を理解した
  - [ ] 新しいツール（フィボナッチ生成）を追加できた

- [ ] **quickstart**
  - [ ] エージェントを実行できた
  - [ ] 統一レスポンス形式の利点を理解した
  - [ ] エラーハンドリングパターンを理解した
  - [ ] 新しい都市データを追加できた

- [ ] **hello_world_anthropic**
  - [ ] Anthropic Claude を使用できた
  - [ ] Google モデルとの違いを理解した
  - [ ] プロバイダー固有設定を理解した
  - [ ] 異なる Claude モデルを試した

#### Week 2: マルチプロバイダーとマルチエージェント
- [ ] **hello_world_litellm**
  - [ ] LiteLLM の統一インターフェースを理解した
  - [ ] 複数プロバイダーを試した
  - [ ] フォールバック機能を実装した
  - [ ] プロバイダー比較システムを作成した

- [ ] **hello_world_ollama**
  - [ ] Ollama をセットアップできた
  - [ ] ローカル LLM を使用できた
  - [ ] プライバシー保護の利点を理解した

- [ ] **hello_world_ma**
  - [ ] マルチエージェント構成を理解した
  - [ ] エージェント間協調の仕組みを理解した
  - [ ] 3つの専門エージェントシステムを作成した

#### Week 3: 状態管理とコールバック
- [ ] **artifact_save_text**
  - [ ] アーティファクトサービスを理解した
  - [ ] データ永続化パターンを理解した

- [ ] **callbacks**
  - [ ] コールバックシステムを理解した
  - [ ] カスタムコールバックを実装した
  - [ ] パフォーマンス測定機能を追加した

### 🔵 統合パス進捗

#### Week 1: Google サービス統合
- [ ] **bigquery**
  - [ ] BigQuery 統合の基本を理解した
  - [ ] SQL クエリ生成を理解した
  - [ ] カスタム分析クエリを作成した

- [ ] **google_search_agent**
  - [ ] Google Search API を理解した
  - [ ] 検索結果処理パターンを理解した

- [ ] **bigquery_agent**
  - [ ] 高度な BigQuery 機能を理解した
  - [ ] 複雑なデータ操作を実装した

#### Week 2: 認証とワークフロー
- [ ] **oauth_calendar_agent**
  - [ ] OAuth2 認証フローを理解した
  - [ ] Google Calendar API を使用できた
  - [ ] 会議スケジューリング機能を追加した

- [ ] **workflow_agent_seq**
  - [ ] シーケンシャルワークフローを理解した
  - [ ] ステップ間データ受け渡しを理解した

- [ ] **simple_sequential_agent**
  - [ ] シンプルシーケンス処理を理解した

#### Week 3: 状態管理とメモリ
- [ ] **session_state_agent**
  - [ ] セッション状態管理を理解した
  - [ ] 永続化戦略を理解した

- [ ] **memory**
  - [ ] メモリシステムの実装を理解した
  - [ ] 会話履歴要約機能を実装した

#### Week 4: エンタープライズ統合
- [ ] **jira_agent**
  - [ ] JIRA 統合を理解した
  - [ ] チケット管理自動化を理解した

- [ ] **application_integration_agent**
  - [ ] Application Integration を理解した

- [ ] **integration_connector_euc_agent**
  - [ ] コネクタベース統合を理解した

- [ ] **toolbox_agent**
  - [ ] ツールボックス管理を理解した
  - [ ] 動的ツール読み込みを理解した

### 🟡 高度パス進捗

#### MCP プロトコル統合
- [ ] **mcp_sse_agent**
  - [ ] MCP SSE プロトコルを理解した
  - [ ] カスタム MCP サーバーを実装した

- [ ] **mcp_stdio_notion_agent**
  - [ ] MCP STDIO プロトコルを理解した

- [ ] **mcp_stdio_server_agent**
  - [ ] MCP サーバー実装を理解した

- [ ] **mcp_streamablehttp_agent**
  - [ ] HTTP ストリーミングを理解した

#### リアルタイム処理と人間協調
- [ ] **live_bidi_streaming_agent**
  - [ ] 双方向ストリーミングを理解した
  - [ ] リアルタイム翻訳システムを実装した

- [ ] **human_in_loop**
  - [ ] 人間協調システムを理解した

- [ ] **generate_image**
  - [ ] 画像生成統合を理解した

#### 高度な出力制御
- [ ] **code_execution**
  - [ ] コード実行エンジンを理解した
  - [ ] セキュアな実行環境を実装した

- [ ] **fields_output_schema**
  - [ ] 構造化出力を理解した

- [ ] **fields_planner**
  - [ ] 構造化プランニングを理解した

### 🔴 専門パス進捗

#### LangChain 統合
- [ ] **langchain_structured_tool_agent**
  - [ ] LangChain 統合を理解した
  - [ ] ハイブリッドアーキテクチャを実装した

- [ ] **langchain_youtube_search_agent**
  - [ ] YouTube API 統合を理解した

- [ ] **rag_agent**
  - [ ] RAG システムを理解した
  - [ ] カスタム RAG システムを構築した

#### システム監視と最適化
- [ ] **telemetry**
  - [ ] テレメトリシステムを理解した

- [ ] **token_usage**
  - [ ] トークン使用量追跡を理解した
  - [ ] コスト監視システムを実装した

- [ ] **non_llm_sequential**
  - [ ] 非 LLM 処理統合を理解した

#### 特殊用途システム
- [ ] **adk_triaging_agent**
  - [ ] トリアージシステムを理解した
  - [ ] カスタマーサポートシステムを実装した

---

## 🛠️ 開発環境セットアップガイド

### 基本環境構築

#### 1. Python 環境準備
```bash
# Python 3.11+ のインストール確認
python --version  # 3.11+ であることを確認

# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトクローン
git clone https://github.com/google/adk-python.git
cd adk-python

# 仮想環境作成
uv venv --python "python3.11" ".venv"
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係インストール
uv sync --all-extras
```

#### 2. API キー設定
```bash
# .env ファイル作成
touch .env

# 以下を .env に追加（必要に応じて）
# GOOGLE_API_KEY=your_google_api_key
# ANTHROPIC_API_KEY=your_anthropic_api_key  
# OPENAI_API_KEY=your_openai_api_key
```

#### 3. Google Cloud 設定（BigQuery, Calendar 等を使用する場合）
```bash
# Google Cloud SDK インストール
# https://cloud.google.com/sdk/docs/install

# 認証設定
gcloud auth application-default login

# プロジェクト設定
gcloud config set project your-project-id
```

### プロバイダー別セットアップ

#### Google AI Studio
1. https://aistudio.google.com/app/apikey でAPI キーを取得
2. 環境変数 `GOOGLE_API_KEY` に設定

#### Anthropic Claude
1. https://console.anthropic.com/ でアカウント作成
2. API キーを取得
3. 環境変数 `ANTHROPIC_API_KEY` に設定

#### OpenAI
1. https://platform.openai.com/api-keys でAPI キーを取得
2. 環境変数 `OPENAI_API_KEY` に設定

#### Ollama (ローカル LLM)
```bash
# Ollama インストール
curl -fsSL https://ollama.ai/install.sh | sh

# モデルダウンロード
ollama pull llama2
ollama pull codellama
```

### 開発ツール設定

#### VSCode 設定
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

#### Git 設定（コントリビューション用）
```bash
# フォークの設定
git remote add personal_origin https://github.com/your-username/adk-python.git

# アップストリームの設定
git remote add upstream https://github.com/google/adk-python.git
```

---

## 🧪 実践演習問題

### 基礎レベル演習

#### 演習1: カスタムツール作成
```python
# 課題: 数学関数ツールセットを作成
def calculate_area_circle(radius: float, tool_context: ToolContext) -> float:
    """円の面積を計算するツール"""
    # TODO: 実装してください
    pass

def calculate_area_rectangle(width: float, height: float, tool_context: ToolContext) -> float:
    """長方形の面積を計算するツール"""  
    # TODO: 実装してください
    pass

# エージェントに統合し、「半径5の円と、幅3高さ4の長方形の面積を教えて」で動作確認
```

#### 演習2: エラーハンドリング
```python
# 課題: 堅牢なツール実装
def safe_divide(dividend: float, divisor: float, tool_context: ToolContext) -> dict:
    """安全な除算ツール（エラーハンドリング付き）"""
    # TODO: ゼロ除算エラーを適切に処理
    # TODO: 統一されたレスポンス形式で返却
    pass
```

#### 演習3: 状態管理
```python
# 課題: 計算履歴を保持するツール
def calculate_with_history(expression: str, tool_context: ToolContext) -> dict:
    """計算結果を履歴として保存するツール"""
    # TODO: 計算結果を tool_context.state に保存
    # TODO: 履歴を表示する機能
    pass

def show_calculation_history(tool_context: ToolContext) -> str:
    """計算履歴を表示するツール"""
    # TODO: 保存された履歴を読みやすい形式で返却
    pass
```

### 中級レベル演習

#### 演習4: 外部API統合
```python
# 課題: 天気予報API統合（実際のAPI使用）
import requests

def get_real_weather(city: str, api_key: str) -> dict:
    """実際の天気APIを使用した天気取得"""
    # TODO: OpenWeatherMap API などの実際のAPIを使用
    # TODO: エラーハンドリングを実装
    # TODO: レスポンスを統一形式に変換
    pass
```

#### 演習5: マルチエージェントシステム
```python
# 課題: レポート生成システム
# データ収集エージェント、分析エージェント、レポート生成エージェントを組み合わせ

data_collector = Agent(
    name="DataCollector",
    tools=[collect_sales_data, collect_customer_data],
    # TODO: 設定を完成させる
)

data_analyzer = Agent(
    name="DataAnalyzer", 
    tools=[analyze_trends, calculate_metrics],
    # TODO: 設定を完成させる
)

report_generator = Agent(
    name="ReportGenerator",
    tools=[generate_chart, format_report],
    # TODO: 設定を完成させる
)

# TODO: 3つのエージェントを統合するコーディネーターを作成
```

### 上級レベル演習

#### 演習6: リアルタイムシステム
```python
# 課題: リアルタイムチャットボット
import asyncio
import websockets

class RealTimeChatbot:
    def __init__(self, agent):
        self.agent = agent
        
    async def handle_websocket(self, websocket, path):
        """WebSocket接続を処理"""
        # TODO: リアルタイムメッセージ処理を実装
        pass
        
    async def start_server(self, host="localhost", port=8765):
        """WebSocketサーバー開始"""
        # TODO: サーバー実装
        pass
```

#### 演習7: セキュアなコード実行
```python
# 課題: 安全なコード実行環境
import subprocess
import tempfile

class SecureCodeRunner:
    def __init__(self):
        self.allowed_imports = ["math", "json", "datetime"]
        
    def execute_python_safely(self, code: str) -> dict:
        """セキュアなPythonコード実行"""
        # TODO: コードの安全性をチェック
        # TODO: 制限された環境で実行
        # TODO: タイムアウト処理
        pass
```

---

## 🔍 理解度確認テスト

### 基礎知識テスト

#### Q1: ツール開発基礎
```
以下のツール関数の問題点を指摘し、修正してください：

def bad_tool(input_data):
    result = process_data(input_data)
    return result
```

**期待する回答要素**:
- [ ] 型ヒントが不足している
- [ ] docstring が不足している  
- [ ] ToolContext パラメータが不足している
- [ ] エラーハンドリングが不足している

#### Q2: 状態管理
```
ToolContextを使用した状態管理で、以下のコードの問題点は何ですか？

def count_calls(tool_context: ToolContext) -> int:
    tool_context.state['count'] += 1
    return tool_context.state['count']
```

**期待する回答要素**:
- [ ] 初期化チェックが不足している
- [ ] KeyError の可能性がある
- [ ] 適切な初期化処理を含める必要がある

#### Q3: プロバイダー選択
```
以下の状況で最適なLLMプロバイダーを選択し、理由を説明してください：

シナリオ1: 大量のデータ分析レポートを高速生成
シナリオ2: 創作的な文章作成を高品質で実行
シナリオ3: コスト重視でシンプルな質問応答
```

### 統合技術テスト

#### Q4: OAuth2認証フロー
OAuth2 認証を使用したGoogle Calendar統合で必要な手順を順序立てて説明してください。

**期待する回答要素**:
- [ ] クライアントID/シークレットの取得
- [ ] 認証URLの生成とリダイレクト  
- [ ] 認証コードの取得
- [ ] アクセストークンの取得
- [ ] APIリクエストでのトークン使用

#### Q5: ワークフロー設計
以下の要件を満たすシーケンシャルワークフローを設計してください：
- データの収集→前処理→分析→レポート生成
- 各ステップでエラーが発生した場合の処理
- 中間結果の保存と引き継ぎ

### 高度技術テスト

#### Q6: MCP プロトコル
MCP (Model Context Protocol) の3つの主要な通信方式（SSE, STDIO, HTTP）の特徴と適用場面を説明してください。

#### Q7: リアルタイム処理
双方向ストリーミングシステムで考慮すべき技術的課題を5つ挙げ、それぞれの解決アプローチを説明してください。

---

## 🚨 よくある問題とトラブルシューティング

### セットアップ関連の問題

#### 問題1: 依存関係のインストールエラー
```
ERROR: Failed building wheel for some-package
```

**解決方法**:
```bash
# システムの依存関係を更新
sudo apt-get update && sudo apt-get install build-essential
# または macOS の場合
xcode-select --install

# Python バージョンを確認
python --version  # 3.11+ が必要

# uv の更新
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 問題2: API キーの認証エラー
```
AuthenticationError: Invalid API key
```

**解決方法**:
```bash
# 環境変数の確認
echo $GOOGLE_API_KEY
echo $ANTHROPIC_API_KEY

# .env ファイルの確認
cat .env

# 環境変数の再読み込み
source .env
# または
export GOOGLE_API_KEY=your_actual_key
```

### 実行時の問題

#### 問題3: モジュールが見つからないエラー
```
ModuleNotFoundError: No module named 'google.adk'
```

**解決方法**:
```bash
# 仮想環境がアクティブか確認
which python  # .venv/bin/python を指すはず

# 仮想環境の再アクティベート
source .venv/bin/activate

# ADK の再インストール
uv sync --all-extras
```

#### 問題4: ツールの実行エラー
```
ToolError: Tool execution failed
```

**デバッグ手順**:
```python
# ログレベルを上げる
import logging
logging.basicConfig(level=logging.DEBUG)

# ツールを個別テスト
result = your_tool("test_input")
print(f"Tool result: {result}")

# エージェント実行時のコンテキストを確認
print(f"Tool context state: {tool_context.state}")
```

### パフォーマンス関連の問題

#### 問題5: レスポンス時間が遅い
**最適化手順**:
1. モデルの選択を確認（GPT-4 → GPT-3.5-turbo など）
2. プロンプトの長さを短縮
3. 並列処理の活用
4. キャッシング機能の実装

#### 問題6: メモリ使用量が多い
**対策方法**:
```python
# 大きなデータの適切な管理
def process_large_data(data_chunks, tool_context: ToolContext):
    results = []
    for chunk in data_chunks:
        result = process_chunk(chunk)
        results.append(result)
        # メモリ解放
        del chunk
    return results
```

### セキュリティ関連の問題

#### 問題7: 機密情報の露出
**予防策**:
```python
# 環境変数の適切な使用
import os
from dotenv import load_dotenv

load_dotenv()

# 直接ハードコーディングしない
# BAD: api_key = "your_secret_key"
# GOOD: api_key = os.getenv("API_KEY")

# ログに機密情報を含めない
def safe_log(message: str, sensitive_data: str):
    # 機密データをマスク
    masked_data = "*" * len(sensitive_data)
    logging.info(f"{message}: {masked_data}")
```

---

## 📊 学習成果評価シート

### スキル評価マトリックス

| スキル領域 | 初級 | 中級 | 上級 | エキスパート |
|------------|------|------|------|-------------|
| **カスタムツール開発** | ✅ 基本的なツール作成 | ✅ エラーハンドリング実装 | ✅ 複雑なツール設計 | ✅ フレームワーク級ツール |
| **状態管理** | ✅ ToolContext使用 | ✅ セッション状態管理 | ✅ 分散状態管理 | ✅ 高可用性状態管理 |
| **外部統合** | ✅ 基本API統合 | ✅ OAuth認証システム | ✅ 複雑なプロトコル統合 | ✅ エンタープライズ統合 |
| **ワークフロー** | ✅ 単純シーケンス | ✅ 条件分岐フロー | ✅ 並列実行制御 | ✅ 動的フロー生成 |
| **システム設計** | ✅ 単体エージェント | ✅ マルチエージェント | ✅ 分散システム | ✅ スケーラブル設計 |

### プロジェクト成果物チェックリスト

#### 基礎レベル成果物
- [ ] 独自のカスタムツールセット（5個以上のツール）
- [ ] エラーハンドリングを含む堅牢なツール実装
- [ ] 状態管理を活用したセッションツール
- [ ] マルチプロバイダー対応エージェント

#### 中級レベル成果物  
- [ ] Google サービス統合エージェント
- [ ] OAuth2 認証システム実装
- [ ] 複数ステップのワークフロー実装
- [ ] エンタープライズシステム統合例

#### 上級レベル成果物
- [ ] MCP プロトコル実装
- [ ] リアルタイムストリーミングシステム
- [ ] 人間協調ワークフロー
- [ ] 構造化出力システム

#### エキスパートレベル成果物
- [ ] RAG システム実装
- [ ] 包括的監視・テレメトリシステム  
- [ ] 特殊用途システム（トリアージなど）
- [ ] フレームワーク統合システム

### 学習時間記録テンプレート

```
日付: ____
学習エージェント: ____
学習時間: ____時間
学習内容:
- 理論学習: ____
- 実践演習: ____
- 問題解決: ____

理解度（1-5）: ____
課題・質問:
____

次回の目標:
____
```

---

## 🎯 学習完了認定基準

### 基礎パス完了認定
以下の全項目を満たすことで基礎パス完了とします：

✅ **知識習得**:
- [ ] カスタムツール開発パターンを説明できる
- [ ] 状態管理の仕組みを理解している
- [ ] 複数プロバイダーの特徴を理解している
- [ ] マルチエージェントの基本概念を理解している

✅ **実装スキル**:
- [ ] 独自のツールを5個以上作成できる
- [ ] エラーハンドリングを適切に実装できる
- [ ] 異なるLLMプロバイダーを使い分けできる
- [ ] 簡単なマルチエージェントシステムを構築できる

✅ **成果物**:
- [ ] オリジナルのカスタムツールセット
- [ ] プロバイダー比較システム
- [ ] 状態管理デモアプリケーション

### 統合パス完了認定

✅ **知識習得**:
- [ ] Google Cloud サービス統合を理解している
- [ ] OAuth2 認証フローを説明できる
- [ ] ワークフロー設計原則を理解している
- [ ] エンタープライズ統合の課題を理解している

✅ **実装スキル**:
- [ ] BigQuery 統合システムを構築できる
- [ ] OAuth2 認証アプリケーションを実装できる
- [ ] 複雑なワークフローを設計・実装できる
- [ ] 外部システムとの統合を実現できる

✅ **成果物**:
- [ ] データ分析エージェントシステム
- [ ] 認証機能付きアプリケーション
- [ ] エンタープライズ統合デモ

### 高度パス完了認定

✅ **知識習得**:
- [ ] MCP プロトコルの仕組みを理解している
- [ ] リアルタイム処理の実装方法を理解している
- [ ] 人間協調システムの設計を理解している
- [ ] 構造化出力の重要性を理解している

✅ **実装スキル**:
- [ ] MCP サーバーを実装できる
- [ ] リアルタイム双方向通信を実装できる
- [ ] 人間承認ワークフローを設計できる
- [ ] 複雑な構造化出力を実装できる

✅ **成果物**:
- [ ] カスタム MCP プロトコル実装
- [ ] リアルタイム処理システム
- [ ] 人間協調ワークフローデモ

### 専門パス完了認定

✅ **知識習得**:
- [ ] LangChain 統合パターンを理解している
- [ ] RAG システムの設計原則を理解している
- [ ] システム監視の重要性を理解している
- [ ] 特殊用途システムの設計を理解している

✅ **実装スキル**:
- [ ] LangChain ツールを ADK で活用できる
- [ ] 独自の RAG システムを構築できる
- [ ] 包括的な監視システムを実装できる
- [ ] 特定業務に特化したシステムを設計できる

✅ **成果物**:
- [ ] ハイブリッド LangChain-ADK システム
- [ ] カスタム RAG 実装
- [ ] 包括的監視・テレメトリシステム

---

このツールキットを活用して、効率的かつ体系的に ADK の学習を進めてください。質問や問題が発生した場合は、このガイドのトラブルシューティングセクションを参照するか、GitHub Issues で質問してください。