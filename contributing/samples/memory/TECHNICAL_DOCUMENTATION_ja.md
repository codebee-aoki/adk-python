# メモリ管理エージェント - 技術ドキュメント

## 概要

メモリ管理エージェント（`memory`）は、ADK フレームワークの組み込みメモリツール機能を活用して長期記憶と情報保持を実現するエージェントです。時間情報の自動更新、メモリの読み込み・事前読み込み機能、コールバックベースの状態管理など、永続的な情報管理パターンを実演します。

## 技術仕様

### アーキテクチャ

```python
# メモリ管理対応エージェント
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='memory_agent',
    description='agent that have access to memory tools.',
    before_agent_callback=update_current_time,  # 時間更新コールバック
    instruction="You are an agent that help user answer questions.\n\nCurrent time: {_time}",
    tools=[
        load_memory_tool,      # メモリ読み込みツール
        preload_memory_tool,   # メモリ事前読み込みツール
    ],
)
```

### 主要コンポーネント

#### 1. 時間更新コールバック
```python
from datetime import datetime
from google.adk.agents.callback_context import CallbackContext

def update_current_time(callback_context: CallbackContext):
    """エージェント実行前に現在時刻を更新"""
    callback_context.state['_time'] = datetime.now().isoformat()
```

#### 2. メモリツール
```python
from google.adk.tools.load_memory_tool import load_memory_tool
from google.adk.tools.preload_memory_tool import preload_memory_tool

tools = [
    load_memory_tool,      # 必要時にメモリを読み込み
    preload_memory_tool,   # 事前にメモリを読み込み
]
```

#### 3. 動的指示テンプレート
```python
instruction = """\
You are an agent that help user answer questions.

Current time: {_time}
"""
# {_time} はコールバックで設定される現在時刻で置換
```

## メモリシステム機能

### 1. メモリ読み込みツール

**機能**:
- ユーザーのクエリに基づいて関連メモリを検索
- セマンティック検索による関連情報取得
- 必要な時点でのオンデマンド読み込み

**使用例**:
```python
# ユーザーが過去の会話を参照したい場合
user_query = "昨日話した プロジェクトの件について詳しく教えて"

# load_memory_tool が自動的に:
# 1. "プロジェクト" "昨日" などのキーワードで検索
# 2. 関連する過去の会話や情報を取得
# 3. コンテキストとして提供
```

### 2. メモリ事前読み込みツール

**機能**:
- 会話開始時に関連性の高いメモリを事前読み込み
- ユーザーの過去の傾向や興味に基づく予測読み込み
- パフォーマンス向上のためのキャッシュ機能

**使用例**:
```python
# 会話開始時に自動実行
# preload_memory_tool が:
# 1. ユーザーの過去の興味関心を分析
# 2. 頻繁に参照される情報を事前読み込み
# 3. 会話の流れを予測して関連情報を準備
```

## 実行フロー

### 1. 初期化フロー

**エージェント起動時**:
```text
1. before_agent_callback 実行
   ↓ update_current_time() 
   ↓ callback_context.state['_time'] = current_time

2. instruction テンプレート展開
   ↓ "Current time: {_time}" → "Current time: 2025-01-01T10:30:00"

3. preload_memory_tool 実行（オプション）
   ↓ 関連メモリの事前読み込み

4. ユーザーリクエスト受付準備完了
```

### 2. メモリ活用フロー

**ユーザークエリ処理**:
```text
User: "先週話したプロジェクトの進捗はどう？"

1. クエリ分析
   ↓ キーワード抽出: "先週", "プロジェクト", "進捗"

2. load_memory_tool 実行
   ↓ 関連メモリ検索・取得

3. 時間コンテキスト確認
   ↓ current_time と過去の記録の時系列分析

4. 統合応答生成
   ↓ メモリ + 現在時刻 + 新情報 → 総合的回答
```

## 使用例

### 基本的なメモリ活用

**過去の会話の参照**:
```python
response = await root_agent.invoke("昨日話したタスクの件、どうなった？")

# 実行フロー:
# 1. update_current_time() で現在時刻設定
# 2. load_memory_tool でタスク関連の昨日の会話を検索
# 3. 時系列を考慮して関連情報を取得
# 4. 現在の状況と過去の記録を統合して応答
```

