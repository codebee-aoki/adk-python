"""Jira Remote MCP エージェント用の共通認証ユーティリティ。"""

import base64
from typing import Dict
from .config import JiraConfig


def create_basic_auth_header(config: JiraConfig) -> Dict[str, str]:
    """API キー認証用の Basic 認証ヘッダーを作成する。
    
    Args:
        config: email と api_token を含む JiraConfig インスタンス
        
    Returns:
        Authorization ヘッダーを含む辞書
    """
    config.validate_for_api_key()
    
    # Atlassian は email:api_token での Basic 認証を期待
    credentials = f"{config.email}:{config.api_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    return {
        "Authorization": f"Basic {encoded_credentials}"
    }


def create_bearer_auth_header(access_token: str) -> Dict[str, str]:
    """OAuth2 用の Bearer 認証ヘッダーを作成する。
    
    Args:
        access_token: OAuth2 アクセストークン
        
    Returns:
        Authorization ヘッダーを含む辞書
    """
    return {
        "Authorization": f"Bearer {access_token}"
    }