"""Jira Remote MCP API キーエージェント。

このエージェントは API キー認証を使用して Atlassian のリモート MCP サーバーに接続します。
MCP プロトコルを通じて公開されるすべての Jira 操作へのアクセスを提供します。
"""

import os
import sys
from pathlib import Path

# インポート用に親ディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from google.adk import Agent
from google.adk.toolbox.mcp import MCPToolset, SseConnectionParams
from google.adk.errors import ConfigurationError as ADKConfigError

# 共通ユーティリティをインポート
sys.path.append(str(Path(__file__).parent.parent))
from jira_remote_mcp_common import (
    JiraConfig,
    create_basic_auth_header,
    setup_logging,
    ConfigurationError
)


def create_jira_mcp_agent() -> Agent:
    """API キー認証で Atlassian のリモート MCP サーバーを使用する Jira エージェントを作成する。
    
    Returns:
        設定されたエージェントインスタンス
        
    Raises:
        ConfigurationError: 必要な環境変数が不足している場合
    """
    logger = setup_logging("jira_mcp_apikey_agent")
    
    try:
        # 環境変数から設定を読み込む
        config = JiraConfig.from_env()
        config.validate_for_api_key()
        
        logger.info(f"Configuring Jira MCP agent for domain: {config.jira_domain}")
        
        # 認証ヘッダーを作成
        auth_headers = create_basic_auth_header(config)
        
        # SSE 接続パラメータを設定
        connection_params = SseConnectionParams(
            url=config.mcp_server_url,
            headers=auth_headers,
            timeout=config.connection_timeout
        )
        
        # MCP ツールセットを作成
        mcp_toolset = MCPToolset(
            connection_params=connection_params,
            tool_filter=None  # 利用可能なすべてのツールを含める
        )
        
        # エージェントを作成
        agent = Agent(
            name="Jira Remote MCP API Key Agent",
            description="""
                Atlassian のリモート MCP サーバーを使用して Jira Cloud と対話する AI エージェントです。
                API キー（Basic 認証）で認証されます。課題管理、プロジェクト管理、
                JQL 検索を含むすべての Jira 操作を実行できます。
            """,
            instruction=f"""
                あなたは {config.jira_domain} に接続された便利な Jira アシスタントです。
                以下のような作業でユーザーを支援できます：
                - 課題の作成、更新、検索
                - プロジェクトとワークフローの管理
                - JQL クエリの実行
                - プロジェクトデータの分析
                - Jira タスクの自動化

                実行するアクションについては常に明確に説明し、重要な変更を行う前には
                確認を求めてください。
            """,
            tools=[mcp_toolset]
        )
        
        logger.info("Jira MCP agent created successfully")
        return agent
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise ADKConfigError("""
            Missing required environment variables. 
            Please copy .env.example to .env and fill in your Jira credentials.
        """)
    except Exception as e:
        logger.error(f"Failed to create agent: {e}", exc_info=True)
        raise


# エージェントインスタンスを作成
agent = create_jira_mcp_agent()