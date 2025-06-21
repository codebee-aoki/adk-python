# Application Integration Agent サンプル

## はじめに

このサンプルは、ADK agent内で`ApplicationIntegrationToolset`を使用して外部アプリケーション（この場合はJira）と対話する方法を示しています。agent（`agent.py`）は、事前設定されたApplication Integration接続を使用してJiraのissueを管理するように構成されています。

## 前提条件

1.  **Integration接続のセットアップ:**
    *   Jiraインスタンスと対話するために、既存の[Integration接続](https://cloud.google.com/integration-connectors/docs/overview)が設定されている必要があります。Google CloudでIntegration Connectorをプロビジョニングするには[ドキュメント](https://google.github.io/adk-docs/tools/google-cloud-tools/#use-integration-connectors)に従い、その後、JIRA接続を作成するには[このドキュメント](https://cloud.google.com/integration-connectors/docs/connectors/jiracloud/configure)を使用してください。接続の`Connection Name`、`Project ID`、`Location`をメモしてください。
    * 

2.  **環境変数の設定:**
    *   `agent.py`と同じディレクトリに`.env`ファイルを作成します（または既存のファイルに追加します）。
    *   次の変数を`.env`ファイルに追加し、プレースホルダーの値を実際の接続詳細に置き換えます：

      ```dotenv
      CONNECTION_NAME=<YOUR_JIRA_CONNECTION_NAME>
      CONNECTION_PROJECT=<YOUR_GOOGLE_CLOUD_PROJECT_ID>
      CONNECTION_LOCATION=<YOUR_CONNECTION_LOCATION>
      ```

## 使用方法

1.  **依存関係のインストール:** 必要なライブラリ（例：`google-adk`、`python-dotenv`）がインストールされていることを確認します。
2.  **Agentの実行:** ターミナルからagentスクリプトを実行します：
    ```bash
    python agent.py
    ```
3.  **対話:** agentが開始したら、Jira issue管理に関連するプロンプトを入力して対話できます。

## サンプルプロンプト

agentとの対話方法の例を以下に示します：

*   `Can you list me all the issues ?`
*   `Can you list me all the projects ?`
*   `Can you create an issue: "Bug in product XYZ" in project ABC ?`