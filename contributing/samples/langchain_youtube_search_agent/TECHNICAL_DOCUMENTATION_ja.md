# langchain_youtube_search_agent - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`langchain_youtube_search_agent` は、LangChain エコシステムとの統合パターンを学習するためのサンプルエージェントです。LangChain の YouTubeSearchTool を ADK のツールシステムにラップすることで、既存の LangChain ツールを ADK エージェントで活用する方法を示します。

### 主要機能
- **LangChain ツール統合**: 既存の LangChain ツールの再利用
- **YouTube 検索機能**: アーティスト名や楽曲での動画検索
- **フレームワーク間連携**: LangChain と ADK のハイブリッド活用
- **出力キー指定**: 結果を特定のキーで保存

### 対象ユースケース
- LangChain から ADK への移行学習
- 既存 LangChain ツールの活用
- フレームワーク統合パターンの理解
- 外部 Python ライブラリの統合方法

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (YouTube検索要求)
[langchain_youtube_search_agent] 
    ↓ (LangchainTool経由)
[ADK ツールラッパー]
    ↓ (LangChain Tool呼び出し)
[YouTubeSearchTool]
    ↓ (youtube_search ライブラリ)
[YouTube Search API (非公式)]
    ↓ (検索結果)
[YouTube 検索結果]
    ├── タイトル
    ├── URL
    ├── 再生時間
    └── チャンネル情報
```

### フレームワーク統合レイヤー
```
┌─────────────────────────────────────┐
│              ADK Layer              │
│  ┌─────────────────────────────────┐ │
│  │         LlmAgent                │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │      LangchainTool          │ │ │
│  │  │  ┌─────────────────────────┐ │ │ │
│  │  │  │   YouTubeSearchTool     │ │ │ │
│  │  │  │  (LangChain Community)  │ │ │ │
│  │  │  └─────────────────────────┘ │ │ │
│  │  └─────────────────────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (LlmAgent クラス)
- **ツールラッパー**: `LangchainTool` (ADK-LangChain ブリッジ)
- **LangChain ツール**: `YouTubeSearchTool` (LangChain Community)
- **外部ライブラリ**: `youtube_search` (Python パッケージ)

### 他のYouTube統合との比較
| 項目 | langchain_youtube_search_agent | 直接API統合 | カスタムツール |
|------|-------------------------------|------------|---------------|
| 実装複雑度 | 低（ラッパーのみ） | 高（API認証・管理） | 中（ライブラリ統合） |
| 機能豊富度 | 基本検索のみ | 高（全API機能） | カスタマイズ可能 |
| 認証要件 | なし | YouTube API Key必須 | ライブラリ依存 |
| 制限事項 | 非公式検索 | API クォータ | ライブラリ制限 |

### 依存関係
```python
# ADK コンポーネント
from google.adk.agents import LlmAgent
from google.adk.tools.langchain_tool import LangchainTool  # LangChain統合

# LangChain コミュニティツール
from langchain_community.tools import YouTubeSearchTool

# 外部依存関係（requirements.txt）
youtube_search  # YouTube検索ライブラリ
```

## 3. コード詳細解説

### 3.1 LangChain ツールのインスタンス化

```python
# LangChain ツールの直接インスタンス化
langchain_yt_tool = YouTubeSearchTool()
```

**特徴**:
- **シンプルな初期化**: 追加設定やAPIキー不要
- **コミュニティツール**: LangChain Community パッケージから提供
- **標準化インターフェース**: LangChain の統一ツールインターフェース

### 3.2 ADK ツールラッパーの実装

```python
# LangChain ツールを ADK ツールシステムにラップ
adk_yt_tool = LangchainTool(
    tool=langchain_yt_tool,
)
```

**重要な実装ポイント**:
- **ブリッジパターン**: 異なるフレームワーク間の橋渡し
- **透明性**: 元のツールの機能をそのまま使用
- **統合性**: ADK のツールシステムに完全統合

### 3.3 LlmAgent の設定

```python
root_agent = LlmAgent(
    name="youtube_search_agent",
    model="gemini-2.0-flash",
    instruction="""
    Ask customer to provide singer name, and the number of videos to search.
    """,
    description="Help customer to search for a video on Youtube.",
    tools=[adk_yt_tool],
    output_key="youtube_search_output",
)
```

**設計の特徴**:

#### Agent vs LlmAgent
```python
# 標準的な Agent 使用
root_agent = Agent(...)

# この例では LlmAgent を使用
root_agent = LlmAgent(...)
```

#### 出力キー指定
```python
output_key="youtube_search_output"
```
**目的**: 検索結果を特定のセッションキーに保存し、後続処理で利用

