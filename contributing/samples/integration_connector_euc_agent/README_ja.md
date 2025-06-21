# エンドユーザー認証情報を使用したApplication Integration Agent サンプル

## はじめに

このサンプルは、ADK agent内で`ApplicationIntegrationToolset`を使用して、**エンドユーザーOAuth 2.0認証情報**を使用して外部アプリケーションと対話する方法を示しています。具体的には、このagent（`agent.py`）は、事前設定されたApplication Integration接続を使用し、エンドユーザーとして認証してGoogle Calendarと対話するように構成されています。

## 前提条件

1.  **Integration接続のセットアップ:**
    *   Google Calendar APIと対話するように設定された、既存の
        [Integration接続](https://cloud.google.com/integration-connectors/docs/overview)
        が必要です。Google CloudでIntegration Connectorをプロビジョニングするには、
        [ドキュメント](https://google.github.io/adk-docs/tools/google-cloud-tools/#use-integration-connectors)
        に従ってください。接続の`Connection Name`、`Project ID`、`Location`が必要になります。
    *   接続がGoogle Calendarを使用するように設定されていることを確認してください（例：`google-calendar-connector`または類似のコネクターを有効にする）。

2.  **OAuth 2.0クライアントの設定:**
    *   必要なGoogle Calendarスコープ（例：
        `https://www.googleapis.com/auth/calendar.readonly`）にアクセスする権限を持つOAuth 2.0クライアントIDとクライアントシークレットが必要です。Google Cloud Consoleの「APIs & Services」
        -> 「Credentials」でOAuth認証情報を作成できます。

3.  **環境変数の設定:**
    *   `agent.py`と同じディレクトリに`.env`ファイルを作成します（または
        既存のファイルに追加します）。
    *   次の変数を`.env`ファイルに追加し、プレースホルダーの値を
        実際の接続詳細に置き換えます：

      ```dotenv
      CONNECTION_NAME=<YOUR_CALENDAR_CONNECTION_NAME>
      CONNECTION_PROJECT=<YOUR_GOOGLE_CLOUD_PROJECT_ID>
      CONNECTION_LOCATION=<YOUR_CONNECTION_LOCATION>
      CLIENT_ID=<YOUR_OAUTH_CLIENT_ID>
      CLIENT_SECRET=<YOUR_OAUTH_CLIENT_SECRET>
      ```

## エンドユーザー認証（OAuth 2.0）

このagentは、認証を処理するためにADKの`AuthCredential`と`OAuth2Auth`クラスを使用します。
*   Google CloudのOAuthエンドポイントと必要なスコープに基づいてOAuth 2.0スキーム（`oauth2_scheme`）を定義します。
*   環境変数（またはサンプルのハードコードされた値）から`CLIENT_ID`と`CLIENT_SECRET`を使用して`OAuth2Auth`を設定します。
*   この`AuthCredential`は`ApplicationIntegrationToolset`に渡され、
    ツールがagentを実行しているユーザーの代わりにGoogle Calendarに対して認証されたAPI呼び出しを行うことを可能にします。ADKフレームワークは通常、
    ツールが最初に呼び出されたときにOAuthフロー（例：ユーザーに同意を求める）を処理します。

## 使用方法

1.  **依存関係のインストール:** 必要なライブラリ（例：`google-adk`、`python-dotenv`）がインストールされていることを確認します。
2.  **Agentの実行:** ターミナルからagentスクリプトを実行します：
    ```bash
    python agent.py
    ```
3.  **対話:** agentが開始したら、対話できます。OAuthが必要なツールを初めて使用する場合、ブラウザでOAuth同意フローを通る必要があるかもしれません。認証が成功した後、agentにタスクの実行を依頼できます。

## サンプルプロンプト

agentとの対話方法の例を以下に示します：

*   `Can you list events from my primary calendar?`