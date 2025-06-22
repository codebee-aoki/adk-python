"""Jira Remote MCP API キーエージェントのテスト用メインエントリーポイント。"""

import asyncio
import sys
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from google.adk.runner import run_agent
from agent import agent


async def main():
    """エージェントをインタラクティブモードで実行する。"""
    print("""Starting Jira Remote MCP API Key Agent...
Make sure you have configured your .env file with:
  - JIRA_DOMAIN
  - JIRA_EMAIL
  - JIRA_API_TOKEN

Type 'exit' to quit.
""")
    
    # エージェントを実行
    await run_agent(agent)


if __name__ == "__main__":
    asyncio.run(main())