# bigquery - 技術ドキュメント

## 1. エージェント概要

### 目的と用途
`bigquery` エージェントは、ADK で Google BigQuery サービスとの統合を学習するためのサンプル実装です。複数の認証方法をサポートし、BigQuery でのデータ分析、SQL クエリ実行、モデル管理を可能にするエージェントです。

### 主要機能
- **BigQuery SQL 実行**: データセットに対する SQL クエリの実行
- **多様な認証方法**: OAuth2、Service Account、Application Default Credentials
- **データ分析**: BigQuery データに対する AI による分析と回答
- **モデル管理**: BigQuery ML モデルとの連携機能

### 対象ユースケース
- Google Cloud BigQuery との統合学習
- エンタープライズデータ分析 AI エージェント
- 複数認証方法の実装パターン
- クラウドサービス統合のベストプラクティス

## 2. アーキテクチャ解析

### 全体アーキテクチャ
```
[ユーザー] 
    ↓ (データ分析質問)
[hello_agent] 
    ↓ (BigQuery ツール使用)
[BigQueryToolset]
    ↓ (認証・接続)
┌─────────────────┬─────────────────┬─────────────────┐
│ OAuth2          │ Service Account │ Default Creds   │
│ (Interactive)   │ (Key File)      │ (Environment)   │
└─────────────────┴─────────────────┴─────────────────┘
    ↓ (Google Cloud API)
[Google BigQuery Service]
    ├── データセット管理
    ├── SQL クエリ実行  
    ├── ML モデル管理
    └── 結果取得・分析
```

### 認証フロー
```
[認証方式選択]
├── OAUTH2 (CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2)
│   ├── OAUTH_CLIENT_ID 環境変数
│   ├── OAUTH_CLIENT_SECRET 環境変数
│   └── インタラクティブ OAuth フロー
├── SERVICE_ACCOUNT (AuthCredentialTypes.SERVICE_ACCOUNT)
│   ├── service_account_key.json ファイル
│   └── google.auth.load_credentials_from_file()
└── DEFAULT (上記以外)
    └── google.auth.default() - ADC 使用
```

### コンポーネント構成
- **メインエージェント**: `root_agent` (llm_agent.Agent)
- **BigQuery ツールセット**: `BigQueryToolset` - 包括的な BigQuery 操作
- **認証設定**: `BigQueryCredentialsConfig` - 柔軟な認証管理
- **ツール設定**: `BigQueryToolConfig` - 実行権限とモード設定

### 依存関係
```python
# ADK BigQuery 統合
from google.adk.agents import llm_agent
from google.adk.auth import AuthCredentialTypes
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode

# Google 認証ライブラリ
import google.auth
```

## 3. コード詳細解説

### 3.1 認証設定の実装

#### 認証方式の選択
```python
# Define an appropriate credential type
CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2
```

#### OAuth2 認証（インタラクティブ）
```python
if CREDENTIALS_TYPE == AuthCredentialTypes.OAUTH2:
  # Initiaze the tools to do interactive OAuth
  # The environment variables OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET
  # must be set
  credentials_config = BigQueryCredentialsConfig(
      client_id=os.getenv("OAUTH_CLIENT_ID"),
      client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
  )
```

**重要ポイント:**
- ユーザー操作による認証フロー
- ブラウザベースの OAuth 認証
- 開発・テスト環境に適している

#### Service Account 認証（サービス間）
```python
elif CREDENTIALS_TYPE == AuthCredentialTypes.SERVICE_ACCOUNT:
  # Initialize the tools to use the credentials in the service account key.
  # If this flow is enabled, make sure to replace the file path with your own
  # service account key file
  # https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys
  creds, _ = google.auth.load_credentials_from_file("service_account_key.json")
  credentials_config = BigQueryCredentialsConfig(credentials=creds)
```

**重要ポイント:**
- 自動化された認証フロー
- プロダクション環境に適している
- サービス間認証に使用

#### Application Default Credentials（推奨）
```python
else:
  # Initialize the tools to use the application default credentials.
  # https://cloud.google.com/docs/authentication/provide-credentials-adc
  application_default_credentials, _ = google.auth.default()
  credentials_config = BigQueryCredentialsConfig(
      credentials=application_default_credentials
  )
```

