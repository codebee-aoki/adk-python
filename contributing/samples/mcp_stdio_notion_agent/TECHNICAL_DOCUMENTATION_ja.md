# MCP STDIO Notion 統合エージェント - 技術ドキュメント

## 概要

MCP STDIO Notion 統合エージェント（`mcp_stdio_notion_agent`）は、Model Context Protocol（MCP）の STDIO 接続を通じて Notion API と統合し、Notion ワークスペースの管理を行うエージェントです。ページの読み取り、検索、コメント、作成など、Notion の包括的な操作を MCP プロトコル経由で実現し、ワークスペース アシスタントとしての機能を提供します。

## 技術仕様

### アーキテクチャ

```python
# MCP STDIO Notion 統合エージェント
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="notion_agent",
    instruction="You are my workspace assistant. Use the provided tools to read, search, comment on, or create Notion pages.",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",                                    # Node.js パッケージ実行
                args=["-y", "@notionhq/notion-mcp-server"],      # Notion MCP サーバー
                env={"OPENAPI_MCP_HEADERS": NOTION_HEADERS},     # 認証ヘッダー
            )
        )
    ],
)
```

### 主要コンポーネント

#### 1. Notion API 認証
```python
import json
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_HEADERS = json.dumps({
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",               # Notion API バージョン
})
```

#### 2. STDIO サーバーパラメータ
```python
from google.adk.tools.mcp_tool.mcp_toolset import StdioServerParameters

connection_params = StdioServerParameters(
    command="npx",                                # Node.js パッケージランナー
    args=["-y", "@notionhq/notion-mcp-server"],  # Notion MCP サーバーパッケージ
    env={"OPENAPI_MCP_HEADERS": NOTION_HEADERS}, # 環境変数として認証情報を渡す
)
```

#### 3. MCP ツールセット
```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

toolset = MCPToolset(
    connection_params=connection_params,
    # Notion MCP サーバーが提供するすべてのツールを使用
)
```

## Notion MCP サーバー機能

### 1. 利用可能なツール

**ページ操作**:
- `search_pages`: ページ検索
- `read_page`: ページ内容読み取り
- `create_page`: 新規ページ作成
- `update_page`: ページ更新
- `delete_page`: ページ削除

**ブロック操作**:
- `read_blocks`: ブロック内容読み取り
- `create_blocks`: ブロック作成
- `update_blocks`: ブロック更新
- `delete_blocks`: ブロック削除

**データベース操作**:
- `query_database`: データベースクエリ
- `create_database_entry`: データベースエントリ作成
- `update_database_entry`: データベースエントリ更新

**コメント機能**:
- `read_comments`: コメント読み取り
- `create_comment`: コメント作成

## 実行フロー

### 1. 初期化と認証

**環境設定**:
```bash
# .env ファイル設定
NOTION_API_KEY=secret_xxxxx...
```

**認証フロー**:
```text
1. 環境変数から Notion API キー読み込み
2. 認証ヘッダー構築
3. MCP サーバーに環境変数として渡す
4. Notion API への認証済みアクセス
```

### 2. MCP STDIO 通信

**サーバー起動**:
```text
npx -y @notionhq/notion-mcp-server
↓
MCP サーバー起動（STDIO モード）
↓
ADK エージェントと双方向通信
```

**ツール呼び出し**:
```text
User: "今日のタスクを確認してください"
↓
Agent: search_pages ツール呼び出し
↓
MCP サーバー: Notion API 経由でページ検索
↓ 
結果をエージェントに返却
↓
User への応答生成
```

## 使用例

### 基本的な Notion 操作

**ページ検索**:
```python
response = await root_agent.invoke("プロジェクト関連のページを検索してください")

# 実行フロー:
# 1. search_pages ツール呼び出し
# 2. "プロジェクト" キーワードでNotion検索
# 3. 検索結果の一覧表示
# 4. 関連ページの概要説明
```