#### 最小限の指示
```python
instruction="""
Ask customer to provide singer name, and the number of videos to search.
"""
```
**シンプルさ**: ツールの機能を最大限活用する最小限の指示

## 4. 設定・環境構築

### 4.1 依存関係のインストール

#### 基本インストール
```bash
# ADK のインストール
pip install google-adk

# LangChain Community のインストール
pip install langchain-community

# YouTube 検索ライブラリのインストール
pip install youtube_search
```

#### uv を使用したインストール
```bash
# requirements.txt からのインストール
uv pip install -r requirements.txt

# または直接インストール
uv pip install youtube_search
```

### 4.2 環境変数設定

YouTube検索には追加の環境変数は不要ですが、ADK の基本設定は必要：

```bash
# .env ファイル
GOOGLE_API_KEY=your_google_api_key
# または
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 4.3 実行方法

```bash
# CLI での実行
adk run contributing/samples/langchain_youtube_search_agent

# Web UI での実行
adk web contributing/samples/langchain_youtube_search_agent

# Python スクリプトでの実行
cd contributing/samples/langchain_youtube_search_agent
python -c "from agent import root_agent; print(root_agent)"
```

### 4.4 動作確認

```python
# 簡単な動作テスト
from agent import root_agent

# エージェントの設定確認
print(f"Agent name: {root_agent.name}")
print(f"Tools count: {len(root_agent.tools)}")
print(f"Output key: {root_agent.output_key}")
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### 音楽検索パターン
```
ユーザー: "Search for Taylor Swift songs on YouTube"
エージェント: "How many videos would you like me to search for?"
ユーザー: "Find the top 5 videos"
エージェント: [YouTubeSearchTool を実行]
結果: "Found 5 Taylor Swift videos:
1. Anti-Hero (Official Music Video)
2. Shake It Off (Official Video)
..."
```

#### 学習コンテンツ検索
```
ユーザー: "I want to learn Python programming"
エージェント: "How many Python tutorial videos should I search for?"
ユーザー: "Show me 3 beginner tutorials"
エージェント: [検索実行]
結果: "Here are 3 Python beginner tutorials:
1. Python Tutorial for Beginners
2. Learn Python in 1 Hour
..."
```

### 5.2 LangChain ツール統合の拡張

#### 複数の LangChain ツール統合
```python
from langchain_community.tools import (
    YouTubeSearchTool,
    WikipediaQueryRun,
    DuckDuckGoSearchRun
)
from google.adk.tools.langchain_tool import LangchainTool

# 複数のLangChainツールをラップ
youtube_tool = LangchainTool(tool=YouTubeSearchTool())
wikipedia_tool = LangchainTool(tool=WikipediaQueryRun())
search_tool = LangchainTool(tool=DuckDuckGoSearchRun())

# 多機能エージェントの作成
multi_search_agent = LlmAgent(
    name="multi_search_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are a comprehensive search assistant with access to:
    1. YouTube video search
    2. Wikipedia articles
    3. General web search
    
    Choose the most appropriate tool based on the user's request.
    """,
    tools=[youtube_tool, wikipedia_tool, search_tool],
)
```

#### カスタムLangChainツールの作成と統合
```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class CustomVideoAnalyzer(BaseTool):
    name = "video_analyzer"
    description = "Analyze YouTube video content and provide insights"
    
    def _run(self, video_url: str) -> str:
        """動画URLを分析して洞察を提供"""
        # カスタム分析ロジック
        return f"Analysis of video: {video_url}"
    
    async def _arun(self, video_url: str) -> str:
        """非同期版の実行"""
        return self._run(video_url)

# カスタムツールをADKで使用
custom_analyzer = LangchainTool(tool=CustomVideoAnalyzer())

enhanced_agent = LlmAgent(
    name="enhanced_youtube_agent",
    tools=[
        LangchainTool(tool=YouTubeSearchTool()),
        custom_analyzer
    ],
    instruction="""
    First search for videos, then analyze the results.
    Provide both search results and content analysis.
    """
)
```

### 5.3 結果処理とフィルタリング

