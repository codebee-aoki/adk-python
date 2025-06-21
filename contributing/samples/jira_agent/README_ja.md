このagentは、Google Application IntegrationワークフローとIntegrations Connectorを使用してJira Cloudに接続します

**agentに接続するための手順:**

**Integration Connectorsの使用**

[Integration Connectors](https://cloud.google.com/integration-connectors/docs/overview)を使用してagentをエンタープライズアプリケーションに接続します。

**ステップ:**

1. Integration Connectorsからコネクターを使用するには、「QUICK SETUP」ボタンをクリックして、接続と同じリージョンで[Application Integrationをプロビジョニング](https://console.cloud.google.com/)する必要があります。
Google Cloud Tools
![image_alt](https://github.com/karthidec/adk-python/blob/adk-samples-jira-agent/contributing/samples/jira_agent/image-application-integration.png?raw=true)

2. テンプレートライブラリから[Connection Tool]((https://console.cloud.google.com/))テンプレートに移動し、「USE TEMPLATE」ボタンをクリックします。
![image_alt](https://github.com/karthidec/adk-python/blob/adk-samples-jira-agent/contributing/samples/jira_agent/image-connection-tool.png?raw=true)

3. Integration Nameを**ExecuteConnection**として入力し（このintegration名のみを使用することが必須です）、接続リージョンと同じリージョンを選択します。「CREATE」をクリックします。

4. Application Integration Editorで「PUBLISH」ボタンを使用してintegrationを公開します。
![image_alt](https://github.com/karthidec/adk-python/blob/adk-samples-jira-agent/contributing/samples/jira_agent/image-app-intg-editor.png?raw=true)

**参考資料:**

https://google.github.io/adk-docs/tools/google-cloud-tools/#application-integration-tools