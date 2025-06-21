# RAG エージェント - 技術ドキュメント

## 概要

RAG エージェント（`rag_agent`）は、Retrieval-Augmented Generation（検索拡張生成）技術を活用したエージェントです。Vertex AI RAG を使用して専門的な文書コーパスから関連情報を検索し、正確で文脈に即した回答を生成します。企業の知識ベースや技術文書を活用した質問応答システムの実装パターンを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# RAG 対応エージェント
root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="root_agent",
    instruction="You are an AI assistant with access to specialized corpus of documents...",
    tools=[ask_vertex_retrieval],  # Vertex AI RAG 検索ツール
)
```

### 主要コンポーネント

#### 1. Vertex AI RAG 検索ツール
```python
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

ask_vertex_retrieval = VertexAiRagRetrieval(
    name="retrieve_rag_documentation",
    description="Use this tool to retrieve documentation and reference materials...",
    rag_resources=[
        rag.RagResource(
            rag_corpus=os.environ.get("RAG_CORPUS"),  # RAG コーパス ID
        )
    ],
    similarity_top_k=1,                    # 類似度上位 K 件
    vector_distance_threshold=0.6,         # ベクトル距離閾値
)
```

#### 2. 環境設定
```python
from dotenv import load_dotenv
import os

load_dotenv()

# RAG コーパス ID の設定
# 例: projects/123/locations/us-central1/ragCorpora/456
RAG_CORPUS = os.environ.get("RAG_CORPUS")
```

## RAG システム概要

### 1. Retrieval-Augmented Generation の仕組み

**基本フロー**:
```text
User Query
↓
1. クエリのベクトル化
↓
2. 文書コーパスからの類似検索
↓
3. 関連文書の取得
↓
4. 文書 + クエリをLLMに送信
↓
5. 文脈に基づく回答生成
```

### 2. Vertex AI RAG の特徴

**コーパス管理**:
- 文書の自動インデックス化
- ベクトル埋め込みの生成
- メタデータベースの検索フィルタリング

**検索パフォーマンス**:
- 高速なベクトル類似度検索
- スケーラブルな検索インフラ
- リアルタイム検索結果

## 設定パラメータ

### 1. 検索設定

**類似度設定**:
```python
similarity_top_k=1                    # 上位1件の関連文書を取得
vector_distance_threshold=0.6         # 距離閾値（0.0-1.0）
```

**距離閾値の考慮事項**:
- `0.0`: 完全一致のみ
- `0.3-0.5`: 高い類似性
- `0.6-0.8`: 中程度の類似性
- `0.9-1.0`: 低い類似性も含める

### 2. コーパス設定

**RAG コーパス例**:
```bash
# 環境変数設定
export RAG_CORPUS="projects/my-project/locations/us-central1/ragCorpora/my-corpus"
```

**複数コーパスの設定**:
```python
rag_resources=[
    rag.RagResource(rag_corpus="projects/.../ragCorpora/technical-docs"),
    rag.RagResource(rag_corpus="projects/.../ragCorpora/user-manuals"),
    rag.RagResource(rag_corpus="projects/.../ragCorpora/api-references"),
]
```

## 実行例

### 基本的な質問応答

**技術文書からの情報検索**:
```python
response = await root_agent.invoke("ADK フレームワークでエージェントを作成する方法を教えてください")

# 実行フロー:
# 1. ask_vertex_retrieval ツール呼び出し
# 2. "ADK エージェント作成" 関連文書の検索
# 3. 上位1件の関連文書を取得
# 4. 文書内容 + 質問をLLMに送信
# 5. 文書に基づく詳細回答の生成
```

**API 使用方法の確認**:
```python
response = await root_agent.invoke("BigQuery ツールの使用方法と認証設定について詳しく説明してください")

# RAG システムが:
# 1. BigQuery 関連の技術文書を検索
# 2. 認証設定の具体例を含む文書を特定
# 3. 正確で実用的な回答を生成
```

### 高度な質問パターン

**比較・分析クエリ**:
```python
response = await root_agent.invoke("LlmAgent と SequentialAgent の違いと使い分けについて教えてください")

# RAG が複数文書から情報を統合:
# 1. LlmAgent の仕様文書
# 2. SequentialAgent の仕様文書  
# 3. 比較表や使用例
# 4. 総合的な比較分析を提供
```

**トラブルシューティング**:
```python
response = await root_agent.invoke("MCP 接続でタイムアウトエラーが発生する場合の対処法は？")

