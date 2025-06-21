# Jira Remote MCP Server Agent Specification (OAuth2 Authentication)

## Overview

This specification defines an ADK agent that connects to Atlassian's remote Jira MCP server using OAuth2 authentication. This approach provides more secure, token-based authentication with automatic refresh capabilities, suitable for production environments and multi-user scenarios.

## Architecture

### Connection Method
- **Protocol**: Server-Sent Events (SSE) with OAuth2
- **Endpoint**: `https://mcp.atlassian.com/v1/sse`
- **Connection Type**: `SseConnectionParams` with ADK's OAuth2 authentication framework

### Authentication Flow
- **Method**: OAuth 2.0 Authorization Code Flow
- **Provider**: Atlassian OAuth2
- **Token Management**: Automatic refresh with ADK's `OAuth2CredentialRefresher`

## OAuth2 Configuration

### Atlassian OAuth2 Endpoints
```python
ATLASSIAN_AUTH_ENDPOINTS = {
    "authorization_endpoint": "https://auth.atlassian.com/authorize",
    "token_endpoint": "https://auth.atlassian.com/oauth/token",
    "userinfo_endpoint": "https://api.atlassian.com/me",
    "revocation_endpoint": "https://auth.atlassian.com/oauth/revoke"
}
```

### Required OAuth2 Scopes
```python
JIRA_OAUTH_SCOPES = [
    "read:jira-work",           # Read Jira project and issue data
    "write:jira-work",          # Create and update issues
    "read:jira-user",           # Access user information
    "read:me",                  # Read user profile
    "offline_access"            # Refresh token support
]
```

## Implementation Details

### Directory Structure
```
contributing/samples/jira_remote_mcp_oauth2_agent/
├── __init__.py
├── agent.py
├── auth_config.py
├── oauth_callback_server.py
├── .env.example
├── README.md
└── requirements.txt
```

### Environment Configuration

`.env.example`:
```env
# OAuth2 Client Configuration (from Atlassian App)
ATLASSIAN_CLIENT_ID=your_client_id_here
ATLASSIAN_CLIENT_SECRET=your_client_secret_here
ATLASSIAN_REDIRECT_URI=http://localhost:8080/callback

# Jira Instance
JIRA_URL=https://yourcompany.atlassian.net

# Token Storage (optional, defaults to in-memory)
TOKEN_STORAGE_PATH=~/.adk/jira_tokens.json
```

### OAuth2 Authentication Configuration

