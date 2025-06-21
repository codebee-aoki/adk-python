# BigQuery Tools サンプル

## はじめに

このサンプルagentは、`google.adk.tools.bigquery`モジュール経由で配布されるADKのBigQueryファーストパーティツールを示しています。これらのツールには以下が含まれます：

1. `list_dataset_ids`

  GCPプロジェクトに存在するBigQueryデータセットIDを取得します。

1. `get_dataset_info`

  BigQueryデータセットに関するメタデータを取得します。

1. `list_table_ids`

  BigQueryデータセットに存在するテーブルIDを取得します。

1. `get_table_info`

  BigQueryテーブルに関するメタデータを取得します。

1. `execute_sql`

  BigQueryでSQLクエリを実行します。

## 使用方法

agentのLLMサービスに[Google AI Studio](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-ai-studio)
または
[Google Cloud Vertex AI](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai)
を使用するために、`.env`ファイルで環境変数を設定します。例えば、Google AI Studioを使用する場合は以下を設定します：

* GOOGLE_GENAI_USE_VERTEXAI=FALSE
* GOOGLE_API_KEY={your api key}

### Application Default Credentialsを使用する場合

このモードは、agent構築者がagentと対話する唯一のユーザーである場合の迅速な開発に便利です。ツールはこれらの認証情報で実行されます。

1. agentが実行されるマシンでアプリケーションデフォルト認証情報を作成します。https://cloud.google.com/docs/authentication/provide-credentials-adc に従ってください。

1. `agent.py`で`CREDENTIALS_TYPE=None`を設定します

1. agentを実行します

### サービスアカウントキーを使用する場合

このモードは、agent構築者がサービスアカウント認証情報でagentを実行したい場合の迅速な開発に便利です。ツールはこれらの認証情報で実行されます。

1. https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys に従ってサービスアカウントキーを作成します。

1. `agent.py`で`CREDENTIALS_TYPE=AuthCredentialTypes.SERVICE_ACCOUNT`を設定します

1. キーファイルをダウンロードし、`"service_account_key.json"`をパスに置き換えます

1. agentを実行します

### 対話型OAuthを使用する場合

1. https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name.
に従って、クライアントIDとクライアントシークレットを取得します。クライアントタイプとして「web」を選択してください。

1. https://developers.google.com/workspace/guides/configure-oauth-consent に従って、スコープ"https://www.googleapis.com/auth/bigquery"を追加します。

1. https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred に従って、http://localhost/dev-ui/ を「承認済みリダイレクトURI」に追加します。

  注：ここでのlocalhostは、dev uiにアクセスするために使用するホスト名にすぎません。
  dev uiにアクセスするために使用する実際のホスト名に置き換えてください。

1. 初回実行時に、ChromeでlocalhostのポップアップをAllowにします。

1. agentを実行する前に、`.env`ファイルを設定して2つの変数を追加します：

  * OAUTH_CLIENT_ID={your client id}
  * OAUTH_CLIENT_SECRET={your client secret}

  注：別の.envを作成しないでください。代わりに、Vertex AIまたはDev ML認証情報を保存する同じ.envファイルに追加してください

1. `agent.py`で`CREDENTIALS_TYPE=AuthCredentialTypes.OAUTH2`を設定し、agentを実行します

## サンプルプロンプト

* which weather datasets exist in bigquery public data?
* tell me more about noaa_lightning
* which tables exist in the ml_datasets dataset?
* show more details about the penguins table
* compute penguins population per island.