# 専門知識に基づく解決策:
# 1. トラブルシューティングガイドから検索
# 2. 具体的なエラー対処法
# 3. 設定例とベストプラクティス
```

## 高度な実装例

### 1. 多言語対応RAGシステム

```python
class MultiLanguageRAGAgent:
    def __init__(self):
        self.language_corpora = {
            'ja': VertexAiRagRetrieval(
                rag_resources=[rag.RagResource(rag_corpus=JP_CORPUS)],
                similarity_top_k=3,
            ),
            'en': VertexAiRagRetrieval(
                rag_resources=[rag.RagResource(rag_corpus=EN_CORPUS)],
                similarity_top_k=3,
            ),
        }
    
    async def query_with_language_detection(self, query: str):
        """言語検出とコーパス選択"""
        detected_language = await self.detect_language(query)
        rag_tool = self.language_corpora.get(detected_language, self.language_corpora['en'])
        
        return await self.agent_with_tool(rag_tool).invoke(query)
```

### 2. ドメイン特化RAGシステム

```python
class DomainSpecificRAG:
    def __init__(self):
        self.domain_agents = {
            'technical': self.create_technical_agent(),
            'business': self.create_business_agent(),
            'legal': self.create_legal_agent(),
        }
    
    def create_technical_agent(self):
        technical_rag = VertexAiRagRetrieval(
            name="technical_retrieval",
            rag_resources=[rag.RagResource(rag_corpus=TECHNICAL_CORPUS)],
            similarity_top_k=2,
            vector_distance_threshold=0.5,  # 高精度検索
        )
        
        return Agent(
            model="gemini-2.0-flash-001",
            instruction="You are a technical expert. Provide detailed technical answers...",
            tools=[technical_rag],
        )
    
    async def route_query(self, query: str):
        """クエリドメインの判定とルーティング"""
        domain = await self.classify_domain(query)
        agent = self.domain_agents.get(domain, self.domain_agents['technical'])
        
        return await agent.invoke(query)
```

### 3. 階層型RAGシステム

```python
class HierarchicalRAG:
    def __init__(self):
        # レベル1: 概要検索
        self.overview_rag = VertexAiRagRetrieval(
            rag_resources=[rag.RagResource(rag_corpus=OVERVIEW_CORPUS)],
            similarity_top_k=1,
            vector_distance_threshold=0.7,
        )
        
        # レベル2: 詳細検索
        self.detailed_rag = VertexAiRagRetrieval(
            rag_resources=[rag.RagResource(rag_corpus=DETAILED_CORPUS)],
            similarity_top_k=3,
            vector_distance_threshold=0.5,
        )
    
    async def hierarchical_search(self, query: str):
        """階層的検索"""
        # 1. 概要レベルで関連トピック特定
        overview_result = await self.overview_agent.invoke(query)
        
        # 2. 詳細情報が必要かどうか判定
        if self.needs_detailed_info(overview_result, query):
            detailed_result = await self.detailed_agent.invoke(query)
            return self.combine_results(overview_result, detailed_result)
        
        return overview_result
```

## コーパス管理とメンテナンス

### 1. 文書の更新管理

```python
class CorpusManager:
    async def update_corpus(self, new_documents: list[str]):
        """コーパスの更新"""
        for doc_path in new_documents:
            # 文書のアップロード
            await self.upload_document(doc_path)
            
            # インデックスの更新
            await self.reindex_corpus()
    
    async def validate_corpus_quality(self):
        """コーパス品質の検証"""
        test_queries = [
            "基本的な使用方法",
            "トラブルシューティング",
            "API リファレンス",
        ]
        
        quality_scores = []
        for query in test_queries:
            results = await self.test_search_quality(query)
            quality_scores.append(results['relevance_score'])
        
        return sum(quality_scores) / len(quality_scores)
```

### 2. 検索品質の監視

```python
class RAGMonitoring:
    def __init__(self):
        self.search_logs = []
        self.relevance_feedback = {}
    
    async def log_search_interaction(self, query: str, results: list, user_satisfaction: float):
        """検索インタラクションのログ"""
        self.search_logs.append({
            'query': query,
            'results': results,
            'satisfaction': user_satisfaction,
            'timestamp': datetime.now(),
        })
    
    async def analyze_search_patterns(self):
        """検索パターンの分析"""
        # 低満足度クエリの特定
        low_satisfaction_queries = [
            log for log in self.search_logs 
            if log['satisfaction'] < 0.6
        ]
        
        # 改善提案の生成
        improvements = await self.generate_improvements(low_satisfaction_queries)
        return improvements
