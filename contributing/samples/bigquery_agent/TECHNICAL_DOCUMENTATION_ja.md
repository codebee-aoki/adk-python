# bigquery_agent - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`bigquery_agent` エージェントは、Google BigQuery サービスとの高度な統合を提供する専門エージェントです。OAuth2 認証を使用してユーザーの BigQuery データに安全にアクセスし、データセットとテーブルの包括的な管理機能を提供します。

### 主要機能
- **データセット管理**: 一覧表示、詳細取得、新規作成
- **テーブル管理**: 一覧表示、詳細取得、新規作成
- **OAuth2 認証**: 安全なユーザー認証とアクセス制御
- **ツールフィルタリング**: 必要な機能のみを選択的に公開

### 対象ユースケース
- データベース管理とモニタリング
- データプラットフォームの構築支援
- データサイエンスプロジェクトの初期セットアップ
- 企業データ資産の管理とガバナンス

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (BigQuery 操作要求)
[bigquery_agent] 
    ↓ (OAuth2 認証)
[Google OAuth2 Server]
    ↓ (認証トークン)
[BigQueryToolset]
    ↓ (API呼び出し)
[Google BigQuery API]
    ├── Datasets API - データセット管理
    └── Tables API - テーブル管理
    ↓ (データ・メタデータ)
[ユーザーのBigQueryプロジェクト]
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (Agent クラス + BigQuery専門機能)
- **認証システム**: OAuth2 (クライアント認証情報管理)
- **BigQuery統合**: `BigQueryToolset` (Google API Tool)
- **ツールフィルタ**: 6つの選択的機能公開
- **環境設定**: dotenv による設定管理

### 提供されるツール機能
```python
tools_to_expose = [
    "bigquery_datasets_list",     # データセット一覧
    "bigquery_datasets_get",      # データセット詳細取得
    "bigquery_datasets_insert",   # データセット作成
    "bigquery_tables_list",       # テーブル一覧  
    "bigquery_tables_get",        # テーブル詳細取得
    "bigquery_tables_insert",     # テーブル作成
]
```

### 依存関係
```python
# 環境管理
from dotenv import load_dotenv
import os

# ADK コンポーネント
from google.adk import Agent
from google.adk.tools.google_api_tool import BigQueryToolset

# BigQuery統合はGoogleAPIToolsetを通じて提供
```

## 3. コード詳細解説

### 3.1 OAuth2 認証設定

```python
# 環境変数からOAuth認証情報を取得
oauth_client_id = os.getenv("OAUTH_CLIENT_ID")
oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")
```

**重要な実装ポイント**:
- **セキュリティ**: 認証情報を環境変数で管理
- **柔軟性**: 複数環境での使い回し可能
- **標準準拠**: Google OAuth2 標準に準拠

### 3.2 BigQueryToolset 設定

```python
bigquery_toolset = BigQueryToolset(
    client_id=oauth_client_id,
    client_secret=oauth_client_secret,
    tool_filter=tools_to_expose,
)
```

**設計の特徴**:
- **最小権限の原則**: 必要な機能のみを公開
- **統合性**: Google API Tool との統一インターフェース
- **拡張性**: tool_filter による柔軟な機能制御

### 3.3 エージェント指示（instruction）

```python
instruction="""
  You are a helpful Google BigQuery agent that help to manage users' data on Google BigQuery.
  Use the provided tools to conduct various operations on users' data in Google BigQuery.

  Scenario 1: データセット一覧の取得
  The user wants to query their biguqery datasets
  Use bigquery_datasets_list to query user's datasets

  Scenario 2: データセット詳細の取得
  The user wants to query the details of a specific dataset
  Use bigquery_datasets_get to get a dataset's details

  Scenario 3: 新しいデータセットの作成
  The user wants to create a new dataset
  Use bigquery_datasets_insert to create a new dataset

  [テーブル管理のシナリオも同様に定義]
"""
```

