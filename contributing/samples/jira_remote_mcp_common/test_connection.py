"""Atlassian MCPサーバー接続のテストスクリプト。"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

# インポート用に親ディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from google.adk.toolbox.mcp import McpClient, SseConnectionParams
from jira_remote_mcp_common import (
    JiraConfig,
    create_basic_auth_header,
    setup_logging,
    handle_mcp_error,
    ConnectionError,
    AuthenticationError
)


async def test_mcp_connection(config: JiraConfig) -> None:
    """Atlassian MCPサーバーへの接続をテストし、利用可能なツールを一覧表示する。
    
    Args:
        config: 認証情報を含むJiraConfigインスタンス
    """
    logger = setup_logging("jira_mcp_test")
    
    try:
        logger.info(f"Atlassian MCPサーバーに接続中: {config.mcp_server_url}")
        
        # 認証ヘッダーを作成
        auth_headers = create_basic_auth_header(config)
        
        # SSE接続パラメータを設定
        connection_params = SseConnectionParams(
            url=config.mcp_server_url,
            headers=auth_headers,
            timeout=config.connection_timeout
        )
        
        # MCPクライアントを作成
        async with McpClient() as client:
            logger.info("MCPクライアントを初期化中...")
            
            # サーバーに接続
            try:
                await client.connect_sse(connection_params)
                logger.info("Atlassian MCPサーバーへの接続に成功しました！")
            except Exception as e:
                raise ConnectionError(f"MCPサーバーへの接続に失敗しました: {e}")
            
            # 利用可能なツールを一覧表示
            logger.info("利用可能なMCPツールを取得中...")
            tools = await client.list_tools()
            
            if tools:
                logger.info(f"{len(tools)}個の利用可能なツールが見つかりました:")
                for tool in tools:
                    logger.info(f"  - {tool.name}: {tool.description}")
                    if hasattr(tool, 'inputSchema'):
                        logger.info(f"    入力スキーマ: {json.dumps(tool.inputSchema, indent=2)}")
            else:
                logger.warning("MCPサーバーでツールが見つかりませんでした")
            
            # 利用可能な場合、シンプルなツール呼び出しをテスト
            if tools and any(tool.name == "jira_get_myself" for tool in tools):
                logger.info("\n'jira_get_myself'ツールをテスト中...")
                try:
                    result = await client.call_tool("jira_get_myself", {})
                    logger.info(f"現在のユーザー情報: {json.dumps(result, indent=2)}")
                except Exception as e:
                    logger.error(f"ツールの呼び出しに失敗しました: {e}")
            
    except AuthenticationError as e:
        logger.error(f"認証に失敗しました: {e}")
        logger.error("JIRA_EMAILとJIRA_API_TOKEN環境変数を確認してください")
    except ConnectionError as e:
        handle_mcp_error(e, logger)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)


async def main():
    """接続テストのメインエントリーポイント。"""
    # 設定を読み込む
    config = JiraConfig.from_env()
    
    # APIキー認証のバリデーション
    try:
        config.validate_for_api_key()
    except ValueError as e:
        print(f"""設定エラー: {e}

以下の環境変数が設定されていることを確認してください:
  - JIRA_DOMAIN (例: 'your-domain.atlassian.net')
  - JIRA_EMAIL (Atlassianアカウントのメールアドレス)
  - JIRA_API_TOKEN (AtlassianのAPIトークン)""")
        return
    
    # テストを実行
    await test_mcp_connection(config)


if __name__ == "__main__":
    asyncio.run(main())