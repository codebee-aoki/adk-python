# Jira Remote MCP API Key Agent

This agent connects to Atlassian's remote MCP (Model Context Protocol) server using API key authentication to interact with Jira Cloud.

## Features

- Direct connection to Atlassian's MCP server (no local Docker required)
- Simple API key authentication
- Access to all Jira operations exposed via MCP
- Automatic error handling and retry logic
- Secure credential management via environment variables

## Prerequisites

1. **Jira Cloud Account**: You need a Jira Cloud instance (not Server/Data Center)
2. **Atlassian API Token**: Generate from your [Atlassian account settings](https://id.atlassian.com/manage-profile/security/api-tokens)
3. **Python 3.10+**: Required for MCP support

## Setup

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```env
   JIRA_DOMAIN=your-company.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token-here
   ```

3. **Install dependencies** (if running standalone):
   ```bash
   pip install google-adk[mcp]
   ```

## Usage

### With ADK CLI

```bash
# Run the agent
adk run path/to/jira_remote_mcp_apikey_agent

# Or use the web interface
adk web path/to/jira_remote_mcp_apikey_agent
```

### As a Module

```python
from jira_remote_mcp_apikey_agent import agent

# The agent is pre-configured and ready to use
response = await agent.say("Create a new bug issue in project ABC")
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

## Security Notes

- API tokens are stored in environment variables (never commit `.env` files)
- Uses HTTPS for all communications
- Basic Auth header is automatically generated from email:token
- No tokens are logged or exposed in responses

## Troubleshooting

### Authentication Errors
- Verify your API token is valid and not expired
- Ensure your email matches the Atlassian account
- Check that your Jira instance allows API access

### Connection Issues
- Verify you have internet connectivity
- Check if `https://mcp.atlassian.com` is accessible
- Try increasing the `JIRA_CONNECTION_TIMEOUT` value

### Missing Tools
- Some tools may require specific Jira permissions
- Ensure your account has the necessary access rights

## Example Interactions

```
User: List all open bugs in project XYZ
Agent: I'll search for open bugs in project XYZ using JQL...

User: Create a new task for updating documentation
Agent: I'll create a new task issue for updating documentation. Which project should I create it in?

User: Show me issues assigned to me
Agent: I'll find all issues currently assigned to you...
```

## Advanced Configuration

### Custom MCP Server URL

If using a different MCP endpoint:
```env
JIRA_MCP_SERVER_URL=https://custom-mcp-server.com/v1/sse
```

### Connection Timeout

Adjust timeout for slow connections:
```env
JIRA_CONNECTION_TIMEOUT=60  # seconds
```

## Limitations

- Requires internet connection (no offline mode)
- Subject to Atlassian API rate limits
- Some advanced Jira features may not be exposed via MCP
- Cannot access Jira Server/Data Center (Cloud only)

## See Also

- [Jira Remote MCP OAuth2 Agent](../jira_remote_mcp_oauth2_agent/) - For OAuth2 authentication
- [Atlassian API Documentation](https://developer.atlassian.com/cloud/jira/platform/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)