**指示設計の特徴**:
- **シナリオベース**: 具体的な使用場面を明示
- **ツール対応**: 各シナリオに対応するツールを明確化
- **ユーザーコンテキスト**: `{userInfo?}` でユーザー情報を動的挿入

## 4. 設定・環境構築

### 4.1 Google Cloud Console 設定

#### OAuth2 認証設定
1. **Google Cloud Console** にアクセス
2. **API とサービス** → **認証情報** に移動
3. **認証情報を作成** → **OAuth 2.0 クライアント ID** を選択
4. **ウェブアプリケーション** を選択
5. **承認済みのリダイレクト URI** に以下を追加:
   ```
   http://localhost/dev-ui/
   ```

#### BigQuery API 有効化
```bash
# gcloud CLI での有効化
gcloud services enable bigquery.googleapis.com

# または Google Cloud Console で有効化
# API とサービス → ライブラリ → BigQuery API → 有効にする
```

### 4.2 環境変数設定

```bash
# .env ファイルに追加
OAUTH_CLIENT_ID=your_oauth_client_id_here
OAUTH_CLIENT_SECRET=your_oauth_client_secret_here

# Google Cloud プロジェクト設定
GOOGLE_CLOUD_PROJECT=your_project_id
```

### 4.3 権限設定

#### 必要な BigQuery 権限
- `BigQuery Data Viewer`: データの読み取り
- `BigQuery Data Editor`: データの編集
- `BigQuery Admin`: データセット・テーブルの作成・削除

#### IAM 設定例
```bash
# ユーザーに BigQuery 権限を付与
gcloud projects add-iam-policy-binding your-project-id \
    --member="user:user@example.com" \
    --role="roles/bigquery.admin"
```

### 4.4 実行方法

```bash
# CLI での実行
adk run contributing/samples/bigquery_agent

# Web UI での実行
adk web contributing/samples/bigquery_agent
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### データセットの管理
```
ユーザー: "Do I have any datasets in project my-project?"
エージェント: [bigquery_datasets_list を実行]
"You have 3 datasets in your project: dataset1, dataset2, analytics_data"