`auth_config.py`:
```python
from google.adk.auth import AuthCredential, AuthScheme
from google.adk.auth.auth_schemes import AuthSchemeType, OAuthGrantType
from google.adk.auth.oauth2_credential_util import OAuth2CredentialUtil
from google.adk.auth.refresher.oauth2_credential_refresher import OAuth2CredentialRefresher
from fastapi.openapi.models import OAuthFlow, OAuthFlows, SecurityScheme
import os
from typing import Optional

class JiraOAuth2Config:
    """Configuration for Jira OAuth2 authentication."""
    
    def __init__(self):
        self.client_id = os.getenv("ATLASSIAN_CLIENT_ID")
        self.client_secret = os.getenv("ATLASSIAN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ATLASSIAN_REDIRECT_URI", "http://localhost:8080/callback")
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("OAuth2 client credentials not configured")
    
    def create_auth_scheme(self) -> AuthScheme:
        """Create OAuth2 auth scheme for Atlassian."""
        return SecurityScheme(
            type=AuthSchemeType.oauth2,
            flows=OAuthFlows(
                authorizationCode=OAuthFlow(
                    authorizationUrl="https://auth.atlassian.com/authorize",
                    tokenUrl="https://auth.atlassian.com/oauth/token",
                    scopes={
                        "read:jira-work": "Read Jira data",
                        "write:jira-work": "Write Jira data",
                        "read:jira-user": "Read user information",
                        "read:me": "Read profile",
                        "offline_access": "Refresh tokens"
                    }
                )
            )
        )
    
    async def get_or_refresh_credential(
        self, 
        stored_token_path: Optional[str] = None
    ) -> AuthCredential:
        """Get OAuth2 credential, refreshing if necessary."""
        # Check for stored token
        if stored_token_path and os.path.exists(stored_token_path):
            with open(stored_token_path, 'r') as f:
                import json
                token_data = json.load(f)
                
            # Create credential from stored token
            credential = AuthCredential(
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                expires_at=token_data.get("expires_at")
            )
            
            # Check if refresh needed
            if OAuth2CredentialUtil.is_expired(credential):
                refresher = OAuth2CredentialRefresher(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    token_endpoint="https://auth.atlassian.com/oauth/token"
                )
                credential = await refresher.refresh(credential)
                
                # Save refreshed token
                self._save_token(credential, stored_token_path)
            
            return credential
        else:
            # Initiate new OAuth2 flow
            return await self._initiate_oauth_flow()
    
    async def _initiate_oauth_flow(self) -> AuthCredential:
        """Initiate OAuth2 authorization flow."""
        from .oauth_callback_server import start_callback_server
        
        # Start local callback server
        auth_code = await start_callback_server(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            auth_url="https://auth.atlassian.com/authorize",
            scopes=["read:jira-work", "write:jira-work", "read:jira-user", "read:me", "offline_access"]
        )
        
        # Exchange code for token
        util = OAuth2CredentialUtil(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_endpoint="https://auth.atlassian.com/oauth/token"
        )
        
        credential = await util.exchange_code_for_token(
            code=auth_code,
            redirect_uri=self.redirect_uri
        )
        
        # Save token
        token_path = os.getenv("TOKEN_STORAGE_PATH", "~/.adk/jira_tokens.json")
        self._save_token(credential, os.path.expanduser(token_path))
        
        return credential
    
    def _save_token(self, credential: AuthCredential, path: str):
        """Save token to file."""
        import json
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump({
                "access_token": credential.access_token,
                "refresh_token": credential.refresh_token,
                "expires_at": credential.expires_at
            }, f)
```

### Agent Implementation

`agent.py`:
```python
import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from .auth_config import JiraOAuth2Config

# Load environment variables
load_dotenv()

# Validate configuration
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
if not JIRA_URL:
    raise ValueError("JIRA_URL environment variable is required")

async def create_jira_agent():
    """Create Jira agent with OAuth2 authentication."""
    # Initialize OAuth2 configuration
    oauth_config = JiraOAuth2Config()
    
    # Get or refresh OAuth2 credential
    token_path = os.path.expanduser(
        os.getenv("TOKEN_STORAGE_PATH", "~/.adk/jira_tokens.json")
    )
    credential = await oauth_config.get_or_refresh_credential(token_path)
    
    # Configure MCP connection with OAuth2 token
    jira_remote_tools = MCPToolset(
        connection_params=SseConnectionParams(
            url="https://mcp.atlassian.com/v1/sse",
            headers={
                "Authorization": f"Bearer {credential.access_token}",
                "X-Atlassian-Instance-URL": JIRA_URL,
                "Accept": "text/event-stream",
                "Content-Type": "application/json"
            },
            timeout=10.0,
            sse_read_timeout=300.0
        ),
        auth_scheme=oauth_config.create_auth_scheme(),
        auth_credential=credential
    )
    
    # Create the agent
    return Agent(
        name="jira_remote_oauth2_agent",
        model="gemini-2.0-flash",
        instruction="""You are a Jira project management assistant with OAuth2 authentication.

You have secure access to the organization's Jira instance through OAuth2 authentication.
This provides enhanced security and automatic token management.

Available capabilities:
1. Full Jira issue management (create, read, update, transition)
2. Project and component management
3. User and team operations
4. Advanced JQL queries
5. Custom field operations
6. Attachment handling

Always maintain security best practices and provide clear, helpful responses.
Your authentication is automatically managed, so focus on helping users with their Jira tasks.
""",
        tools=[jira_remote_tools],
    )

# For use in async contexts
root_agent = None

def get_agent():
    """Get or create the Jira agent."""
    global root_agent
    if root_agent is None:
        loop = asyncio.get_event_loop()
        root_agent = loop.run_until_complete(create_jira_agent())
    return root_agent
```