**重要ポイント:**
- 環境に応じた自動認証
- Google Cloud 環境で推奨
- 設定ファイル不要

### 3.2 BigQuery ツール設定

#### ツール設定の構成
```python
# Define BigQuery tool config
tool_config = BigQueryToolConfig(write_mode=WriteMode.ALLOWED)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, 
    bigquery_tool_config=tool_config
)
```

**WriteMode の選択肢:**
- `WriteMode.ALLOWED`: 読み書き両方を許可
- `WriteMode.READ_ONLY`: 読み取り専用
- `WriteMode.DISABLED`: BigQuery 書き込み無効

### 3.3 エージェント設定

```python
# The variable name `root_agent` determines what your root agent is for the
# debug CLI
root_agent = llm_agent.Agent(
    model="gemini-2.0-flash",
    name="hello_agent",
    description=(
        "Agent to answer questions about BigQuery data and models and execute"
        " SQL queries."
    ),
    instruction="""\
        You are a data science agent with access to several BigQuery tools.
        Make use of those tools to answer the user's questions.
    """,
    tools=[bigquery_toolset],
)
```

**設計の特徴:**
- データサイエンス特化のエージェント
- SQL クエリ実行とデータ分析機能
- シンプルで明確な指示

## 4. 設定・環境構築

### 4.1 Google Cloud プロジェクト設定

#### プロジェクトの準備
```bash
# Google Cloud CLI のインストール
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# プロジェクトの設定
gcloud config set project YOUR_PROJECT_ID

# BigQuery API の有効化
gcloud services enable bigquery.googleapis.com
```

### 4.2 認証方式別セットアップ

#### OAuth2 認証の設定
```bash
# Google Cloud Console で OAuth2 クライアントを作成
# https://console.cloud.google.com/apis/credentials

# 環境変数の設定
export OAUTH_CLIENT_ID=your_oauth_client_id
export OAUTH_CLIENT_SECRET=your_oauth_client_secret
```

#### Service Account 認証の設定
```bash
# Service Account の作成
gcloud iam service-accounts create bigquery-agent \
    --display-name="BigQuery Agent Service Account"

# 必要な権限の付与
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

# キーファイルの生成
gcloud iam service-accounts keys create service_account_key.json \
    --iam-account=bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### Application Default Credentials の設定
```bash
# 開発環境での設定
gcloud auth application-default login

# または環境変数で Service Account を指定
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account_key.json
```

### 4.3 依存関係とインストール

```bash
# 基本インストール
pip install google-adk[bigquery]

# または個別インストール
pip install google-adk
pip install google-cloud-bigquery
pip install google-auth
```

### 4.4 BigQuery データセットの準備

#### サンプルデータセットの作成
```sql
-- BigQuery コンソールで実行
CREATE SCHEMA IF NOT EXISTS sample_dataset;

CREATE OR REPLACE TABLE sample_dataset.sales_data (
  id INT64,
  product_name STRING,
  sales_amount NUMERIC,
  sale_date DATE,
  region STRING
);

INSERT INTO sample_dataset.sales_data VALUES
  (1, 'Product A', 1000.50, '2024-01-15', 'North'),
  (2, 'Product B', 750.25, '2024-01-16', 'South'),
  (3, 'Product C', 1250.75, '2024-01-17', 'East');
```

### 4.5 実行方法

```bash
# CLI での実行
adk run contributing/samples/bigquery

