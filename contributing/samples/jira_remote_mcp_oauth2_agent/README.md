# Jira Remote MCP OAuth2 Agent

This agent connects to Atlassian's remote MCP (Model Context Protocol) server using OAuth2 authentication to interact with Jira Cloud. It provides enterprise-grade security with automatic token refresh and secure storage.

## Features

- OAuth2 authentication with PKCE (Proof Key for Code Exchange)
- Automatic token refresh when access tokens expire
- Secure local token storage
- Direct connection to Atlassian's MCP server (no Docker required)
- Access to all Jira operations exposed via MCP
- Multi-tenant support (can work with multiple Jira instances)

## Prerequisites

1. **Jira Cloud Account**: You need a Jira Cloud instance (not Server/Data Center)
2. **Atlassian OAuth2 App**: Create at [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/)
3. **Python 3.10+**: Required for MCP support

## OAuth2 App Setup

1. Go to the [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/)
2. Click "Create new app"
3. Configure your app:
   - **App name**: Choose a descriptive name
   - **App description**: Brief description of your integration
   - **App type**: Select "OAuth 2.0 integration"
4. Set up OAuth2:
   - **Callback URL**: `http://localhost:8080/callback` (or your custom URL)
   - **Permissions**: Add required scopes:
     - `read:jira-work`
     - `write:jira-work`  
     - `read:jira-user`
     - `offline_access` (for refresh tokens)
5. Save your **Client ID** and **Client Secret**

## Agent Setup

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```env
   JIRA_DOMAIN=your-company.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_OAUTH_CLIENT_ID=your-oauth-client-id
   JIRA_OAUTH_CLIENT_SECRET=your-oauth-client-secret
   JIRA_OAUTH_REDIRECT_URI=http://localhost:8080/callback
   ```

3. **Install dependencies** (if running standalone):
   ```bash
   pip install google-adk[mcp] aiohttp
   ```

## Usage

### First Run (Authentication)

On first run, the agent will:
1. Start a local web server on port 8080
2. Open your browser to Atlassian's OAuth2 consent page
3. After you authorize, save tokens securely for future use

### With ADK CLI

```bash
# Run the agent
adk run path/to/jira_remote_mcp_oauth2_agent

# Or use the web interface
adk web path/to/jira_remote_mcp_oauth2_agent
```

### As a Module

```python
from jira_remote_mcp_oauth2_agent import agent

# The agent handles OAuth2 flow automatically
response = await agent.say("Show me all high priority bugs")
```

## Token Management

### Token Storage
- Tokens are stored in `~/.jira_mcp_tokens/` with restrictive permissions
- Each Jira domain has its own token file
- Tokens are automatically refreshed when they expire

### Manual Token Management
```bash
# View stored tokens (be careful - contains sensitive data!)
ls -la ~/.jira_mcp_tokens/

# Remove tokens for a specific domain
rm ~/.jira_mcp_tokens/your_company_atlassian_net.json
```

## Available Operations

The agent has access to all Jira operations provided by Atlassian's MCP server, including:

- **Issue Management**: Create, update, delete, transition issues
- **Search**: Run JQL queries, find issues
- **Projects**: List projects, get project details
- **Users**: Search users, get user details
- **Workflows**: Get available transitions, move issues
- **Fields**: Get field configurations, custom fields
- **Comments**: Add, update, delete comments
- **Attachments**: Upload and manage attachments

## Security Features

### OAuth2 with PKCE
- Uses Authorization Code flow with PKCE for enhanced security
- No client credentials stored in the app
- State parameter prevents CSRF attacks

### Token Security
- Access tokens have short lifetime (typically 1 hour)
- Refresh tokens allow automatic renewal without re-authentication
- Tokens stored with restrictive file permissions (600)
- Token files only accessible by owner

### Best Practices
- Never share your `.env` file or token files
- Regularly rotate your OAuth2 client secret
- Review app permissions in Atlassian settings
- Use environment-specific OAuth2 apps for dev/prod

## Troubleshooting

### OAuth2 Flow Issues

**Browser doesn't open automatically**:
- Manually visit the URL shown in the console
- Ensure your system allows opening browsers from terminal

**Callback fails**:
- Check that port 8080 is not in use
- Verify redirect URI matches your OAuth2 app configuration
- Try a different port by setting `OAUTH_CALLBACK_PORT`

**Authentication denied**:
- Ensure you're logged into the correct Atlassian account
- Verify the OAuth2 app has required permissions
- Check that your Jira domain matches the authorized sites

### Token Issues

**Token refresh fails**:
- Re-authenticate by deleting the token file
- Verify OAuth2 app still has `offline_access` scope
- Check client secret hasn't been rotated

**Access denied after authentication**:
- Ensure your account has Jira access
- Verify the Jira site is in your accessible resources
- Check OAuth2 app isn't suspended

### Connection Issues
- Verify internet connectivity
- Check if `https://mcp.atlassian.com` is accessible
- Review any proxy/firewall settings

## Example Interactions

```
User: What Jira projects do I have access to?
Agent: I'll list all the Jira projects you have access to...

User: Create a bug for the login page not working
Agent: I'll create a bug issue. Which project should I create it in, and what additional details would you like to include?

User: Show me all issues I created this week
Agent: I'll search for all issues you created this week using JQL...
```

## Advanced Configuration

### Custom Callback Port

If port 8080 is in use:
```env
OAUTH_CALLBACK_PORT=8888
JIRA_OAUTH_REDIRECT_URI=http://localhost:8888/callback
```

### Custom Token Storage Location

Set environment variable:
```env
JIRA_TOKEN_STORAGE_PATH=/custom/path/to/tokens
```

### Proxy Configuration

For corporate environments:
```env
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

## Comparison with API Key Agent

| Feature | OAuth2 Agent | API Key Agent |
|---------|--------------|---------------|
| Security | Higher (tokens expire) | Lower (permanent key) |
| Setup Complexity | Higher (OAuth2 app) | Lower (just API key) |
| Token Management | Automatic refresh | Not needed |
| User Attribution | Full user context | Service account |
| Enterprise Ready | Yes | Limited |
| Multi-tenant | Yes | Per-key basis |

## See Also

- [Jira Remote MCP API Key Agent](../jira_remote_mcp_apikey_agent/) - Simpler authentication option
- [Atlassian OAuth2 Documentation](https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)