### OAuth2 Callback Server

`oauth_callback_server.py`:
```python
import asyncio
import urllib.parse
from aiohttp import web
import webbrowser
from typing import Optional

async def start_callback_server(
    client_id: str,
    redirect_uri: str,
    auth_url: str,
    scopes: list[str],
    port: int = 8080
) -> str:
    """Start a local server to handle OAuth2 callback."""
    
    auth_code: Optional[str] = None
    app = web.Application()
    
    async def handle_callback(request):
        nonlocal auth_code
        auth_code = request.query.get('code')
        
        if auth_code:
            return web.Response(
                text="Authorization successful! You can close this window.",
                content_type='text/html'
            )
        else:
            error = request.query.get('error', 'Unknown error')
            return web.Response(
                text=f"Authorization failed: {error}",
                content_type='text/html',
                status=400
            )
    
    app.router.add_get('/callback', handle_callback)
    
    # Build authorization URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'audience': 'api.atlassian.com',
        'prompt': 'consent'
    }
    
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    # Open browser for authorization
    print(f"Opening browser for authorization: {full_auth_url}")
    webbrowser.open(full_auth_url)
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    
    # Wait for callback
    while auth_code is None:
        await asyncio.sleep(0.1)
    
    # Cleanup
    await runner.cleanup()
    
    return auth_code
```

## Advanced Features

### Token Refresh Handling

The agent automatically handles token refresh:

```python
class AutoRefreshMCPToolset(MCPToolset):
    """MCPToolset with automatic OAuth2 token refresh."""
    
    def __init__(self, oauth_config: JiraOAuth2Config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oauth_config = oauth_config
        self._refresher = OAuth2CredentialRefresher(
            client_id=oauth_config.client_id,
            client_secret=oauth_config.client_secret,
            token_endpoint="https://auth.atlassian.com/oauth/token"
        )
    
    async def get_tools(self, readonly_context=None):
        """Override to handle token refresh on 401 errors."""
        try:
            return await super().get_tools(readonly_context)
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                # Refresh token and retry
                new_credential = await self._refresher.refresh(self._auth_credential)
                self._auth_credential = new_credential
                
                # Update connection headers
                self._connection_params.headers["Authorization"] = f"Bearer {new_credential.access_token}"
                
                # Retry
                return await super().get_tools(readonly_context)
            raise
```

### Multi-Tenant Support

For supporting multiple Jira instances:

```python
class MultiTenantJiraAgent:
    """Support multiple Jira instances with different OAuth apps."""
    
    def __init__(self):
        self.instances = {}
    
    def add_instance(self, name: str, config: dict):
        """Add a Jira instance configuration."""
        self.instances[name] = {
            'url': config['jira_url'],
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'agent': None
        }
    
    async def get_agent(self, instance_name: str) -> Agent:
        """Get agent for specific instance."""
        if instance_name not in self.instances:
            raise ValueError(f"Unknown instance: {instance_name}")
        
        if self.instances[instance_name]['agent'] is None:
            # Create agent for this instance
            config = JiraOAuth2Config()
            config.client_id = self.instances[instance_name]['client_id']
            config.client_secret = self.instances[instance_name]['client_secret']
            
            # Create agent...
            self.instances[instance_name]['agent'] = await create_jira_agent_for_instance(config)
        
        return self.instances[instance_name]['agent']
```

## Security Best Practices

### Token Storage
```python
import keyring
from cryptography.fernet import Fernet

class SecureTokenStorage:
    """Secure token storage using system keychain."""
    
    def __init__(self, service_name="adk_jira_oauth"):
        self.service_name = service_name
        self.encryption_key = self._get_or_create_key()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key."""
        key = keyring.get_password(self.service_name, "encryption_key")
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password(self.service_name, "encryption_key", key)
        return key.encode()
    
    def save_token(self, user_id: str, token_data: dict):
        """Save encrypted token."""
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(json.dumps(token_data).encode())
        keyring.set_password(self.service_name, user_id, encrypted.decode())
    
    def get_token(self, user_id: str) -> Optional[dict]:
        """Retrieve and decrypt token."""
        encrypted = keyring.get_password(self.service_name, user_id)
        if encrypted:
            f = Fernet(self.encryption_key)
            decrypted = f.decrypt(encrypted.encode())
            return json.loads(decrypted.decode())
        return None
```

