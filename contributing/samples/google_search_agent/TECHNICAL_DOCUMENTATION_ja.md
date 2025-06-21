# google_search_agent - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`google_search_agent` エージェントは、ADK で Google Search API を使用してウェブ検索機能を提供するサンプル実装です。リアルタイムの情報検索と AI による結果分析を組み合わせ、検索ベースの AI アシスタントの基本パターンを示します。

### 主要機能
- **Google Search 実行**: プログラマティックなウェブ検索
- **検索結果分析**: AI による検索結果の解釈と要約
- **リアルタイム情報**: 最新のウェブ情報へのアクセス
- **質問応答**: 検索結果を基にした知識ベースの回答

### 対象ユースケース
- リアルタイム情報検索 AI エージェント
- 研究・調査支援システム
- 情報収集の自動化
- ファクトチェック機能の実装

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー質問] 
    ↓ (情報検索要求)
[root_agent] 
    ↓ (google_search ツール呼び出し)
[Google Search API]
    ↓ (検索実行)
[Web検索結果]
    ↓ (結果取得)
[ADK google_search ツール]
    ↓ (構造化データ)
[Gemini 2.0 Flash]
    ↓ (結果分析・要約)
[AI による回答生成]
```

### 検索フロー
1. ユーザーが質問や検索要求を入力
2. エージェントが適切な検索クエリを生成
3. `google_search` ツールが Google Search API を呼び出し
4. 検索結果（タイトル、URL、スニペット）を取得
5. AI が結果を分析し、質問に対する適切な回答を生成

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス)
- **検索ツール**: `google_search` - Google Search API 統合
- **LLM モデル**: Gemini 2.0 Flash - 結果分析と回答生成
- **Google GenAI Client**: Vertex AI 連携用クライアント

### 依存関係
```python
# ADK コンポーネント
from google.adk import Agent
from google.adk.tools import google_search

# Google GenAI クライアント
from google.genai import Client
```

## 3. コード詳細解説

### 3.1 Google Search ツールの統合

```python
from google.adk.tools import google_search

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description="""an agent whose job it is to perform Google search queries and answer questions about the results.""",
    instruction="""You are an agent whose job is to perform Google search queries and answer questions about the results.
""",
    tools=[google_search],
)
```

**重要な実装ポイント:**

#### 1. シンプルな統合
- `google_search` ツールをインポートして直接使用
- 複雑な設定や認証設定が不要
- ADK に統合済みの検索機能

#### 2. 明確な役割定義
- 検索実行と結果分析に特化
- 検索ベースの質問応答システム
- リアルタイム情報へのアクセス

### 3.2 Google GenAI クライアント

```python
# Only Vertex AI supports image generation for now.
client = Client()
```

**用途:**
- Vertex AI との連携準備
- 将来的な画像生成機能への対応
- Google Cloud サービスとの統合基盤

### 3.3 エージェント設定の特徴

#### モデル選択
```python
model='gemini-2.0-flash-001'
```
- 最新の Gemini 2.0 Flash モデル
- 高速な応答性能
- ウェブ検索結果の効率的な処理

#### 指示の設計
```python
description="""an agent whose job it is to perform Google search queries and answer questions about the results."""
instruction="""You are an agent whose job is to perform Google search queries and answer questions about the results."""
```
- シンプルで明確な役割定義
- 検索と分析の両方を担当
- 柔軟な質問対応

## 4. 設定・環境構築

### 4.1 Google Search API の設定

#### Custom Search Engine の作成
1. [Google Custom Search Engine](https://cse.google.com/cse/) にアクセス
2. 新しい検索エンジンを作成
3. 検索対象を「ウェブ全体」に設定
4. Search Engine ID (CX) を取得

#### API キーの取得
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. APIs & Services > Credentials に移動
3. Custom Search API を有効化
4. API キーを作成

### 4.2 必要な環境変数

```bash
# .env ファイルまたは環境変数
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id

# または
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_custom_search_engine_id
```

### 4.3 依存関係とインストール

```bash
# 基本インストール
pip install google-adk

# Google Search 用の追加依存関係
pip install google-api-python-client
```

### 4.4 実行方法

```bash
# CLI での実行
adk run contributing/samples/google_search_agent