**ページ内容の読み取り**:
```python
response = await root_agent.invoke("「週次レポート」ページの内容を要約してください")

# 実行フロー:
# 1. search_pages で「週次レポート」検索
# 2. read_page で詳細内容取得
# 3. 内容の分析と要約
# 4. 要約結果の提示
```

### 高度な Notion 操作

**新規ページ作成**:
```python
query = """
「今週の振り返り」というタイトルで新しいページを作成し、
以下の項目を含めてください：
- 達成できたこと
- 課題と改善点
- 来週の目標
"""

response = await root_agent.invoke(query)

# 実行フロー:
# 1. create_page ツール呼び出し
# 2. 指定された構造でページ作成
# 3. 各セクションのブロック追加
# 4. 作成完了の報告
```

**データベースクエリ**:
```python
response = await root_agent.invoke("タスクデータベースから未完了のタスクを取得してください")

# 実行フロー:
# 1. データベース検索
# 2. query_database で条件指定（status != "完了"）
# 3. 結果の整理と表示
# 4. 優先度に応じた並び替え
```

## 高度な実装例

### 1. 自動タスク管理システム

```python
class NotionTaskManager:
    def __init__(self, notion_agent):
        self.agent = notion_agent
    
    async def daily_task_review(self):
        """日次タスクレビュー"""
        # 今日期限のタスク取得
        today_tasks = await self.agent.invoke(
            "今日期限のタスクをデータベースから取得してください"
        )
        
        # 未完了タスクの確認
        incomplete_tasks = await self.agent.invoke(
            "未完了タスクをリストアップしてください"
        )
        
        # 進捗レポート作成
        report = await self.agent.invoke(
            f"以下のタスクの進捗レポートを作成してください:\n{today_tasks}"
        )
        
        return report
    
    async def create_weekly_goals(self, goals: list[str]):
        """週次目標設定"""
        goal_text = "\n".join(f"- {goal}" for goal in goals)
        
        return await self.agent.invoke(
            f"「今週の目標」ページを作成し、以下の目標を追加してください:\n{goal_text}"
        )
```

### 2. 会議議事録管理

```python
class MeetingNotesManager:
    async def create_meeting_notes(self, meeting_info: dict):
        """会議議事録作成"""
        template = f"""
        「{meeting_info['title']}」の議事録ページを作成してください。
        
        構成:
        - 日時: {meeting_info['date']}
        - 参加者: {', '.join(meeting_info['participants'])}
        - アジェンダ: {meeting_info['agenda']}
        - 議論内容: （後で記入）
        - アクションアイテム: （後で記入）
        - 次回予定: （後で記入）
        """
        
        return await self.agent.invoke(template)
    
    async def update_action_items(self, page_id: str, actions: list[dict]):
        """アクションアイテム更新"""
        action_text = ""
        for action in actions:
            action_text += f"- {action['task']} (担当: {action['owner']}, 期限: {action['due']})\n"
        
        return await self.agent.invoke(
            f"ページ{page_id}のアクションアイテムセクションを更新してください:\n{action_text}"
        )
```

### 3. ナレッジベース構築

```python
class KnowledgeBaseBuilder:
    async def organize_documentation(self):
        """ドキュメント整理"""
        # 既存ページの分析
        all_pages = await self.agent.invoke("すべてのページを取得してください")
        
        # カテゴリ別分類
        categories = await self.agent.invoke(
            "取得したページをカテゴリ別に分類し、階層構造を提案してください"
        )
        
        # インデックスページ作成
        index_page = await self.agent.invoke(
            "「ナレッジベース インデックス」ページを作成し、"
            "分類結果に基づいてリンク構造を構築してください"
        )
        
        return index_page
    
    async def create_template_library(self):
        """テンプレートライブラリ作成"""
        templates = [
            "プロジェクト計画書",
            "週次レポート", 
            "議事録",
            "技術仕様書",
            "振り返りシート"
        ]
        
        for template in templates:
            await self.agent.invoke(
                f"「{template}テンプレート」ページを作成し、"
                f"再利用可能な{template}の構造を定義してください"
            )
```

## Notion ワークスペースとの統合