**継続的な話題の追跡**:
```python
# 第1回目の会話
response1 = await root_agent.invoke("新しいプロジェクトを始めます。目標は売上20%向上です。")

# 第2回目の会話（別セッション）
response2 = await root_agent.invoke("プロジェクトの進捗を確認したいです")

# メモリツールにより第1回目の情報が自動的に参照される
```

### 高度なメモリ管理

**時系列を考慮した情報管理**:
```python
# 時間経過を考慮した応答
user_queries = [
    "今月の目標を設定しました",        # 1月1日
    "目標の中間確認をお願いします",      # 1月15日  
    "月末なので成果をレビューしたい",    # 1月31日
]

# 各段階で適切な時間コンテキストと過去のメモリが活用される
```

## 高度な実装例

### 1. プロジェクト管理アシスタント

```python
class ProjectMemoryManager:
    def __init__(self, memory_agent):
        self.agent = memory_agent
    
    async def track_project_milestones(self, project_id: str):
        """プロジェクト マイルストーン追跡"""
        # 過去のマイルストーン情報を取得
        milestone_history = await self.agent.invoke(
            f"プロジェクト {project_id} のマイルストーン履歴を確認"
        )
        
        # 現在の進捗と比較分析
        current_status = await self.agent.invoke(
            "現在のプロジェクト状況を過去の計画と比較してください"
        )
        
        return {
            'history': milestone_history,
            'current_status': current_status,
            'recommendations': await self.generate_recommendations(
                milestone_history, current_status
            )
        }
    
    async def generate_weekly_summary(self):
        """週次サマリー生成"""
        return await self.agent.invoke(
            "今週の活動を振り返り、先週の計画との差異を分析してください。"
            "来週への提案も含めてください。"
        )
```

### 2. 学習進捗管理システム

```python
class LearningProgressTracker:
    async def track_learning_journey(self, topic: str):
        """学習の旅の追跡"""
        # 過去の学習記録を取得
        learning_history = await self.agent.invoke(
            f"{topic}について過去に学習した内容と理解度を確認"
        )
        
        # 現在の理解レベル評価
        current_understanding = await self.agent.invoke(
            f"{topic}に関する現在の理解度を過去と比較評価してください"
        )
        
        # 次のステップ推奨
        next_steps = await self.agent.invoke(
            "学習履歴と現在のレベルに基づいて、次に学ぶべき内容を提案してください"
        )
        
        return {
            'history': learning_history,
            'current_level': current_understanding,
            'next_steps': next_steps
        }
    
    async def create_personalized_curriculum(self):
        """個人化されたカリキュラム作成"""
        return await self.agent.invoke(
            "これまでの学習履歴、興味分野、習得済みスキルを分析し、"
            "個人に最適化された学習計画を作成してください"
        )
```

### 3. 長期関係管理システム

```python
class RelationshipManager:
    async def maintain_relationship_context(self, person_name: str):
        """関係性コンテキスト維持"""
        # 過去のやり取り履歴
        interaction_history = await self.agent.invoke(
            f"{person_name}さんとの過去のやり取りや話題を確認"
        )
        
        # 関係性の変化分析
        relationship_evolution = await self.agent.invoke(
            f"{person_name}さんとの関係性の変化や発展を時系列で分析"
        )
        
        # 次回の接触における注意点
        interaction_tips = await self.agent.invoke(
            "次回のやり取りで気を付けるべき点や言及すべき話題を提案"
        )
        
        return {
            'history': interaction_history,
            'relationship_analysis': relationship_evolution,
            'tips': interaction_tips
        }
```

## メモリシステムの詳細機能

### 1. セマンティック検索

**概念的類似性による検索**:
```python
# 直接的なキーワードがなくても関連情報を取得
user_query = "最近の成果について"

# メモリシステムが以下のような関連情報を検索:
# - "達成", "完了", "成功" などの類似概念
# - 時間軸での "最近" の定義（過去1-2週間）
# - 成果に関連するプロジェクト、タスク、目標
```