#### 検索結果の後処理
```python
def process_youtube_results(search_results: list) -> list:
    """YouTube検索結果の後処理"""
    processed = []
    
    for result in search_results:
        # 結果の構造化
        processed_result = {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "channel": result.get("channel", ""),
            "duration": result.get("duration", ""),
            "views": extract_view_count(result.get("description", "")),
            "relevance_score": calculate_relevance(result)
        }
        processed.append(processed_result)
    
    # 関連度でソート
    return sorted(processed, key=lambda x: x["relevance_score"], reverse=True)

def extract_view_count(description: str) -> int:
    """説明文から再生回数を抽出"""
    import re
    pattern = r'(\d+(?:,\d+)*)\s*views'
    match = re.search(pattern, description, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def calculate_relevance(result: dict) -> float:
    """結果の関連度を計算"""
    score = 0.0
    
    # タイトルの長さ（適度な長さを好む）
    title_length = len(result.get("title", ""))
    if 10 <= title_length <= 100:
        score += 0.3
    
    # 公式チャンネルの判定
    channel = result.get("channel", "").lower()
    if "official" in channel or "vevo" in channel:
        score += 0.4
    
    # その他の要因...
    return score
```

#### 結果フィルタリング機能
```python
def create_filtered_youtube_agent(content_filters: dict):
    """フィルタリング機能付きYouTubeエージェント"""
    
    class FilteredYouTubeSearchTool(BaseTool):
        name = "filtered_youtube_search"
        description = "Search YouTube with content filtering"
        
        def _run(self, query: str, num_results: int = 5) -> str:
            # 基本検索を実行
            basic_tool = YouTubeSearchTool()
            results = basic_tool._run(f"{query} {num_results}")
            
            # フィルタリング適用
            filtered_results = []
            for result in results:
                if self.passes_filters(result, content_filters):
                    filtered_results.append(result)
            
            return filtered_results
        
        def passes_filters(self, result: dict, filters: dict) -> bool:
            """結果がフィルタ条件を満たすかチェック"""
            duration = result.get("duration", "")
            
            # 長さフィルタ
            if filters.get("max_duration"):
                if not self.is_within_duration(duration, filters["max_duration"]):
                    return False
            
            # チャンネルフィルタ
            if filters.get("excluded_channels"):
                channel = result.get("channel", "").lower()
                if any(excluded in channel for excluded in filters["excluded_channels"]):
                    return False
            
            return True
        
        def is_within_duration(self, duration: str, max_minutes: int) -> bool:
            """動画の長さが制限内かチェック"""
            # 時間文字列のパース実装
            return True  # 簡略化
    
    return LlmAgent(
        name="filtered_youtube_agent",
        tools=[LangchainTool(tool=FilteredYouTubeSearchTool())],
        instruction="Search YouTube with applied content filters"
    )

# 使用例
family_friendly_agent = create_filtered_youtube_agent({
    "max_duration": 30,  # 30分以下
    "excluded_channels": ["inappropriate", "adult"]
})
```

### 5.4 マルチモーダル統合

#### 動画メタデータの分析
```python
def create_multimedia_analysis_agent():
    """マルチメディア分析エージェント"""
    
    return LlmAgent(
        name="multimedia_analyst",
        model="gemini-2.0-flash",
        tools=[
            LangchainTool(tool=YouTubeSearchTool()),
            video_metadata_analyzer,
            thumbnail_analyzer,
            transcript_extractor
        ],
        instruction="""
        You are a multimedia content analyst. For each video:
        1. Search for relevant videos
        2. Analyze metadata (duration, upload date, etc.)
        3. Analyze thumbnails for visual content
        4. Extract and analyze transcripts when available
        5. Provide comprehensive content summaries
        """
    )

def video_metadata_analyzer(video_url: str, tool_context: ToolContext) -> dict:
    """動画メタデータの詳細分析"""
    return {
        "upload_date": "2024-01-15",
        "duration_seconds": 240,
        "view_count": 1500000,
        "like_count": 85000,
        "comment_count": 2300,
        "tags": ["music", "pop", "official"],
        "category": "Music"
    }
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "ModuleNotFoundError: No module named 'youtube_search'"
**原因**: youtube_search ライブラリがインストールされていない
**解決法**:
```bash
# pip でインストール
pip install youtube_search

# uv でインストール
uv pip install youtube_search

# requirements.txt からインストール
pip install -r requirements.txt
```

#### エラー: "ModuleNotFoundError: No module named 'langchain_community'"
**原因**: LangChain Community パッケージがインストールされていない
**解決法**:
```bash
# LangChain Community のインストール
pip install langchain-community

# 必要に応じて LangChain Core も
pip install langchain-core
```

#### エラー: "No search results found"
**原因**: 検索クエリが不適切または YouTube API の制限
**解決法**:
```python
def robust_youtube_search(query: str, max_retries: int = 3):
    """リトライ機能付きYouTube検索"""
    
    for attempt in range(max_retries):
        try:
            tool = YouTubeSearchTool()
            results = tool._run(query)
            
            if results:
                return results
            else:
                # クエリを調整
                query = adjust_search_query(query, attempt)
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # 指数バックオフ
    
    return []