# Web UI での実行
adk web contributing/samples/google_search_agent
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### 一般的な情報検索
```
ユーザー: "What is the latest news about artificial intelligence?"
エージェント: [Google Search 実行] 
"Based on recent search results, here are the latest AI developments: ..."
```

#### 特定事実の確認
```
ユーザー: "When was GPT-4 released?"
エージェント: [検索で最新情報を確認]
"According to recent sources, GPT-4 was released on March 14, 2023..."
```

#### 比較情報の収集
```
ユーザー: "Compare the features of iPhone 15 and Samsung Galaxy S24"
エージェント: [複数検索で情報収集]
"Based on search results, here's a comparison: ..."
```

### 5.2 高度な検索パターン

#### 複数検索クエリの組み合わせ
```python
def create_research_agent():
    return Agent(
        model='gemini-2.0-flash-001',
        name='research_agent',
        instruction="""
        You are a research specialist. When answering questions:
        1. Perform multiple targeted searches if needed
        2. Cross-reference information from different sources
        3. Identify potential contradictions in search results
        4. Provide source URLs for verification
        5. Indicate the freshness of information
        """,
        tools=[google_search],
    )
```

#### ドメイン固有の検索
```python
def create_domain_specific_agent(domain: str):
    return Agent(
        model='gemini-2.0-flash-001',
        name=f'{domain}_search_agent',
        instruction=f"""
        You are specialized in searching for {domain}-related information.
        Always include relevant domain-specific terms in your searches.
        Focus on authoritative sources in the {domain} field.
        """,
        tools=[google_search],
    )

# 使用例
tech_agent = create_domain_specific_agent("technology")
medical_agent = create_domain_specific_agent("medical research")
```

### 5.3 検索結果の処理強化

#### ソース信頼性の評価
```python
def create_fact_checking_agent():
    return Agent(
        model='gemini-2.0-flash-001',
        name='fact_checker',
        instruction="""
        You are a fact-checking specialist. When providing information:
        1. Evaluate the credibility of sources
        2. Look for multiple sources confirming the same information
        3. Flag potential misinformation or unverified claims
        4. Provide confidence levels for your findings
        5. Always include source URLs
        """,
        tools=[google_search],
    )
```

#### 時系列情報の管理
```python
def create_timeline_agent():
    return Agent(
        model='gemini-2.0-flash-001',
        name='timeline_agent',
        instruction="""
        You specialize in creating timelines and tracking changes over time.
        When searching:
        1. Include date-specific terms in searches
        2. Look for historical context
        3. Track how information has evolved
        4. Create chronological summaries
        """,
        tools=[google_search],
    )
```

### 5.4 マルチモーダル拡張

#### 画像検索との組み合わせ
```python
# 将来的な拡張例（現在は Vertex AI のみサポート）
def create_multimodal_search_agent():
    return Agent(
        model='gemini-2.0-flash-001',
        name='multimodal_agent',
        instruction="""
        You can search for both text and images.
        When appropriate, suggest visual content to support your answers.
        """,
        tools=[
            google_search,
            # 将来的に画像検索ツールも追加
        ],
    )
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "Google Search API key not found"
**原因**: API キーが設定されていない
**解決法**: 環境変数の確認と設定
```bash
# 環境変数の確認
echo $GOOGLE_API_KEY
echo $GOOGLE_CSE_ID

# .env ファイルでの設定
cat >> .env << EOF
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CSE_ID=your_cse_id_here
EOF
```

#### エラー: "Custom Search API not enabled"
**原因**: Custom Search API が有効化されていない
**解決法**: Google Cloud Console での API 有効化
```bash
# gcloud CLI を使用した場合
gcloud services enable customsearch.googleapis.com
```

#### エラー: "Daily quota exceeded"
**原因**: 1日の検索クォータ制限に達した
**解決法**: クォータ管理とエラーハンドリング
```python
def create_quota_aware_agent():
    return Agent(
        instruction="""
        When performing searches, be mindful of API quotas.
        If you encounter quota errors:
        1. Inform the user about the limitation
        2. Suggest alternative approaches
        3. Prioritize the most important searches
        """,
        tools=[google_search],
    )