```

## パフォーマンス最適化

### 1. キャッシュ戦略

```python
class RAGCache:
    def __init__(self, cache_size: int = 1000, ttl: int = 3600):
        self.query_cache = {}
        self.cache_size = cache_size
        self.ttl = ttl
    
    async def cached_search(self, query: str):
        """キャッシュ付き検索"""
        query_hash = hash(query)
        
        # キャッシュヒット確認
        if query_hash in self.query_cache:
            cached_result, timestamp = self.query_cache[query_hash]
            if time.time() - timestamp < self.ttl:
                return cached_result
        
        # キャッシュミス: 実際の検索実行
        result = await self.rag_tool.search(query)
        
        # キャッシュ保存
        self.save_to_cache(query_hash, result)
        return result
```

### 2. バッチ検索

```python
class BatchRAGProcessor:
    async def batch_search(self, queries: list[str]):
        """バッチ検索処理"""
        # 類似クエリのグループ化
        query_groups = self.group_similar_queries(queries)
        
        results = {}
        for group in query_groups:
            # 代表クエリで検索
            representative_query = group[0]
            search_result = await self.rag_tool.search(representative_query)
            
            # グループ内の全クエリに結果を適用
            for query in group:
                results[query] = self.adapt_result_for_query(search_result, query)
        
        return results
```

## エラーハンドリング

### 1. 検索失敗時の対応

```python
async def robust_rag_search(query: str, max_retries: int = 3):
    """ロバストな RAG 検索"""
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            result = await ask_vertex_retrieval.search(query)
            
            if result and len(result.documents) > 0:
                return result
            else:
                # 検索結果なし: クエリを言い換えて再試行
                reformulated_query = await reformulate_query(query)
                query = reformulated_query
                retry_count += 1
        
        except Exception as e:
            if "quota_exceeded" in str(e):
                # クォータ超過: 待機して再試行
                await asyncio.sleep(60)
            elif "not_found" in str(e):
                # コーパス不存在: エラー報告
                raise RAGCorpusNotFoundError(f"Corpus not found: {RAG_CORPUS}")
            
            retry_count += 1
    
    # 最大リトライ後も失敗
    return await fallback_response(query)
```

### 2. 品質フィルタリング

```python
def filter_low_quality_results(search_results: list, min_score: float = 0.6):
    """低品質結果のフィルタリング"""
    filtered_results = []
    
    for result in search_results:
        if result.relevance_score >= min_score:
            filtered_results.append(result)
    
    # 結果が少ない場合は閾値を下げて再試行
    if len(filtered_results) == 0 and min_score > 0.3:
        return filter_low_quality_results(search_results, min_score - 0.1)
    
    return filtered_results
```

## セキュリティとプライバシー

### 1. アクセス制御

```python
class SecureRAGAgent:
    def __init__(self, user_permissions: dict):
        self.user_permissions = user_permissions
        self.access_controlled_corpora = {
            'public': PUBLIC_CORPUS,
            'internal': INTERNAL_CORPUS,
            'confidential': CONFIDENTIAL_CORPUS,
        }
    
    async def secure_search(self, query: str, user_id: str):
        """アクセス制御付き検索"""
        user_level = self.user_permissions.get(user_id, 'public')
        
        # ユーザーの権限レベルに応じたコーパス選択
        available_corpora = self.get_accessible_corpora(user_level)
        
        # 制限されたコーパスで検索実行
        rag_tool = VertexAiRagRetrieval(
            rag_resources=[rag.RagResource(corpus) for corpus in available_corpora]
        )
        
        return await rag_tool.search(query)
```

### 2. 機密情報の除去

```python
class PrivacyPreservingRAG:
    def __init__(self):
        self.sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
        ]
    
    def sanitize_response(self, response: str) -> str:
        """機密情報の除去"""
        sanitized = response
        
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `.env`: 環境変数設定（RAG_CORPUS）

## 依存関係

- `google.adk.agents`: ADK エージェント基底クラス
- `google.adk.tools.retrieval.vertex_ai_rag_retrieval`: Vertex AI RAG 検索ツール
- `vertexai.preview.rag`: Vertex AI RAG プレビュー API
- `dotenv`: 環境変数管理
- **Vertex AI RAG**: Google Cloud の RAG サービス
- **RAG コーパス**: 検索対象となる文書コレクション