def adjust_search_query(query: str, attempt: int) -> str:
    """検索クエリの調整"""
    adjustments = [
        lambda q: q.replace(" ", "+"),  # スペースを+に変換
        lambda q: q + " official",      # "official"を追加
        lambda q: q.split()[0]          # 最初の単語のみ使用
    ]
    
    if attempt < len(adjustments):
        return adjustments[attempt](query)
    return query
```

### 6.2 LangChain統合の問題

#### バージョン互換性の問題
```python
# LangChain バージョンチェック
import langchain
print(f"LangChain version: {langchain.__version__}")

# 互換性確保のための条件分岐
try:
    from langchain_community.tools import YouTubeSearchTool
except ImportError:
    # 古いバージョンでは別のインポートパス
    from langchain.tools import YouTubeSearchTool
```

#### ツールの初期化エラー
```python
def safe_langchain_tool_init(tool_class, **kwargs):
    """安全なLangChainツール初期化"""
    try:
        return tool_class(**kwargs)
    except Exception as e:
        print(f"Failed to initialize {tool_class.__name__}: {e}")
        # フォールバック実装
        return create_fallback_tool(tool_class.__name__)

def create_fallback_tool(tool_name: str):
    """フォールバック用の基本ツール"""
    class FallbackTool(BaseTool):
        name = tool_name.lower()
        description = f"Fallback implementation for {tool_name}"
        
        def _run(self, query: str) -> str:
            return f"Fallback response for query: {query}"
    
    return FallbackTool()
```

### 6.3 パフォーマンス最適化

#### 検索結果のキャッシュ
```python
import time
from functools import lru_cache

class CachedYouTubeSearchTool(BaseTool):
    name = "cached_youtube_search"
    description = "YouTube search with caching"
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1時間
    
    def _run(self, query: str, num_results: int = 5) -> str:
        cache_key = f"{query}_{num_results}"
        
        # キャッシュチェック
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        # 実際の検索
        basic_tool = YouTubeSearchTool()
        results = basic_tool._run(f"{query} {num_results}")
        
        # キャッシュに保存
        self.cache[cache_key] = (results, time.time())
        
        return results
```

#### 非同期処理の実装
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncYouTubeAgent:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def parallel_search(self, queries: list[str]) -> list[dict]:
        """複数クエリの並列検索"""
        
        loop = asyncio.get_event_loop()
        tasks = []
        
        for query in queries:
            task = loop.run_in_executor(
                self.executor,
                self.search_videos,
                query
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # エラーハンドリング
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "query": queries[i],
                    "error": str(result),
                    "results": []
                })
            else:
                processed_results.append({
                    "query": queries[i],
                    "results": result
                })
        
        return processed_results
    
    def search_videos(self, query: str) -> list:
        """同期的な動画検索"""
        tool = YouTubeSearchTool()
        return tool._run(query)
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### フレームワーク統合パターン
- **ラッパーパターン**: 既存ツールを新しいフレームワークで使用
- **透明性**: 元の機能を損なわない統合
- **段階的移行**: LangChain から ADK への移行戦略

#### ツール統合の最小実装
```python
# 最小限の統合パターン
def integrate_langchain_tool(langchain_tool_class, **init_kwargs):
    """LangChainツールをADKに統合する汎用関数"""
    
    # LangChainツールのインスタンス化
    tool_instance = langchain_tool_class(**init_kwargs)
    
    # ADKツールとしてラップ
    adk_tool = LangchainTool(tool=tool_instance)
    
    return adk_tool

# 使用例
youtube_tool = integrate_langchain_tool(YouTubeSearchTool)
wikipedia_tool = integrate_langchain_tool(WikipediaQueryRun)
```

#### 設定駆動の統合
```python
# 設定ベースのツール統合
LANGCHAIN_TOOLS_CONFIG = {
    "youtube": {
        "class": "langchain_community.tools.YouTubeSearchTool",
        "params": {},
        "enabled": True
    },
    "wikipedia": {
        "class": "langchain_community.tools.WikipediaQueryRun", 
        "params": {},
        "enabled": True
    }
}

