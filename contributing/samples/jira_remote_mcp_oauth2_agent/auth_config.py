"""Atlassian 用 OAuth2 認証設定。"""

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin


@dataclass
class AtlassianOAuth2Config:
    """Atlassian OAuth2 認証の設定。"""
    
    # OAuth2 エンドポイント
    auth_base_url: str = "https://auth.atlassian.com"
    api_base_url: str = "https://api.atlassian.com"
    
    # OAuth2 URL
    authorize_url: str = None
    token_url: str = None
    accessible_resources_url: str = None
    
    # Jira アクセスに必要なスコープ
    scopes: list[str] = None
    
    def __post_init__(self):
        """派生 URL を初期化する。"""
        if not self.authorize_url:
            self.authorize_url = urljoin(self.auth_base_url, "/authorize")
        if not self.token_url:
            self.token_url = urljoin(self.auth_base_url, "/oauth/token")
        if not self.accessible_resources_url:
            self.accessible_resources_url = urljoin(
                self.api_base_url, 
                "/oauth/token/accessible-resources"
            )
        if not self.scopes:
            self.scopes = [
                "read:jira-work",
                "write:jira-work",
                "read:jira-user",
                "offline_access"  # リフレッシュトークン用
            ]
    
    def get_authorize_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str,
        code_challenge: str,
        code_challenge_method: str = "S256"
    ) -> str:
        """OAuth2 フロー用の認証 URL を構築する。
        
        Args:
            client_id: OAuth2 クライアント ID
            redirect_uri: コールバック URL
            state: CSRF 保護用のランダム状態
            code_challenge: PKCE コードチャレンジ
            code_challenge_method: PKCE メソッド (S256)
            
        Returns:
            完全な認証 URL
        """
        params = {
            "audience": "api.atlassian.com",
            "client_id": client_id,
            "scope": " ".join(self.scopes),
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent",
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authorize_url}?{query_string}"