# Web UI での実行
adk web contributing/samples/bigquery
```

## 5. 使用パターンと拡張

### 5.1 基本的な使用例

#### データ探索
```
ユーザー: "What tables are available in my BigQuery project?"
エージェント: [BigQuery ツールでメタデータ取得] "You have the following datasets: sample_dataset, analytics_data..."
```

#### SQL クエリ実行
```
ユーザー: "Show me the total sales by region"
エージェント: [SQL クエリ実行]
SELECT region, SUM(sales_amount) as total_sales 
FROM sample_dataset.sales_data 
GROUP BY region
結果: "North: $1000.50, South: $750.25, East: $1250.75"
```

#### データ分析
```
ユーザー: "What insights can you provide about our sales data?"
エージェント: [複数クエリ実行して分析] "Based on your sales data, I found that..."
```

### 5.2 高度な設定パターン

#### プロジェクト固有の設定
```python
def create_project_specific_agent(project_id: str, dataset_id: str):
    tool_config = BigQueryToolConfig(
        write_mode=WriteMode.READ_ONLY,
        default_project=project_id,
        default_dataset=dataset_id
    )
    
    credentials_config = BigQueryCredentialsConfig(
        # 認証設定...
    )
    
    bigquery_toolset = BigQueryToolset(
        credentials_config=credentials_config,
        bigquery_tool_config=tool_config
    )
    
    return llm_agent.Agent(
        model="gemini-2.0-flash",
        name=f"agent_{project_id}",
        instruction=f"You are specialized in analyzing data from {dataset_id} dataset in {project_id} project.",
        tools=[bigquery_toolset],
    )
```

#### 権限制限のある設定
```python
# 読み取り専用エージェント
readonly_config = BigQueryToolConfig(write_mode=WriteMode.READ_ONLY)

# 特定のデータセットのみアクセス
limited_credentials = BigQueryCredentialsConfig(
    # Service Account with limited permissions
    credentials=limited_service_account_creds
)

secure_agent = llm_agent.Agent(
    tools=[BigQueryToolset(
        credentials_config=limited_credentials,
        bigquery_tool_config=readonly_config
    )],
    instruction="You can only read data. Never attempt to modify or delete data.",
    # ...
)
```

### 5.3 データパイプライン統合

#### ETL パイプライン支援エージェント
```python
def create_etl_agent():
    etl_config = BigQueryToolConfig(
        write_mode=WriteMode.ALLOWED,
        enable_legacy_sql=False,
        job_timeout_ms=300000  # 5分
    )
    
    return llm_agent.Agent(
        name="etl_agent",
        instruction="""
        You are an ETL pipeline assistant. You can:
        1. Create and manage BigQuery tables
        2. Execute data transformation queries
        3. Validate data quality
        4. Generate reports on data processing status
        """,
        tools=[BigQueryToolset(
            credentials_config=credentials_config,
            bigquery_tool_config=etl_config
        )],
    )
```

### 5.4 機械学習統合

#### BigQuery ML エージェント
```python
def create_ml_agent():
    ml_config = BigQueryToolConfig(
        write_mode=WriteMode.ALLOWED,
        enable_ml_functions=True
    )
    
    return llm_agent.Agent(
        name="bq_ml_agent",
        instruction="""
        You are a BigQuery ML specialist. You can:
        1. Create and train ML models using BigQuery ML
        2. Make predictions using existing models
        3. Evaluate model performance
        4. Export models for external use
        """,
        tools=[BigQueryToolset(
            credentials_config=credentials_config,
            bigquery_tool_config=ml_config
        )],
    )
```

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決法

#### エラー: "Access Denied: Project not found"
**原因**: プロジェクト ID が間違っているか、権限がない
**解決法**: プロジェクトと権限の確認
```bash
# 現在のプロジェクト確認
gcloud config get-value project

# プロジェクトの権限確認
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

#### エラー: "OAuth2 client credentials not found"
**原因**: OAuth2 設定が不完全
**解決法**: 環境変数の確認
```bash
# 環境変数の確認
echo $OAUTH_CLIENT_ID
echo $OAUTH_CLIENT_SECRET

# .env ファイルの確認
cat .env | grep OAUTH
```

#### エラー: "BigQuery API not enabled"
**原因**: BigQuery API が有効化されていない
**解決法**: API の有効化
```bash
# API 有効化
gcloud services enable bigquery.googleapis.com

# 有効な API の確認
gcloud services list --enabled
```

### 6.2 権限の問題

#### 最小権限の設定
```bash
# BigQuery データ閲覧者（読み取り専用）
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:your-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

# BigQuery ユーザー（クエリ実行）
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:your-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.user"
```

### 6.3 パフォーマンス最適化