```

### 6.2 検索品質の向上

#### 検索クエリの最適化
```python
def create_optimized_search_agent():
    return Agent(
        instruction="""
        To improve search quality:
        1. Use specific and relevant keywords
        2. Include quotation marks for exact phrases
        3. Use site: operator for specific domains
        4. Add date ranges when needed (after:2023)
        5. Exclude irrelevant terms with minus operator
        """,
        tools=[google_search],
    )
```

#### 結果の信頼性評価
```python
def create_reliable_search_agent():
    return Agent(
        instruction="""
        Evaluate search results for reliability:
        1. Prefer authoritative sources (.edu, .gov, established publications)
        2. Check publication dates for currency
        3. Look for author credentials
        4. Cross-reference with multiple sources
        5. Be cautious of promotional or biased content
        """,
        tools=[google_search],
    )
```

### 6.3 パフォーマンス最適化

#### 検索効率の改善
```python
def create_efficient_search_agent():
    return Agent(
        instruction="""
        Optimize search efficiency:
        1. Start with broad searches, then narrow down
        2. Use previous search results to inform new queries
        3. Avoid redundant searches
        4. Summarize findings before additional searches
        """,
        tools=[google_search],
    )
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### 外部API統合の基本
- ADK ツールシステムによる API 統合
- シンプルな設定での外部サービス利用
- エラーハンドリングとフォールバック戦略

#### 情報検索エージェントの設計
```python
class InformationRetrievalAgent:
    def __init__(self):
        self.search_strategies = {
            "factual": "Focus on authoritative sources and recent information",
            "comparative": "Search for multiple perspectives and comparisons",
            "historical": "Include timeline and evolution of topics",
            "technical": "Focus on detailed specifications and expert sources"
        }
    
    def create_specialized_agent(self, strategy: str):
        instruction = f"""
        You are an information retrieval specialist.
        Strategy: {self.search_strategies[strategy]}
        Always provide source attribution and confidence levels.
        """
        return Agent(
            model='gemini-2.0-flash-001',
            instruction=instruction,
            tools=[google_search],
        )
```

### 7.2 情報の品質管理

#### ソース多様性の確保
```python
def create_diverse_search_agent():
    return Agent(
        instruction="""
        Ensure information diversity:
        1. Search for information from different types of sources
        2. Include academic, news, and industry perspectives
        3. Consider geographic and cultural diversity
        4. Balance recent and historical information
        """,
        tools=[google_search],
    )
```

#### バイアス対策
```python
def create_bias_aware_agent():
    return Agent(
        instruction="""
        Be aware of potential biases:
        1. Acknowledge limitations of search results
        2. Identify potential source biases
        3. Present multiple viewpoints when available
        4. Distinguish between facts and opinions
        """,
        tools=[google_search],
    )
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **API クォータ管理**: 1日の検索制限を考慮した設計
- **ソース検証**: 信頼できるソースの優先的使用
- **情報の鮮度**: 最新情報の重要性を考慮
- **エラーハンドリング**: 検索失敗時の適切な対応

#### 注意点
- **情報の正確性**: 検索結果の検証責任
- **著作権**: 検索結果の適切な引用
- **プライバシー**: ユーザーの検索履歴管理
- **コスト管理**: API 使用料の監視

### 7.4 他のプロジェクトへの応用

#### 研究支援システム
```python
class ResearchAssistant:
    def __init__(self):
        self.research_agent = Agent(
            model='gemini-2.0-flash-001',
            instruction="""
            You are a research assistant. For each research topic:
            1. Conduct comprehensive literature searches
            2. Identify key researchers and institutions
            3. Track recent developments and trends
            4. Provide structured research summaries
            """,
            tools=[google_search],
        )
```

#### ニュース分析システム
```python
class NewsAnalyzer:
    def __init__(self):
        self.news_agent = Agent(
            model='gemini-2.0-flash-001',
            instruction="""
            You are a news analyst. When analyzing topics:
            1. Search for latest news from multiple sources
            2. Identify trending themes and patterns
            3. Provide balanced perspective on controversial topics
            4. Track story development over time
            """,
            tools=[google_search],
        )
```

この google_search_agent エージェントは、リアルタイム情報検索機能を AI エージェントに統合する基本パターンを提供します。特に情報の鮮度と信頼性が重要な研究・調査支援システムの構築に有用なサンプルです。