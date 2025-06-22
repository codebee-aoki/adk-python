# Wikipedia人物アシスタント

Wikipedia MCPを使って、ユーザーの挨拶から人物検索まで幅広く対応するマルチエージェントシステムです。

## 概要

このエージェントは、ADKのマルチエージェント機能を活用して、3つの専門エージェントが連携動作する教育用サンプルです。Coordinatorエージェントがユーザーの質問を分析し、適切な専門エージェントに自動転送します。

## 特徴

- **マルチエージェント構造**: 3つの専門エージェントによる役割分担
- **自動ルーティング**: Coordinatorによる質問内容の自動判別と転送
- **Wikipedia MCP**: 日本語Wikipediaから実際の人物情報を取得
- **教育的価値**: ADKのマルチエージェントパターンの学習に最適

## 前提条件

### 環境要件
- Python 3.9以上
- Google ADK Python SDK
- wikipedia-mcp パッケージ

### セットアップ

1. **wikipedia-mcpのインストール**
```bash
pip install wikipedia-mcp google-adk==1.4.2
```

2. **依存関係の確認**
```bash
# ADKの環境が正しく設定されていることを確認
cd /path/to/adk-python
uv sync --all-extras
```

3. **Wikipedia MCPサーバーの動作確認**
```bash
# 日本語Wikipedia MCPサーバーをテスト起動
wikipedia-mcp --language ja
```

## 使用方法

### 基本的な実行

```bash
# プロジェクトルートから実行
cd /path/to/adk-python
python contributing/samples/wikipedia_person_assistant/main.py
```

### ADK Web UIでの実行

```bash
# ADK Web UIを起動
adk web contributing/samples/wikipedia_person_assistant/

# ブラウザでhttp://localhost:8080にアクセス
```

### 実行例

**例1: 挨拶と機能案内（Greeterエージェント）**
```
> こんにちは

[Greeter]
こんにちは！いつもお疲れ様です。
私は歴史上の人物についての情報をお調べするお手伝いをしています。

例えば：
- 「夏目漱石について教えて」
- 「江戸時代の画家について知りたい」
- 「現代音楽で有名な人について」

どなたについて知りたいことがありますか？
```

**例2: 具体的な人物検索（WikipediaPersonAssistantエージェント）**
```
> 夏目漱石について教えて

[WikipediaPersonAssistant]
夏目漱石は、1867年2月9日に生まれ、1916年12月9日に亡くなった日本の小説家、英文学者です。
本名は夏目金之助。明治末期から大正初期にかけて活躍し、今日に通用する言文一致の現代書き言葉を作った
近代日本文学の文豪の一人です。代表作には『吾輩は猫である』『坊っちゃん』『三四郎』『それから』
『こゝろ』『明暗』などがあります。
```

**例3: 曖昧な質問（WikipediaPersonAssistantエージェント）**
```
> 江戸時代の画家について知りたい

[WikipediaPersonAssistant]
【検索結果】候補リスト
1. 葛飾北斎 - 浮世絵師、富嶽三十六景で有名
2. 歌川広重 - 風景画で知られる浮世絵師
3. 円山応挙 - 写実的な絵画で知られる

複数の候補が見つかりました。具体的な人物名を教えてください。
```

## エージェント構成

### 1. Coordinator（調整エージェント）
- **役割**: ユーザーの質問を分析して適切なエージェントに転送
- **機能**: 
  - 質問内容の自動分類（人物関連 vs 一般質問）
  - 適切なエージェントへの自動転送
  - マルチエージェント全体の制御
- **ツール**: なし（転送専用）

### 2. Greeter（挨拶エージェント）
- **役割**: 挨拶・一般会話・システム質問への対応
- **機能**: 
  - 親しみやすい挨拶応答
  - システム機能の案内
  - 人物検索機能への誘導
- **ツール**: なし（会話専用）

### 3. WikipediaPersonAssistant（人物検索エージェント）
- **役割**: 人物に関する詳細情報の検索・提供
- **機能**: 
  - Wikipedia検索による人物情報取得
  - 詳細な人物要約の作成
  - 曖昧な質問での候補リスト表示
- **ツール**: Wikipedia MCP (search_wikipedia, get_summary, get_article)

## マルチエージェントの動作フロー

```
ユーザー入力
    ↓
[Coordinator] 質問を分析
    ↓
人物関連？ ─Yes→ [WikipediaPersonAssistant] → Wikipedia検索 → 詳細応答
    ↓
   No
    ↓
[Greeter] → 親しみやすい応答・機能案内
```

- **明確な役割分担**: 各エージェントが専門分野に特化
- **自動ルーティング**: Coordinatorによる適切な転送
- **教育的価値**: ADKのマルチエージェントパターンを学習

## トラブルシューティング

### よくある問題

1. **Wikipedia MCPに接続できない**
```bash
# MCPサーバーが起動しているか確認
wikipedia-mcp --language ja

# ポートが使用されていないか確認
lsof -i :PORT_NUMBER
```

2. **検索結果が表示されない**
- インターネット接続を確認
- 検索キーワードを変更してみる
- 日本語Wikipedia以外の記事は表示されません

3. **エージェントが応答しない**
- Google API Keyが正しく設定されているか確認
- Wikipedia MCPサーバーとの接続を確認

### ログ確認

```bash
# ADKのログレベルを設定
export ADK_LOG_LEVEL=DEBUG
python -m contributing.samples.wikipedia_person_assistant.main
```

## カスタマイズ

### 検索対象の拡張
```python
# agent.pyのtool_filterを変更
tool_filter=[
    'search_wikipedia',
    'get_article', 
    'get_summary',
    'get_sections',        # 追加: 記事セクション取得
    'get_related_topics',  # 追加: 関連トピック
]
```

### 応答内容のカスタマイズ
```python
# agent.pyのinstructionを変更
instruction="""あなたは挨拶と人物検索の両方に対応するアシスタントです。
（ここで応答スタイルやトーンを調整）
"""
```

### モデルの変更
```python
wikipedia_person_assistant = LlmAgent(
    name="WikipediaPersonAssistant",
    model="gemini-1.5-pro",  # より高性能なモデルに変更
    # ...
)
```

## 学習ポイント

このサンプルを通して以下を学ぶことができます：

1. **マルチエージェント設計**
   - Coordinatorパターンの実装
   - エージェント間の役割分担
   - sub_agentsによる階層構造

2. **自動ルーティング**
   - 質問内容の自動分類ロジック
   - 適切なエージェントへの転送
   - 日本語での条件判定

3. **MCP統合**
   - 外部ツールの統合方法
   - tool_filterによる機能制限
   - 接続パラメータの設定

4. **専門エージェントの設計**
   - 単一機能に特化したエージェント
   - 各エージェントの独立性
   - 明確なinstruction設計

5. **実用的なアシスタント設計**
   - 挨拶から専門機能まで一貫対応
   - モジュラーで拡張しやすい構造
   - メンテナンスしやすい実装

## 関連資料

- [ADK Multi-Agent公式ドキュメント](https://google.github.io/adk-docs/agents/llm-agents/)
- [Wikipedia MCP GitHub](https://github.com/Rudra-ravi/wikipedia-mcp)
- [ADK開発ガイド](../../README.md)
- [マルチエージェントパターン](https://google.github.io/adk-docs/patterns/multi-agent/)