### Scope Management
- Request only necessary scopes
- Implement scope escalation when needed
- Log scope usage for audit

### Session Security
```python
# Implement session timeout
SESSION_TIMEOUT = 3600  # 1 hour

# Add session validation
async def validate_session(credential: AuthCredential) -> bool:
    """Validate OAuth2 session is still active."""
    try:
        # Call userinfo endpoint to validate token
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.atlassian.com/me",
                headers={"Authorization": f"Bearer {credential.access_token}"}
            ) as response:
                return response.status == 200
    except:
        return False
```

## Testing Guidelines

### Unit Tests
```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_oauth_flow():
    """Test OAuth2 authorization flow."""
    config = JiraOAuth2Config()
    
    with patch('webbrowser.open') as mock_browser:
        with patch('aiohttp.web.TCPSite.start') as mock_server:
            # Simulate authorization code callback
            mock_code = "test_auth_code"
            
            # Test flow initiation
            credential = await config._initiate_oauth_flow()
            
            assert mock_browser.called
            assert credential.access_token is not None

@pytest.mark.asyncio  
async def test_token_refresh():
    """Test automatic token refresh."""
    config = JiraOAuth2Config()
    
    # Create expired credential
    expired_credential = AuthCredential(
        access_token="expired_token",
        refresh_token="refresh_token",
        expires_at=0  # Already expired
    )
    
    # Test refresh
    refreshed = await config.get_or_refresh_credential()
    assert refreshed.access_token != "expired_token"
```

### Integration Tests
```python
@pytest.mark.integration
async def test_jira_operations_with_oauth():
    """Test actual Jira operations with OAuth2."""
    agent = await create_jira_agent()
    
    # Test issue search
    result = await agent.execute(
        "Search for all open issues in project TEST"
    )
    
    assert result.success
    assert "issues" in result.data
```

## Deployment

### Production Configuration
```python
# Production settings
PRODUCTION_CONFIG = {
    "token_storage": "aws_secrets_manager",  # or "azure_keyvault"
    "session_timeout": 3600,
    "max_refresh_attempts": 3,
    "ssl_verify": True,
    "log_level": "INFO"
}
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy agent code
COPY . /app
WORKDIR /app

# Use secure token storage
ENV TOKEN_STORAGE_PATH=/secure/tokens
ENV PYTHONPATH=/app

# Run with limited privileges
USER nobody
CMD ["python", "-m", "agent"]
```

## Monitoring and Observability

### OAuth2 Metrics
```python
from prometheus_client import Counter, Histogram

oauth_token_refreshes = Counter(
    'jira_oauth_token_refreshes_total',
    'Total number of OAuth token refreshes'
)

oauth_auth_duration = Histogram(
    'jira_oauth_auth_duration_seconds',
    'OAuth authorization flow duration'
)

class MonitoredOAuth2Config(JiraOAuth2Config):
    """OAuth2 config with monitoring."""
    
    async def get_or_refresh_credential(self, *args, **kwargs):
        with oauth_auth_duration.time():
            credential = await super().get_or_refresh_credential(*args, **kwargs)
        
        if hasattr(self, '_did_refresh') and self._did_refresh:
            oauth_token_refreshes.inc()
        
        return credential
```

## Troubleshooting

### Common Issues

1. **Invalid Client Error**
   - Verify client ID and secret
   - Check OAuth app configuration in Atlassian

2. **Scope Errors**
   - Ensure requested scopes are approved for your OAuth app
   - Check Atlassian API permissions

3. **Token Expiry**
   - Implement proper refresh logic
   - Monitor token expiry times

4. **Network Issues**
   - Implement retry logic with exponential backoff
   - Add connection pooling for better performance

## References

- [Atlassian OAuth 2.0 Documentation](https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [ADK Authentication Guide](https://github.com/google/adk-python/blob/main/docs/auth.md)
- [MCP Authentication Specification](https://modelcontextprotocol.io/specification/basic/authorization)