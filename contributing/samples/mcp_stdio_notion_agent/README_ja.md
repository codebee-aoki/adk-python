# Notion MCP Agent

これは、Notion MCPツールを使用してNotion APIを呼び出すagentです。Notion APIキーの渡し方を示しています。

使用するには以下の手順に従ってください：

* 以下のページのインストール手順に従って、Notion APIのAPIキーを取得してください：
https://www.npmjs.com/package/@notionhq/notion-mcp-server

* 前の手順で取得したAPIキーを環境変数`NOTION_API_KEY`に設定してください。

```bash
export NOTION_API_KEY=<your_notion_api_key>
```

* ADK Web UIでagentを実行してください

* 以下のクエリを送信してください：
  * What can you do for me ?
  * Seach `XXXX` in my pages.