ユーザー: "Show me details of analytics_data dataset"
エージェント: [bigquery_datasets_get を実行]
"Dataset analytics_data: Location: US, Created: 2024-01-15, Tables: 5"
```

#### テーブルの作成
```
ユーザー: "Create a new table called 'users' with columns: id (integer), name (string), email (string)"
エージェント: [bigquery_tables_insert を実行]
"Successfully created table 'users' with the specified schema in dataset analytics_data"
```

### 5.2 高度な使用パターン

#### データセット作成からテーブル作成までの一連の流れ
```python
# カスタムワークフローの実装例
async def setup_analytics_environment(project_id: str, location: str):
    """分析環境のセットアップワークフロー"""
    
    # 1. データセット作成
    dataset_config = {
        "datasetReference": {
            "projectId": project_id,
            "datasetId": "analytics_workspace"
        },
        "location": location,
        "description": "Analytics workspace for data science projects"
    }
    
    # 2. 標準テーブル群の作成
    tables_schema = [
        {
            "name": "raw_events",
            "schema": [
                {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
                {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
                {"name": "user_id", "type": "STRING", "mode": "REQUIRED"},
                {"name": "event_data", "type": "JSON", "mode": "NULLABLE"}
            ]
        },
        {
            "name": "processed_metrics", 
            "schema": [
                {"name": "metric_date", "type": "DATE", "mode": "REQUIRED"},
                {"name": "metric_name", "type": "STRING", "mode": "REQUIRED"},
                {"name": "metric_value", "type": "FLOAT64", "mode": "REQUIRED"}
            ]
        }
    ]
```

### 5.3 エンタープライズ統合パターン

#### マルチプロジェクト対応
```python
class MultiProjectBigQueryAgent:
    def __init__(self):
        self.project_agents = {}
        
    def create_project_agent(self, project_id: str, client_id: str, client_secret: str):
        """プロジェクト固有のエージェントを作成"""
        toolset = BigQueryToolset(
            client_id=client_id,
            client_secret=client_secret,
            tool_filter=["bigquery_datasets_list", "bigquery_tables_list"]
        )
        
        agent = Agent(
            name=f"bigquery_agent_{project_id}",
            model="gemini-2.0-flash",
            instruction=f"You manage BigQuery resources for project {project_id}",
            tools=[toolset]
        )
        
        self.project_agents[project_id] = agent
        return agent
```

#### データガバナンス統合
```python
def create_governed_bigquery_agent(governance_rules: dict):
    """ガバナンス制御付きBigQueryエージェント"""
    
    # 許可されたオペレーションのフィルタリング
    allowed_operations = governance_rules.get("allowed_operations", [])
    
    # 地域制限の適用
    allowed_locations = governance_rules.get("allowed_locations", ["US", "EU"])
    
    # カスタム指示の生成
    governance_instruction = f"""
    You are a governance-compliant BigQuery agent.
    
    RESTRICTIONS:
    - Only perform these operations: {', '.join(allowed_operations)}
    - Only create resources in these locations: {', '.join(allowed_locations)}
    - Always check data classification before operations
    - Log all operations for audit purposes
    """
    
    return Agent(
        name="governed_bigquery_agent",
        instruction=governance_instruction,
        tools=[create_governed_toolset(governance_rules)]
    )
```

## 6. トラブルシューティング

### 6.1 認証関連の問題

#### 問題: "OAuth2 認証に失敗する"
**原因と解決法**:
```bash
# 1. クライアント認証情報の確認
echo $OAUTH_CLIENT_ID
echo $OAUTH_CLIENT_SECRET

# 2. リダイレクトURIの確認
# Google Cloud Console で以下が設定されているか確認:
# http://localhost/dev-ui/

# 3. ブラウザのポップアップブロック解除
# Chrome: 設定 → プライバシーとセキュリティ → サイトの設定 → ポップアップとリダイレクト
```

#### 問題: "権限が不足している"
**解決方法**:
```bash
# 必要な権限を確認・付与
gcloud projects get-iam-policy your-project-id

# BigQuery Admin 権限の付与
gcloud projects add-iam-policy-binding your-project-id \
    --member="user:your-email@domain.com" \
    --role="roles/bigquery.admin"
```

### 6.2 API 使用量とコスト管理

#### クォータ監視
```python
# BigQuery 使用量の監視
def monitor_bigquery_usage(project_id: str):
    """BigQuery 使用量の監視"""
    
    # クォータ使用量の確認
    usage_query = f"""
    SELECT
      job_type,
      COUNT(*) as job_count,
      SUM(total_bytes_processed) as total_bytes
    FROM `{project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
    WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
    GROUP BY job_type
    """
    
    return usage_query
```

#### コスト最適化
```python
# コスト効率的な設定
cost_optimized_toolset = BigQueryToolset(
    client_id=oauth_client_id,
    client_secret=oauth_client_secret,
    tool_filter=[
        "bigquery_datasets_list",  # 無料
        "bigquery_tables_list",    # 無料
        "bigquery_datasets_get",   # 無料
        # クエリ実行系は除外してコスト制御
    ]
)
```

### 6.3 パフォーマンス最適化

#### 大量データ処理への対応
```python
# ページネーション対応
def list_large_datasets(project_id: str, page_size: int = 50):
    """大量のデータセットを効率的に処理"""
    
    # ページングロジックの実装
    # BigQuery API のページング機能を活用
    pass

# 並列処理での高速化
import asyncio

async def parallel_dataset_operations(dataset_ids: list[str]):
    """複数データセットの並列処理"""
    tasks = []
    for dataset_id in dataset_ids:
        task = asyncio.create_task(get_dataset_details(dataset_id))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### Google API Tool 統合パターン
- **ツールセット活用**: 複雑なAPI統合の抽象化
- **認証管理**: OAuth2 の安全で効率的な実装
- **機能選択**: tool_filter による最小権限実装

#### エンタープライズ対応パターン
```python
# 監査ログ付きエージェント
def create_audited_bigquery_agent(audit_config: dict):
    """監査機能付きBigQueryエージェント"""
    
    def audit_callback(callback_context):
        # 全操作をログに記録
        operation = callback_context.get("operation")
        user = callback_context.get("user")
        timestamp = datetime.now().isoformat()
        
        audit_log = {
            "timestamp": timestamp,
            "user": user,
            "operation": operation,
            "project": callback_context.get("project_id")
        }
        
        # 監査ログの保存
        save_audit_log(audit_log, audit_config["log_destination"])
    
    return Agent(
        name="audited_bigquery_agent",
        tools=[bigquery_toolset],
        before_tool_callback=audit_callback,
        after_tool_callback=audit_callback
    )
```

### 7.2 セキュリティベストプラクティス

#### 認証情報の安全な管理
```python
# プロダクション環境での設定例
class SecureBigQueryConfig:
    def __init__(self):
        # 環境変数ではなくSecret Managerを使用
        self.client_id = self.get_secret("oauth-client-id")
        self.client_secret = self.get_secret("oauth-client-secret")
    
    def get_secret(self, secret_name: str) -> str:
        """Google Secret Manager からシークレットを取得"""
        from google.cloud import secretmanager
        
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
```

#### データアクセス制御
```python
# ロールベースアクセス制御
def create_rbac_bigquery_agent(user_role: str):
    """ロールベースのアクセス制御を適用したエージェント"""
    
    role_permissions = {
        "analyst": ["bigquery_datasets_list", "bigquery_tables_list"],
        "developer": ["bigquery_datasets_list", "bigquery_tables_list", 
                     "bigquery_tables_get", "bigquery_datasets_get"],
        "admin": ["bigquery_datasets_list", "bigquery_datasets_get", 
                 "bigquery_datasets_insert", "bigquery_tables_list",
                 "bigquery_tables_get", "bigquery_tables_insert"]
    }
    
    allowed_tools = role_permissions.get(user_role, [])
    
    return BigQueryToolset(
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        tool_filter=allowed_tools
    )
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **最小権限の原則**: 必要最小限のツールのみを公開
- **監査ログ**: 全操作の記録とトレーサビリティ確保
- **エラーハンドリング**: 適切なエラー処理とユーザーフィードバック
- **コスト監視**: BigQuery 使用量の定期的な監視

#### 注意点
- **認証情報の保護**: OAuth認証情報の安全な管理
- **権限管理**: 過度な権限付与の回避
- **コスト制御**: 大量データ処理時のコスト注意
- **プライバシー**: ユーザーデータの適切な取り扱い

### 7.4 他のプロジェクトへの応用

#### データプラットフォーム構築
```python
class DataPlatformOrchestrator:
    """データプラットフォーム統合システム"""
    
    def __init__(self):
        self.bigquery_agent = create_bigquery_agent()
        self.storage_agent = create_storage_agent()
        self.dataflow_agent = create_dataflow_agent()
    
    async def setup_data_pipeline(self, pipeline_config: dict):
        """データパイプラインの自動セットアップ"""
        # 1. BigQuery データセット作成
        await self.bigquery_agent.create_dataset(pipeline_config["dataset"])
        
        # 2. Cloud Storage バケット作成
        await self.storage_agent.create_bucket(pipeline_config["bucket"])
        
        # 3. Dataflow ジョブ作成
        await self.dataflow_agent.create_job(pipeline_config["job"])
```

この bigquery_agent は、Google BigQuery との企業レベルの統合実装を学ぶのに最適な例です。OAuth2 認証、ツールフィルタリング、エンタープライズ統合パターンなど、実用的なシステム構築に必要な要素を包括的に学習できます。