# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Jira MCP Agent - mcp-atlassian を使用したシンプルな Jira 統合.

このエージェントは mcp-atlassian MCP サーバーと ADK の MCPToolset を使用して
Jira との統合を実現します。独自実装なしで、mcp-atlassian の豊富な機能を活用します。
"""

import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.base.external_tools.mcp import StdioServerParameters

# 環境変数の読み込み
load_dotenv()

# 設定の検証
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_USERNAME = os.getenv("JIRA_USERNAME", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
  raise ValueError(
      "必要な環境変数が不足しています。JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN を .env ファイルに設定してください。"
  )

# MCPToolset でmcp-atlassian サーバーに接続
jira_mcp_tools = MCPToolset(
    connection_params=StdioServerParameters(
        command='docker',
        args=[
            'run', '--rm', '-i',
            '--env', f'JIRA_URL={JIRA_URL}',
            '--env', f'JIRA_USERNAME={JIRA_USERNAME}',
            '--env', f'JIRA_API_TOKEN={JIRA_API_TOKEN}',
            '-v', f'{os.path.expanduser("~")}/.mcp-atlassian:/home/app/.mcp-atlassian',
            'ghcr.io/sooperset/mcp-atlassian:latest'
        ]
    )
)

# エージェントを作成
root_agent = Agent(
    name="jira_mcp_agent",
    model="gemini-2.0-flash",
    instruction="""あなたは mcp-atlassian を使用する Jira プロジェクト管理アシスタントです。

利用可能な機能:
1. Jira 課題の検索とフィルタリング
2. 課題の詳細情報取得
3. 新規課題の作成
4. 課題へのコメント追加
5. 課題の更新と状態変更
6. 高度なJQL (Jira Query Language) クエリ実行

使用可能なツールは mcp-atlassian によって提供され、以下のような操作が可能です:
- スマートな課題フィルタリング
- 自動的な課題更新
- プロジェクト情報の取得
- ユーザー情報の検索

常に明確で整理された情報を提供し、Jira の豊富な機能を活用してユーザーのプロジェクト管理を支援してください。
""",
    tools=[jira_mcp_tools],
)