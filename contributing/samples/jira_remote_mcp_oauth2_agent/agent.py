"""Jira Remote MCP OAuth2 エージェント。

このエージェントは OAuth2 認証を使用して Atlassian のリモート MCP サーバーに接続します。
トークンリフレッシュとセキュアストレージを含むエンタープライズグレードのセキュリティ機能を備え、
MCP プロトコルを通じて公開されるすべての Jira 操作へのアクセスを提供します。
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# インポート用に親ディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from google.adk import Agent
from google.adk.toolbox.mcp import MCPToolset, SseConnectionParams
from google.adk.errors import ConfigurationError as ADKConfigError

# 共通ユーティリティをインポート
sys.path.append(str(Path(__file__).parent.parent))
from jira_remote_mcp_common import (
    JiraConfig,
    create_bearer_auth_header,
    setup_logging,
    ConfigurationError,
    AuthenticationError
)

# OAuth2 コンポーネントをインポート
from oauth2_flow import OAuth2Flow
from token_storage import TokenStorage


class OAuth2MCPAgent:
    """Jira 用 OAuth2 認証 MCP エージェント。"""
    
    def __init__(self):
        self.logger = setup_logging("jira_mcp_oauth2_agent")
        self.config = None
        self.token_storage = TokenStorage()
        self.oauth_flow = None
        self.current_token = None
    
    async def _ensure_authenticated(self) -> str:
        """有効なアクセストークンを保持していることを確認する。
        
        Returns:
            有効なアクセストークン
            
        Raises:
            AuthenticationError: 認証が失敗した場合
        """
        # 既存のトークンをチェック
        token_data = self.token_storage.load_tokens(self.config.jira_domain)
        
        if token_data and not token_data.get("expired", True):
            # トークンはまだ有効
            self.logger.info("Using existing valid access token")
            return token_data["access_token"]
        
        if token_data and token_data.get("refresh_token"):
            # トークンのリフレッシュを試行
            self.logger.info("Access token expired, attempting refresh...")
            try:
                new_tokens = await self.oauth_flow.refresh_access_token(
                    token_data["refresh_token"]
                )
                
                # リフレッシュされたトークンを保存
                self.token_storage.update_access_token(
                    domain=self.config.jira_domain,
                    access_token=new_tokens["access_token"],
                    expires_in=new_tokens["expires_in"]
                )
                
                self.logger.info("Token refreshed successfully")
                return new_tokens["access_token"]
                
            except Exception as e:
                self.logger.warning(f"Token refresh failed: {e}")
                # 新しい認証フローにフォールスルー
        
        # 完全な OAuth2 フローを実行する必要あり
        self.logger.info("Starting OAuth2 authentication flow...")
        return await self._perform_oauth_flow()
    
    async def _perform_oauth_flow(self) -> str:
        """完全な OAuth2 認証フローを実行する。
        
        Returns:
            アクセストークン
            
        Raises:
            AuthenticationError: 認証が失敗した場合
        """
        try:
            # 認証フローを開始
            auth_code = await self.oauth_flow.start_auth_flow()
            
            # コードをトークンと交換
            token_response = await self.oauth_flow.exchange_code_for_token(auth_code)
            
            # cloud ID を見つけるためにアクセス可能なリソースを取得
            resources = await self.oauth_flow.get_accessible_resources(
                token_response["access_token"]
            )
            
            # マッチする Jira サイトを検索
            cloud_id = None
            for resource in resources:
                if self.config.jira_domain in resource.get("url", ""):
                    cloud_id = resource["id"]
                    break
            
            if not cloud_id:
                raise AuthenticationError(
                    f"No accessible Jira site found for domain: {self.config.jira_domain}"
                )
            
            # トークンを保存
            self.token_storage.save_tokens(
                domain=self.config.jira_domain,
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token"),
                expires_in=token_response["expires_in"],
                cloud_id=cloud_id
            )
            
            self.logger.info("OAuth2 authentication successful")
            return token_response["access_token"]
            
        except Exception as e:
            raise AuthenticationError(f"OAuth2 flow failed: {e}")
    
    async def create_agent(self) -> Agent:
        """OAuth2 認証された Jira エージェントを作成する。
        
        Returns:
            設定されたエージェントインスタンス
        """
        # 設定を読み込み
        self.config = JiraConfig.from_env()
        self.config.validate_for_oauth2()
        
        # OAuth2 フローを初期化
        callback_port = int(os.getenv("OAUTH_CALLBACK_PORT", "8080"))
        self.oauth_flow = OAuth2Flow(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            redirect_uri=self.config.redirect_uri,
            port=callback_port
        )
        
        # 有効なアクセストークンを取得
        access_token = await self._ensure_authenticated()
        
        # 認証ヘッダーを作成
        auth_headers = create_bearer_auth_header(access_token)
        
        # SSE 接続パラメータを設定
        connection_params = SseConnectionParams(
            url=self.config.mcp_server_url,
            headers=auth_headers,
            timeout=self.config.connection_timeout
        )
        
        # MCP ツールセットを作成
        mcp_toolset = MCPToolset(
            connection_params=connection_params,
            tool_filter=None  # 利用可能なすべてのツールを含める
        )
        
        # エージェントを作成
        agent = Agent(
            name="Jira Remote MCP OAuth2 Agent",
            description="""
                Atlassian のリモート MCP サーバーを使用して Jira Cloud と対話する AI エージェントです。
                自動トークンリフレッシュ機能を備えた OAuth2 で認証されます。課題管理、プロジェクト管理、
                JQL 検索を含む Jira 操作にエンタープライズグレードのセキュリティを提供します。
            """,
            instruction=f"""
                あなたは OAuth2 認証を使用して {self.config.jira_domain} に接続された
                便利な Jira アシスタントです。以下のような作業でユーザーを支援できます：
                - 課題の作成、更新、検索
                - プロジェクトとワークフローの管理
                - JQL クエリの実行
                - プロジェクトデータの分析
                - Jira タスクの自動化

                認証はトークンリフレッシュにより自動的に処理されるため、あなたは
                ユーザーの Jira タスクの支援に集中できます。実行するアクションについては
                常に明確に説明し、重要な変更を行う前には確認を求めてください。
            """,
            tools=[mcp_toolset]
        )
        
        self.logger.info("OAuth2 Jira MCP agent created successfully")
        return agent


async def create_jira_oauth2_agent() -> Agent:
    """OAuth2 認証を使用する Jira エージェントを作成する。
    
    Returns:
        設定されたエージェントインスタンス
        
    Raises:
        ConfigurationError: 必要な環境変数が不足している場合
    """
    try:
        oauth_agent = OAuth2MCPAgent()
        return await oauth_agent.create_agent()
    except ConfigurationError as e:
        raise ADKConfigError("""
            Missing required OAuth2 configuration. 
            Please copy .env.example to .env and configure your OAuth2 app credentials.
        """)
    except Exception as e:
        raise ADKConfigError(f"Failed to create OAuth2 agent: {e}")


# エージェントインスタンスを作成
# 注意: OAuth2 は非同期初期化が必要
def _create_agent():
    """エージェントを同期的に作成するヘルパー。"""
    return asyncio.run(create_jira_oauth2_agent())

agent = _create_agent()