#### クエリ最適化
```python
# クエリタイムアウト設定
optimized_config = BigQueryToolConfig(
    write_mode=WriteMode.READ_ONLY,
    job_timeout_ms=30000,  # 30秒
    max_results=1000       # 結果行数制限
)

# コスト制御
cost_controlled_config = BigQueryToolConfig(
    maximum_bytes_billed=100000000,  # 100MB制限
    use_query_cache=True,
    dry_run=False  # 実際の実行前にコスト確認
)
```

## 7. 開発者向けベストプラクティス

### 7.1 このエージェントから学べるパターン

#### 多様な認証方法の実装
- 環境に応じた適切な認証方式の選択
- 設定の外部化と環境変数の活用
- セキュリティベストプラクティス

#### エンタープライズ統合パターン
```python
# 設定の抽象化
class BigQueryAgentFactory:
    @staticmethod
    def create_for_environment(env: str):
        if env == "development":
            return BigQueryAgentFactory.create_development_agent()
        elif env == "production":
            return BigQueryAgentFactory.create_production_agent()
        else:
            raise ValueError(f"Unknown environment: {env}")
    
    @staticmethod
    def create_development_agent():
        return llm_agent.Agent(
            tools=[BigQueryToolset(
                credentials_config=BigQueryCredentialsConfig(
                    client_id=os.getenv("DEV_OAUTH_CLIENT_ID"),
                    client_secret=os.getenv("DEV_OAUTH_CLIENT_SECRET"),
                ),
                bigquery_tool_config=BigQueryToolConfig(
                    write_mode=WriteMode.READ_ONLY
                )
            )],
            # ...
        )
```

### 7.2 セキュリティのベストプラクティス

#### 権限の最小化
```python
# 役割ベースの権限設定
class RoleBasedBigQueryAgent:
    ROLE_PERMISSIONS = {
        "analyst": WriteMode.READ_ONLY,
        "developer": WriteMode.ALLOWED,
        "admin": WriteMode.ALLOWED
    }
    
    def create_agent_for_role(self, role: str, user_credentials):
        write_mode = self.ROLE_PERMISSIONS.get(role, WriteMode.READ_ONLY)
        
        return llm_agent.Agent(
            tools=[BigQueryToolset(
                credentials_config=BigQueryCredentialsConfig(
                    credentials=user_credentials
                ),
                bigquery_tool_config=BigQueryToolConfig(
                    write_mode=write_mode
                )
            )],
            instruction=f"You are operating as a {role}. Follow the principle of least privilege.",
        )
```

### 7.3 推奨事項と注意点

#### 推奨事項
- **環境別設定**: 開発・本番環境での異なる認証方式
- **権限最小化**: 必要最小限の BigQuery 権限
- **エラーハンドリング**: BigQuery 固有のエラーへの対応
- **コスト監視**: クエリコストとリソース使用量の追跡

#### 注意点
- **認証情報**: OAuth クライアント情報の適切な管理
- **クエリコスト**: 大量データ処理でのコスト発生
- **権限管理**: 過剰な権限付与のリスク
- **データプライバシー**: 機密データへのアクセス制御

### 7.4 他のプロジェクトへの応用

#### データ分析プラットフォーム
```python
class DataAnalyticsPlatform:
    def __init__(self):
        self.bigquery_agent = self.create_bigquery_agent()
        self.visualization_agent = self.create_visualization_agent()
        
    def create_comprehensive_analysis_agent(self):
        return llm_agent.Agent(
            name="data_platform_agent",
            instruction="""
            You are a comprehensive data analysis platform. You can:
            1. Query and analyze data using BigQuery
            2. Create visualizations and reports
            3. Provide business insights and recommendations
            4. Automate data pipeline tasks
            """,
            tools=[
                self.bigquery_agent.tools[0],  # BigQuery ツール
                # 他の分析ツール...
            ]
        )
```

この bigquery エージェントは、Google Cloud の企業級データ分析サービスとの統合パターンを学ぶのに最適なサンプルです。特に複数の認証方式と権限管理の実装は、プロダクション環境での AI エージェント開発に直接応用できる重要なパターンです。