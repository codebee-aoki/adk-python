"""Jira Remote MCP エージェント用の共通エラーハンドリング。"""

import logging
from typing import Optional, Any


class JiraMCPError(Exception):
    """Jira MCP 関連エラーの基底例外。"""
    pass


class AuthenticationError(JiraMCPError):
    """認証失敗。"""
    pass


class ConnectionError(JiraMCPError):
    """MCP サーバーへの接続失敗。"""
    pass


class ConfigurationError(JiraMCPError):
    """設定が無効または不足。"""
    pass


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """エージェント用の構造化ロギングを設定する。
    
    Args:
        name: ロガー名
        level: ロギングレベル
        
    Returns:
        設定されたロガーインスタンス
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # フォーマット付きコンソールハンドラーを作成
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def handle_mcp_error(error: Exception, logger: logging.Logger) -> None:
    """MCP 関連エラーを適切なロギングで処理する。
    
    Args:
        error: 発生した例外
        logger: 出力用のロガーインスタンス
    """
    if isinstance(error, AuthenticationError):
        logger.error(f"認証失敗: {error}")
    elif isinstance(error, ConnectionError):
        logger.error(f"接続失敗: {error}")
    elif isinstance(error, ConfigurationError):
        logger.error(f"設定エラー: {error}")
    else:
        logger.error(f"予期しないエラー: {error}", exc_info=True)