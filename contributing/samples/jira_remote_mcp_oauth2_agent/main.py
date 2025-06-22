"""Jira Remote MCP OAuth2 エージェントのテスト用メインエントリーポイント。"""

import asyncio
import sys
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from google.adk.runner import run_agent
from agent import agent


async def main():
    """エージェントをインタラクティブモードで実行する。"""
    print("""Starting Jira Remote MCP OAuth2 Agent...

Required OAuth2 Configuration:
  - JIRA_DOMAIN
  - JIRA_EMAIL
  - JIRA_OAUTH_CLIENT_ID
  - JIRA_OAUTH_CLIENT_SECRET
  - JIRA_OAUTH_REDIRECT_URI (default: http://localhost:8080/callback)

Make sure your OAuth2 app is configured in the Atlassian Developer Console.

Type 'exit' to quit.
""")
    
    # エージェントを実行
    await run_agent(agent)


if __name__ == "__main__":
    asyncio.run(main())