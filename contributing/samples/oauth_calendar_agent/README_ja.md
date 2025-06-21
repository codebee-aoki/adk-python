# OAuth サンプル

## はじめに

このサンプルは、2つのツールを通じてADKのOAuthサポートをテストおよびデモンストレーションします：

* 1. list_calendar_events

  これは、Google Calendar APIを呼び出してカレンダーイベントを一覧表示するカスタマイズされたツールです。
  クライアントIDとクライアントシークレットをADKに渡し、ADKからアクセストークンを取得します。
  その後、アクセストークンを使用してカレンダーAPIを呼び出します。

* 2. get_calendar_events

  これは、Google Calendar APIを呼び出して特定のカレンダーの詳細を取得するGoogle Calendarツールです。
  このツールは、ADKの内蔵Google Calendar ToolSetからのものです。
  すべてがラップされており、ツールユーザーはクライアントIDとクライアントシークレットを渡すだけで済みます。

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

* `List all my today's meeting from 7am to 7pm.`
* `Get the details of the first event.`