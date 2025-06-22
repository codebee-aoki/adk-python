"""Jira Remote MCP エージェント用の共通設定ユーティリティ。"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class JiraConfig:
    """Jira Remote MCP 接続の設定。"""
    
    # Jira インスタンス設定
    jira_domain: str
    email: str
    
    # 認証
    api_token: Optional[str] = None
    
    # OAuth2 設定（OAuth2 エージェント用）
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    
    # MCP サーバー設定
    mcp_server_url: str = "https://mcp.atlassian.com/v1/sse"
    connection_timeout: int = 30
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "JiraConfig":
        """環境変数から設定を読み込む。"""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # 必須フィールド
        jira_domain = os.getenv("JIRA_DOMAIN")
        if not jira_domain:
            raise ValueError("JIRA_DOMAIN 環境変数が必要です")
        
        email = os.getenv("JIRA_EMAIL")
        if not email:
            raise ValueError("JIRA_EMAIL 環境変数が必要です")
        
        return cls(
            jira_domain=jira_domain,
            email=email,
            api_token=os.getenv("JIRA_API_TOKEN"),
            client_id=os.getenv("JIRA_OAUTH_CLIENT_ID"),
            client_secret=os.getenv("JIRA_OAUTH_CLIENT_SECRET"),
            redirect_uri=os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback"),
            mcp_server_url=os.getenv("JIRA_MCP_SERVER_URL", "https://mcp.atlassian.com/v1/sse"),
            connection_timeout=int(os.getenv("JIRA_CONNECTION_TIMEOUT", "30"))
        )
    
    def validate_for_api_key(self) -> None:
        """API キー認証用の設定を検証する。"""
        if not self.api_token:
            raise ValueError("API キー認証には JIRA_API_TOKEN が必要です")
    
    def validate_for_oauth2(self) -> None:
        """OAuth2 認証用の設定を検証する。"""
        if not self.client_id:
            raise ValueError("OAuth2 認証には JIRA_OAUTH_CLIENT_ID が必要です")
        if not self.client_secret:
            raise ValueError("OAuth2 認証には JIRA_OAUTH_CLIENT_SECRET が必要です")