### 1. ワークスペース設定

**Notion 統合の作成**:
```text
1. Notion 開発者ページ (https://www.notion.so/my-integrations)
2. 新しい統合を作成
3. API キーを取得
4. 必要なページ・データベースに統合を招待
```

**権限設定**:
```text
- Read content: ページ・データベース読み取り
- Update content: ページ・データベース更新  
- Insert content: 新規作成
- Comment: コメント機能
```

### 2. データベーススキーマ

**タスク管理データベース例**:
```json
{
  "properties": {
    "タスク名": {"type": "title"},
    "状態": {
      "type": "select",
      "options": ["未着手", "進行中", "完了", "保留"]
    },
    "優先度": {
      "type": "select", 
      "options": ["高", "中", "低"]
    },
    "期限": {"type": "date"},
    "担当者": {"type": "people"},
    "プロジェクト": {"type": "relation"}
  }
}
```

## エラーハンドリング

### 1. 認証エラー

```python
try:
    response = await notion_agent.invoke("ページを検索してください")
except NotionAPIError as e:
    if e.code == "unauthorized":
        print("Notion API キーの確認が必要です")
        # API キー再設定の案内
    elif e.code == "forbidden":
        print("統合に必要な権限がありません")
        # 権限設定の案内
```

### 2. ページ不存在エラー

```python
try:
    page_content = await notion_agent.invoke("存在しないページを読み取り")
except NotionPageNotFoundError as e:
    print(f"ページが見つかりません: {e.page_id}")
    # 代替ページの提案
```

### 3. レート制限エラー

```python
import asyncio

async def rate_limited_operation(operation):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            return await operation()
        except NotionRateLimitError as e:
            wait_time = 2 ** retry_count
            print(f"レート制限: {wait_time}秒待機")
            await asyncio.sleep(wait_time)
            retry_count += 1
    
    raise Exception("最大リトライ回数を超過")
```

## セキュリティ考慮事項

### 1. API キー管理
```python
# 環境変数での管理（推奨）
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

# 設定ファイルでの管理（本番環境では非推奨）
# with open('.notion_config') as f:
#     config = json.load(f)
```

### 2. アクセス制御
```python
# 読み取り専用モードの設定
readonly_agent = LlmAgent(
    tools=[
        MCPToolset(
            connection_params=stdio_params,
            tool_filter=['search_pages', 'read_page', 'read_blocks']  # 読み取りのみ
        )
    ]
)
```

## パフォーマンス最適化

### 1. バッチ処理

```python
async def batch_page_updates(updates: list[dict]):
    """複数ページの一括更新"""
    tasks = []
    for update in updates:
        task = notion_agent.invoke(
            f"ページ {update['page_id']} を更新: {update['content']}"
        )
        tasks.append(task)
    
    # 並列実行
    results = await asyncio.gather(*tasks)
    return results
```

### 2. キャッシュ機能

```python
from functools import lru_cache
import time

class NotionCache:
    def __init__(self, ttl=300):  # 5分間キャッシュ
        self.cache = {}
        self.ttl = ttl
    
    async def get_cached_page(self, page_id: str):
        if page_id in self.cache:
            content, timestamp = self.cache[page_id]
            if time.time() - timestamp < self.ttl:
                return content
        
        # キャッシュミス: 実際のページ取得
        content = await notion_agent.invoke(f"ページ {page_id} を読み取り")
        self.cache[page_id] = (content, time.time())
        return content
```

## 関連ファイル

- `agent.py`: メインエージェント実装
- `README.md`: 英語版ドキュメント
- `README_ja.md`: 日本語版ドキュメント
- `.env`: 環境変数設定（Notion API キー）

## 依存関係

- `google.adk.agents.llm_agent`: LLM エージェント
- `google.adk.tools.mcp_tool.mcp_toolset`: MCP ツールセット
- `dotenv`: 環境変数管理
- `@notionhq/notion-mcp-server`: Notion MCP サーバー（npm パッケージ）
- **Notion API**: ワークスペースアクセス用の API キー