def create_agent_from_config(config: dict):
    """設定からエージェントを動的生成"""
    tools = []
    
    for tool_name, tool_config in config.items():
        if not tool_config.get("enabled", True):
            continue
            
        # 動的クラスインポート
        module_path, class_name = tool_config["class"].rsplit(".", 1)
        module = importlib.import_module(module_path)
        tool_class = getattr(module, class_name)
        
        # ツール作成
        tool_instance = tool_class(**tool_config.get("params", {}))
        adk_tool = LangchainTool(tool=tool_instance)
        tools.append(adk_tool)
    
    return LlmAgent(
        name="configured_agent",
        model="gemini-2.0-flash",
        tools=tools
    )
```

### 7.2 他のプロジェクトへの応用

#### エンタープライズ統合プラットフォーム
```python
def create_enterprise_integration_agent():
    """エンタープライズシステム統合エージェント"""
    
    # 各種LangChainツールを統合
    tools = [
        LangchainTool(tool=YouTubeSearchTool()),           # メディア検索
        LangchainTool(tool=SlackSearchTool()),             # 社内コミュニケーション
        LangchainTool(tool=ConfluenceSearchTool()),        # ドキュメント検索
        LangchainTool(tool=JiraSearchTool()),              # タスク管理
    ]
    
    return LlmAgent(
        name="enterprise_search_agent",
        model="gemini-2.0-flash",
        tools=tools,
        instruction="""
        You are an enterprise search assistant with access to:
        - YouTube for training videos
        - Slack for team communications
        - Confluence for documentation
        - Jira for project tracking
        
        Choose the most appropriate tool based on the user's needs.
        """
    )
```

#### 教育プラットフォーム統合
```python
def create_educational_assistant():
    """教育支援エージェント"""
    
    educational_tools = [
        LangchainTool(tool=YouTubeSearchTool()),           # 教育動画
        LangchainTool(tool=ArxivSearchTool()),             # 学術論文
        LangchainTool(tool=WikipediaQueryRun()),           # 百科事典
        LangchainTool(tool=StackOverflowSearchTool()),     # プログラミング支援
    ]
    
    return LlmAgent(
        name="educational_assistant",
        tools=educational_tools,
        instruction="""
        You are an educational assistant helping students learn.
        For each topic:
        1. Search for educational videos on YouTube
        2. Find relevant Wikipedia articles
        3. Look for academic papers on Arxiv
        4. Find programming solutions on Stack Overflow
        
        Provide comprehensive learning resources.
        """
    )
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **段階的統合**: 一度に1つのツールから統合開始
- **エラーハンドリング**: 外部依存関係の適切な処理
- **キャッシュ戦略**: 検索結果の効率的な管理
- **設定外部化**: ツール設定の環境による切り替え

#### 注意点
- **ライセンス確認**: LangChain ツールのライセンス要件
- **API制限**: 外部サービスの利用制限
- **バージョン管理**: LangChain のバージョン互換性
- **依存関係**: 追加パッケージの管理

### 7.4 LangChain エコシステム活用

#### 大規模LangChainツール統合
```python
class LangChainToolsRegistry:
    """LangChainツールの統合レジストリ"""
    
    def __init__(self):
        self.tools = {}
        self.categories = {
            "search": [YouTubeSearchTool, DuckDuckGoSearchRun],
            "knowledge": [WikipediaQueryRun, ArxivSearchTool],
            "development": [ShellTool, PythonREPLTool],
            "communication": [SlackSearchTool, EmailTool]
        }
    
    def register_tool(self, name: str, tool_class, category: str = "misc"):
        """ツールをレジストリに登録"""
        self.tools[name] = {
            "class": tool_class,
            "category": category,
            "adk_tool": None
        }
    
    def get_tools_by_category(self, category: str) -> list:
        """カテゴリ別ツール取得"""
        return [
            self.get_adk_tool(name) 
            for name, info in self.tools.items() 
            if info["category"] == category
        ]
    
    def get_adk_tool(self, name: str):
        """ADKツールとして取得（遅延初期化）"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")
        
        tool_info = self.tools[name]
        if tool_info["adk_tool"] is None:
            langchain_tool = tool_info["class"]()
            tool_info["adk_tool"] = LangchainTool(tool=langchain_tool)
        
        return tool_info["adk_tool"]

# 使用例
registry = LangChainToolsRegistry()
registry.register_tool("youtube", YouTubeSearchTool, "search")
registry.register_tool("wikipedia", WikipediaQueryRun, "knowledge")

# カテゴリ別エージェント作成
search_agent = LlmAgent(
    name="search_specialist",
    tools=registry.get_tools_by_category("search")
)
```

この langchain_youtube_search_agent は、LangChain エコシステムとの統合パターンを学ぶのに最適なサンプルです。特に既存の LangChain ツールを ADK で活用する方法や、フレームワーク間の統合戦略を理解するのに有用です。