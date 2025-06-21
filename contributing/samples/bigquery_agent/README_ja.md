# BigQuery サンプル

## はじめに

このサンプルは、2つのツールを通じてADKのBigQueryサポートをテストおよびデモンストレーションします：

* 1. bigquery_datasets_list:

    ユーザーのデータセットを一覧表示します。

* 2. bigquery_datasets_get:
    データセットの詳細を取得します。

* 3. bigquery_datasets_insert:
    新しいデータセットを作成します。

* 4. bigquery_tables_list:
    データセット内のすべてのテーブルを一覧表示します。

* 5. bigquery_tables_get:
    テーブルの詳細を取得します。

* 6. bigquery_tables_insert:
    データセットに新しいテーブルを挿入します。

## 使用方法

* 1. https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name. に従って、クライアントIDとクライアントシークレットを取得します。
  クライアントタイプとして「web」を選択してください。

* 2. `.env`ファイルを設定して2つの変数を追加します：

  * OAUTH_CLIENT_ID={your client id}
  * OAUTH_CLIENT_SECRET={your client secret}

  注：別の`.env`ファイルを作成しないでください。代わりに、Vertex AIまたはDev ML認証情報を保存する同じ`.env`ファイルに追加してください

* 3. https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred に従って、http://localhost/dev-ui/ を「承認済みリダイレクトURI」に追加します。

  注：ここでのlocalhostは、dev uiにアクセスするために使用するホスト名にすぎません。dev uiにアクセスするために使用する実際のホスト名に置き換えてください。

* 4. 初回実行時に、ChromeでlocalhostのポップアップをAllowにします。

## サンプルプロンプト

* `Do I have any datasets in project sean-dev-agent ?`
* `Do I have any tables under it ?`
* `could you get me the details of this table ?`
* `Can you help to create a new dataset in the same project? id : sean_test , location: us`
* `could you show me the details of this new dataset ?`
* `could you create a new table under this dataset ? table name : sean_test_table. column1 : name is id , type is integer, required. column2 : name is info , type is string, required. column3 : name is backup , type is string, optional.`