# Jira Remote MCP Server Agent Specification (API Key Authentication)

## Overview

This specification defines an ADK agent that connects to Atlassian's remote Jira MCP server using API key authentication. Unlike the local MCP server approach in `jira_api_agent`, this agent connects directly to Atlassian's hosted MCP endpoint at `https://mcp.atlassian.com/v1/sse`.

## Architecture

### Connection Method
- **Protocol**: Server-Sent Events (SSE)
- **Endpoint**: `https://mcp.atlassian.com/v1/sse`
- **Connection Type**: `SseConnectionParams` from ADK's MCP toolset

### Authentication
- **Method**: API Key in HTTP headers
- **Required Credentials**:
  - Jira instance URL (e.g., `https://yourcompany.atlassian.net`)
  - User email address
  - Atlassian API token (generated from Atlassian account settings)

## Implementation Details

### Directory Structure
```
contributing/samples/jira_remote_mcp_apikey_agent/
├── __init__.py
├── agent.py
├── .env.example
├── README.md
└── requirements.txt
```

### Environment Configuration

`.env.example`:
```env
# Your Jira instance URL
JIRA_URL=https://yourcompany.atlassian.net

# Your Atlassian account email
JIRA_EMAIL=your.email@company.com

# Atlassian API token (generate from: https://id.atlassian.com/manage-profile/security/api-tokens)
JIRA_API_TOKEN=your_api_token_here
```

### Agent Implementation

`agent.py`:
```python
import os
import base64
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# Load environment variables
load_dotenv()

# Validate configuration
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise ValueError(
        "Missing required environment variables. Please check your .env file."
    )

# Create Basic Auth header
auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

# Configure MCP connection with authentication headers
jira_remote_tools = MCPToolset(
    connection_params=SseConnectionParams(
        url="https://mcp.atlassian.com/v1/sse",
        headers={
            "Authorization": f"Basic {auth_b64}",
            "X-Atlassian-Instance-URL": JIRA_URL,
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        },
        timeout=10.0,
        sse_read_timeout=300.0  # 5 minutes for long-running operations
    )
)

# Create the agent
root_agent = Agent(
    name="jira_remote_mcp_agent",
    model="gemini-2.0-flash",
    instruction="""You are a Jira project management assistant connected to a remote Atlassian MCP server.

Available capabilities:
1. Search and filter Jira issues
2. Get detailed issue information
3. Create new issues
4. Add comments to issues
5. Update issue fields and transitions
6. Execute JQL queries
7. Manage project information
8. Work with users and teams

You have direct access to the organization's Jira instance through Atlassian's MCP server.
Always provide clear, organized responses and leverage Jira's full capabilities to assist with project management tasks.
""",
    tools=[jira_remote_tools],
)
```

## Available Tools

The remote MCP server provides access to Jira operations including:

### Issue Management
- `jira_search_issues` - Search issues using JQL
- `jira_get_issue` - Get detailed issue information
- `jira_create_issue` - Create new issues
- `jira_update_issue` - Update issue fields
- `jira_transition_issue` - Change issue status
- `jira_add_comment` - Add comments to issues

### Project Operations
- `jira_get_projects` - List available projects
- `jira_get_project` - Get project details
- `jira_get_project_components` - List project components
- `jira_get_project_versions` - List project versions

### User and Team Management
- `jira_get_user` - Get user information
- `jira_search_users` - Search for users
- `jira_get_groups` - List user groups

### Advanced Features
- `jira_execute_jql` - Execute custom JQL queries
- `jira_get_fields` - Get available custom fields
- `jira_get_issue_types` - List issue types
- `jira_get_priorities` - List priority levels

## Security Considerations

### API Token Management
- Store API tokens in environment variables, never in code
- Use `.env` files locally with proper `.gitignore` configuration
- In production, use secure secret management services
- Rotate API tokens regularly

### Network Security
- All connections use HTTPS/TLS
- Consider implementing request rate limiting
- Monitor API usage through Atlassian admin console

### Access Control
- API tokens inherit the permissions of the associated user
- Create dedicated service accounts with appropriate permissions
- Follow principle of least privilege

## Error Handling

The agent should handle common error scenarios:

```python
# Connection errors
try:
    await jira_remote_tools.get_tools()
except ConnectionError as e:
    logger.error(f"Failed to connect to Jira MCP server: {e}")
    # Implement retry logic or fallback

# Authentication errors (401)
# The MCP toolset will handle auth errors internally
# Monitor logs for authentication failures

# Rate limiting (429)
# Implement exponential backoff for rate limit errors
```

## Testing Guidelines

### Unit Tests
```python
# Test connection configuration
def test_sse_connection_params():
    params = SseConnectionParams(
        url="https://mcp.atlassian.com/v1/sse",
        headers={"Authorization": "Basic test_token"}
    )
    assert params.url == "https://mcp.atlassian.com/v1/sse"
    assert "Authorization" in params.headers

# Test authentication header generation
def test_auth_header_generation():
    email = "test@example.com"
    token = "test_token"
    auth_string = f"{email}:{token}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    assert auth_b64 == "dGVzdEBleGFtcGxlLmNvbTp0ZXN0X3Rva2Vu"
```

### Integration Tests
- Test with a sandbox Jira instance
- Verify all tool operations work correctly
- Test error handling and edge cases
- Monitor performance and latency

## Deployment Considerations

### Environment-Specific Configuration
```python
# Support multiple environments
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    SSE_TIMEOUT = 300.0  # 5 minutes
    CONNECTION_TIMEOUT = 30.0
else:
    SSE_TIMEOUT = 60.0  # 1 minute for dev
    CONNECTION_TIMEOUT = 10.0
```

### Monitoring and Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log important events
logger.info(f"Connecting to Jira MCP server for instance: {JIRA_URL}")
```

## Migration from Local MCP Server

To migrate from the local Docker-based approach:

1. Remove Docker dependencies
2. Update connection parameters from `StdioConnectionParams` to `SseConnectionParams`
3. Add authentication headers
4. Update the MCP server URL
5. Test all existing functionality

## Limitations and Considerations

1. **Network Dependency**: Requires stable internet connection
2. **Latency**: Remote connections may have higher latency than local servers
3. **Rate Limits**: Subject to Atlassian API rate limits
4. **Feature Parity**: Ensure remote MCP server supports all required operations

## References

- [Atlassian API Tokens](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [ADK MCP Documentation](https://github.com/google/adk-python/blob/main/docs/tools.md#mcp-tools)