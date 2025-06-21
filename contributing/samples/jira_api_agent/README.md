# Jira MCP Agent

A modern Jira integration agent using MCP Atlassian server and ADK's MCPToolset. This agent demonstrates how to leverage the power of mcp-atlassian without custom implementation, providing comprehensive Jira functionality through the Model Context Protocol.

## Features

- **Advanced Issue Search**: Intelligent issue filtering and JQL query execution
- **Issue Management**: Create, update, and manage issues with full field support
- **Comment Management**: Add and manage comments on issues
- **Project Information**: Access detailed project and user information
- **Smart Filtering**: AI-powered issue filtering capabilities
- **Real-time Integration**: Direct connection to Jira through MCP Atlassian

## Prerequisites

- Python 3.11+
- ADK (Agent Development Kit) installed
- Docker installed and running
- Jira Cloud account with API token
- Access to a Jira project

## Setup

### 1. Generate Jira API Token

1. Go to [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a descriptive name (e.g., "MCP Jira Agent")
4. Copy the generated token immediately (it won't be shown again)

### 2. Configure Environment Variables

Create a `.env` file in this directory:

```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
```

**Required Variables:**
- `JIRA_URL`: Your Jira Cloud instance URL
- `JIRA_USERNAME`: Your Jira account email
- `JIRA_API_TOKEN`: Generated API token from step 1

### 3. Verify Docker Installation

Ensure Docker is installed and running:

```bash
docker --version
docker run --rm hello-world
```

## Usage

### Running with ADK Web Interface

```bash
# Launch the web interface (recommended)
adk web contributing/samples/jira_api_agent
```

This will start the ADK web interface where you can interact with the Jira agent through a chat interface.

### Example Interactions

#### Search for Issues

```
User: "Search for all open issues in project PROJ"
Agent: *Uses mcp-atlassian tools to search with smart filtering*
```

```
User: "Find urgent bugs from last week"
Agent: *Leverages mcp-atlassian's intelligent filtering capabilities*
```

#### Get Issue Details

```
User: "Show me details for PROJ-123"
Agent: *Retrieves comprehensive issue information via MCP Atlassian*
```

#### Create New Issue

```
User: "Create a new bug report for login issue"
Agent: *Creates issue using mcp-atlassian's creation tools*
```

#### Update Issues from Meeting Notes

```
User: "Update Jira from our meeting notes"
Agent: *Uses mcp-atlassian's automatic issue update capabilities*
```

## How It Works

This agent leverages the [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) MCP server, which provides:

- **Docker-based Integration**: Runs mcp-atlassian server in a Docker container
- **MCPToolset Connection**: Uses ADK's MCPToolset to connect to the server
- **Zero Custom Code**: No custom Jira API implementation needed
- **Rich Functionality**: Access to all mcp-atlassian features

## Tools Available

The agent automatically receives all tools provided by mcp-atlassian, including:

### Jira Tools
- Smart issue search and filtering
- Issue creation with full field support
- Issue updates and status changes
- Comment management
- Project information retrieval
- User and permission management

### Advanced Features
- JQL query execution
- Automatic issue updates from text
- Intelligent content filtering
- Real-time synchronization

## Security Considerations

- **API Token Storage**: Never commit your `.env` file or expose API tokens
- **Docker Security**: Ensure Docker daemon is properly secured
- **Permissions**: The agent inherits permissions from the API token owner
- **Container Isolation**: mcp-atlassian runs in isolated Docker containers
- **Data Privacy**: Be cautious when handling sensitive issue data

## Troubleshooting

### Docker Issues
- Verify Docker is installed and running: `docker --version`
- Check if Docker daemon is accessible: `docker ps`
- Ensure sufficient disk space for Docker images

### Authentication Failed
- Verify your API token is correct and not expired
- Check that your email matches the Jira account
- Ensure the Jira URL includes the correct subdomain
- Test credentials manually: `curl -u email:token https://your-domain.atlassian.net/rest/api/3/myself`

### MCP Connection Issues
- Check Docker container logs for mcp-atlassian
- Verify environment variables are correctly passed to container
- Ensure network connectivity between ADK and Docker container

### Permission Errors
- Verify your account has access to the project
- Check project permissions in Jira settings
- Some operations may require admin privileges

## Technical Architecture

This agent demonstrates a modern approach to API integration:

1. **MCPToolset**: ADK's MCP client connects to external MCP servers
2. **mcp-atlassian**: Docker-based MCP server providing Jira integration
3. **Zero Custom Code**: No custom API implementation needed
4. **Extensible**: Easy to add more MCP servers for additional functionality

## Advantages

- **Simplified Maintenance**: No custom API code to maintain
- **Rich Functionality**: Full access to mcp-atlassian capabilities
- **Future-Proof**: Automatic updates when mcp-atlassian is improved
- **Best Practices**: Leverages battle-tested mcp-atlassian implementation

## Related Documentation

- [mcp-atlassian GitHub](https://github.com/sooperset/mcp-atlassian)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [ADK MCP Tools](https://google.github.io/adk-docs/tools/mcp-tools/)
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [ADK Documentation](https://github.com/google/adk-python)