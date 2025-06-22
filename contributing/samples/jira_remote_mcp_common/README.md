# Jira Remote MCP Common Utilities

This directory contains shared utilities used by both the API Key and OAuth2 Jira Remote MCP agents.

## Structure

- `config.py` - Configuration management for Jira connections
- `auth.py` - Authentication header creation (Basic Auth and Bearer tokens)
- `errors.py` - Common error handling and logging setup
- `test_connection.py` - Utility to test MCP server connectivity

## Testing MCP Connection

The `test_connection.py` script allows you to verify connectivity to Atlassian's MCP server and discover available tools.

### Usage

1. Set up your environment variables:
   ```bash
   export JIRA_DOMAIN=your-company.atlassian.net
   export JIRA_EMAIL=your-email@example.com
   export JIRA_API_TOKEN=your-api-token
   ```

2. Run the test script:
   ```bash
   cd jira_remote_mcp_common
   python test_connection.py
   ```

3. Expected output:
   - Connection status
   - List of available MCP tools
   - Test call to `jira_get_myself` (if available)

### What the Test Reveals

The test script will show you:
- Whether your credentials are valid
- All Jira operations available via MCP
- The input schema for each tool
- Your current user information

This is useful for:
- Verifying your setup before using the agents
- Understanding what operations are available
- Debugging authentication issues
- Exploring the MCP tool schemas

## Shared Components

### JiraConfig

Centralized configuration class that handles:
- Loading from environment variables
- Validation for different auth methods
- Default values for MCP server URLs

### Authentication Helpers

- `create_basic_auth_header()` - For API key authentication
- `create_bearer_auth_header()` - For OAuth2 token authentication

### Error Handling

Consistent error types and logging across both agents:
- `JiraMCPError` - Base error class
- `AuthenticationError` - Auth failures
- `ConnectionError` - Network issues
- `ConfigurationError` - Missing/invalid config

## Environment Variables

Common variables used by both agents:

| Variable | Description | Required |
|----------|-------------|----------|
| `JIRA_DOMAIN` | Your Jira Cloud domain (e.g., company.atlassian.net) | Yes |
| `JIRA_EMAIL` | Your Atlassian account email | Yes |
| `JIRA_API_TOKEN` | API token for Basic Auth | For API Key agent |
| `JIRA_OAUTH_CLIENT_ID` | OAuth2 client ID | For OAuth2 agent |
| `JIRA_OAUTH_CLIENT_SECRET` | OAuth2 client secret | For OAuth2 agent |
| `JIRA_MCP_SERVER_URL` | Override MCP server URL | No |
| `JIRA_CONNECTION_TIMEOUT` | Connection timeout in seconds | No |

## Security Notes

- Never commit `.env` files with real credentials
- API tokens and OAuth2 secrets should be kept secure
- Use environment variables or secure vaults in production
- The utilities ensure sensitive data is not logged