### 2. 時間ベースフィルタリング

**時系列を考慮した情報取得**:
```python
# 時間の表現を理解した検索
time_queries = [
    "昨日の件",           # 1日前の情報
    "先週話した",         # 1週間前の情報
    "今月初めに決めた",    # 月初の情報
    "前回のミーティング",  # 最後のミーティング記録
]

# 各々で適切な時間範囲の情報が取得される
```

### 3. 優先度ベース情報取得

**重要度を考慮した情報選択**:
```python
# 重要度の高い情報から優先的に取得
# - ユーザーが強調した内容
# - 繰り返し言及された話題
# - 期限やマイルストーンに関連する情報
# - 感情的に重要な出来事
```

## パフォーマンス最適化

### 1. メモリキャッシュ戦略

```python
class MemoryCache:
    def __init__(self, cache_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.cache_size = cache_size
        self.ttl = ttl  # Time To Live (seconds)
    
    async def get_cached_memory(self, query_hash: str):
        """キャッシュされたメモリ取得"""
        if query_hash in self.cache:
            memory_data, timestamp = self.cache[query_hash]
            if time.time() - timestamp < self.ttl:
                return memory_data
        
        return None
    
    async def cache_memory(self, query_hash: str, memory_data: dict):
        """メモリのキャッシュ保存"""
        if len(self.cache) >= self.cache_size:
            # LRU eviction
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[query_hash] = (memory_data, time.time())
```

### 2. プリフェッチ戦略

```python
class MemoryPrefetcher:
    async def predict_and_prefetch(self, conversation_context: str):
        """会話コンテキストから次に必要なメモリを予測"""
        # 会話パターン分析
        patterns = self.analyze_conversation_patterns(conversation_context)
        
        # 関連トピック予測
        likely_topics = self.predict_topics(patterns)
        
        # バックグラウンドでメモリ事前読み込み
        prefetch_tasks = []
        for topic in likely_topics:
            task = self.prefetch_memory_for_topic(topic)
            prefetch_tasks.append(task)
        
        await asyncio.gather(*prefetch_tasks, return_exceptions=True)
```

### 3. メモリ整理とアーカイブ

```python
class MemoryArchiver:
    async def organize_memories(self):
        """メモリの整理とアーカイブ"""
        # 古いメモリの特定
        old_memories = await self.identify_old_memories()
        
        # 重要度評価
        for memory in old_memories:
            importance_score = await self.evaluate_importance(memory)
            
            if importance_score < threshold:
                # 低重要度メモリをアーカイブ
                await self.archive_memory(memory)
            else:
                # 重要メモリを維持
                await self.maintain_memory(memory)
```

## トラブルシューティング

### 1. メモリ取得失敗

```python
async def handle_memory_retrieval_failure(query: str, error: Exception):
    """メモリ取得失敗時の処理"""
    if "timeout" in str(error).lower():
        # タイムアウト: より具体的なクエリで再試行
        simplified_query = simplify_query(query)
        return await retry_memory_retrieval(simplified_query)
    
    elif "not_found" in str(error).lower():
        # メモリ不存在: ユーザーに確認
        return "申し訳ございませんが、関連する過去の記録が見つかりませんでした。"
    
    else:
        # その他のエラー: 汎用的な応答
        return "メモリの取得中に問題が発生しました。詳細を再度お聞かせください。"
```

### 2. 時間情報の不整合

```python
def validate_time_consistency(callback_context: CallbackContext):
    """時間情報の整合性検証"""
    current_time = datetime.now()
    stored_time_str = callback_context.state.get('_time')
    
    if stored_time_str:
        stored_time = datetime.fromisoformat(stored_time_str)
        time_diff = abs((current_time - stored_time).total_seconds())
        
        # 5分以上の差がある場合は更新
        if time_diff > 300:
            callback_context.state['_time'] = current_time.isoformat()
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `main.py`: 実行エントリーポイント

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.agents.callback_context`: コールバックコンテキスト
- `google.adk.tools.load_memory_tool`: メモリ読み込みツール
- `google.adk.tools.preload_memory_tool`: メモリ事前読み込みツール
- `datetime`: 時間管理機能