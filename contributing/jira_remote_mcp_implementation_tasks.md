# Jira Remote MCP Server Agents - Implementation Task List

**Created**: 2025-01-21  
**Last Updated**: 2025-01-21  
**Overall Progress**: 0%

## Overview

This document tracks the implementation of two Jira agents that connect to Atlassian's remote MCP server:
1. **API Key Agent**: Simple authentication using Atlassian API tokens
2. **OAuth2 Agent**: Enterprise-grade authentication with OAuth 2.0 flow

## Implementation Phases

### Phase 1: Foundation and Shared Components (0%)
Core infrastructure needed by both agents.

#### 1.1 Project Structure Setup
- [ ] Create base directory structure for both agents
  - Status: Not Started
  - Priority: High
  - Dependencies: None
  - Notes: Follow ADK sample agent conventions

- [ ] Set up common utilities module for shared code
  - Status: Not Started
  - Priority: High
  - Dependencies: Project structure
  - Notes: Error handling, logging, connection helpers

- [ ] Create base test infrastructure
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Project structure
  - Notes: pytest fixtures, mock servers

#### 1.2 MCP Connection Research
- [ ] Test SSE connection to https://mcp.atlassian.com/v1/sse
  - Status: Not Started
  - Priority: High
  - Dependencies: None
  - Notes: Verify endpoint availability and requirements

- [ ] Document available MCP tools from Atlassian server
  - Status: Not Started
  - Priority: High
  - Dependencies: SSE connection test
  - Notes: List all Jira operations exposed via MCP

- [ ] Analyze authentication header requirements
  - Status: Not Started
  - Priority: High
  - Dependencies: SSE connection test
  - Notes: Exact format for API key and OAuth2 bearer tokens

### Phase 2: API Key Agent Implementation (0%)

#### 2.1 Core Implementation
- [ ] Create `jira_remote_mcp_apikey_agent` directory structure
  - Status: Not Started
  - Priority: High
  - Dependencies: Phase 1.1
  - Notes: Include all files from spec

- [ ] Implement environment configuration loading
  - Status: Not Started
  - Priority: High
  - Dependencies: Directory structure
  - Notes: .env support, validation

- [ ] Implement Basic Auth header generation
  - Status: Not Started
  - Priority: High
  - Dependencies: Environment config
  - Notes: Base64 encoding of email:token

- [ ] Create main agent.py with MCPToolset configuration
  - Status: Not Started
  - Priority: High
  - Dependencies: Auth header generation
  - Notes: SseConnectionParams setup

- [ ] Add error handling and retry logic
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Main agent
  - Notes: Connection errors, auth failures

#### 2.2 API Key Agent Features
- [ ] Implement connection timeout handling
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Main agent
  - Notes: Configurable timeouts

- [ ] Add logging and monitoring
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Main agent
  - Notes: Structured logging for debugging

- [ ] Create helper scripts for testing
  - Status: Not Started
  - Priority: Low
  - Dependencies: Main agent
  - Notes: Quick test scripts for common operations

### Phase 3: OAuth2 Agent Implementation (0%)

#### 3.1 OAuth2 Foundation
- [ ] Create `jira_remote_mcp_oauth2_agent` directory structure
  - Status: Not Started
  - Priority: High
  - Dependencies: Phase 1.1
  - Notes: More complex than API key agent

- [ ] Implement OAuth2 configuration class
  - Status: Not Started
  - Priority: High
  - Dependencies: Directory structure
  - Notes: auth_config.py with Atlassian endpoints

- [ ] Create OAuth2 callback server
  - Status: Not Started
  - Priority: High
  - Dependencies: OAuth2 config
  - Notes: Local server for authorization code

- [ ] Implement secure token storage
  - Status: Not Started
  - Priority: High
  - Dependencies: OAuth2 config
  - Notes: File-based initially, keyring later

#### 3.2 OAuth2 Flow Implementation
- [ ] Implement authorization code flow
  - Status: Not Started
  - Priority: High
  - Dependencies: Callback server
  - Notes: Browser launch, code capture

- [ ] Add token exchange logic
  - Status: Not Started
  - Priority: High
  - Dependencies: Auth code flow
  - Notes: Code to token exchange

- [ ] Implement automatic token refresh
  - Status: Not Started
  - Priority: High
  - Dependencies: Token exchange
  - Notes: Handle expired tokens gracefully

- [ ] Create main OAuth2 agent
  - Status: Not Started
  - Priority: High
  - Dependencies: All OAuth2 components
  - Notes: Integrate all pieces

#### 3.3 Advanced OAuth2 Features
- [ ] Add multi-tenant support
  - Status: Not Started
  - Priority: Low
  - Dependencies: Main OAuth2 agent
  - Notes: Support multiple Jira instances

- [ ] Implement secure token storage with encryption
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Basic token storage
  - Notes: Use keyring + encryption

- [ ] Add session validation
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Main OAuth2 agent
  - Notes: Verify tokens are still valid

### Phase 4: Testing (0%)

#### 4.1 Unit Tests
- [ ] Write unit tests for API key authentication
  - Status: Not Started
  - Priority: High
  - Dependencies: API key agent
  - Notes: Mock MCP responses

- [ ] Write unit tests for OAuth2 flow
  - Status: Not Started
  - Priority: High
  - Dependencies: OAuth2 agent
  - Notes: Mock auth endpoints

- [ ] Test error handling scenarios
  - Status: Not Started
  - Priority: High
  - Dependencies: Both agents
  - Notes: Network errors, auth failures

- [ ] Test token refresh logic
  - Status: Not Started
  - Priority: High
  - Dependencies: OAuth2 agent
  - Notes: Expired token handling

#### 4.2 Integration Tests
- [ ] Create test Atlassian account/sandbox
  - Status: Not Started
  - Priority: High
  - Dependencies: None
  - Notes: Need real Jira instance for testing

- [ ] Test real MCP connection with API key
  - Status: Not Started
  - Priority: High
  - Dependencies: Test account, API key agent
  - Notes: Verify all MCP tools work

- [ ] Test real OAuth2 flow
  - Status: Not Started
  - Priority: High
  - Dependencies: Test account, OAuth2 agent
  - Notes: Full end-to-end flow

- [ ] Performance and latency testing
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Both agents working
  - Notes: Compare with local MCP server

### Phase 5: Documentation and Deployment (0%)

#### 5.1 Documentation
- [ ] Create comprehensive README for API key agent
  - Status: Not Started
  - Priority: High
  - Dependencies: API key agent complete
  - Notes: Setup guide, examples

- [ ] Create comprehensive README for OAuth2 agent
  - Status: Not Started
  - Priority: High
  - Dependencies: OAuth2 agent complete
  - Notes: OAuth setup, security notes

- [ ] Write migration guide from local MCP
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Both agents complete
  - Notes: Step-by-step migration

- [ ] Create troubleshooting guide
  - Status: Not Started
  - Priority: Medium
  - Dependencies: Testing complete
  - Notes: Common issues and solutions

#### 5.2 Deployment Preparation
- [ ] Create Docker configurations
  - Status: Not Started
  - Priority: Low
  - Dependencies: Both agents complete
  - Notes: Container deployment options

- [ ] Add CI/CD configuration
  - Status: Not Started
  - Priority: Low
  - Dependencies: Tests complete
  - Notes: GitHub Actions for testing

- [ ] Create deployment scripts
  - Status: Not Started
  - Priority: Low
  - Dependencies: Both agents complete
  - Notes: Easy deployment automation

## Risk Assessment

### High Risk Items
1. **MCP Server Availability**: Remote server might have different capabilities than local
2. **Authentication Complexity**: OAuth2 flow requires careful implementation
3. **Rate Limiting**: Remote server may have stricter limits
4. **Network Reliability**: Internet connectivity required

### Mitigation Strategies
1. Early testing with real Atlassian MCP server
2. Implement robust error handling and retry logic
3. Add connection pooling and caching where appropriate
4. Provide clear fallback options

## Dependencies and Prerequisites

### Required Before Starting
1. Atlassian account with API access
2. OAuth2 app registration (for OAuth2 agent)
3. Test Jira instance (cloud)
4. Understanding of MCP protocol

### External Dependencies
- `mcp` Python package (requires Python 3.10+)
- `aiohttp` for async HTTP
- `python-dotenv` for configuration
- `keyring` for secure storage (OAuth2)
- `cryptography` for token encryption (OAuth2)

## Success Criteria

1. Both agents can successfully connect to remote MCP server
2. All Jira operations work as expected
3. Authentication is secure and reliable
4. Performance is acceptable (< 2s for most operations)
5. Comprehensive documentation and examples provided
6. All tests pass with > 90% coverage

## Notes and Considerations

- **Priority Order**: API Key agent first (simpler), then OAuth2
- **Testing Strategy**: Use mocks for unit tests, real server for integration
- **Security Focus**: Never log tokens, use secure storage
- **User Experience**: Clear error messages, easy setup process
- **Maintainability**: Clean code, good documentation, CI/CD

## Progress Tracking

### Milestone 1: Foundation Complete (Target: 2 days)
- [ ] All Phase 1 tasks completed
- [ ] Basic project structure in place
- [ ] MCP server connectivity verified

### Milestone 2: API Key Agent Working (Target: 3 days)
- [ ] All Phase 2 tasks completed
- [ ] Basic integration tests passing
- [ ] Can perform Jira operations

### Milestone 3: OAuth2 Agent Working (Target: 5 days)
- [ ] All Phase 3 tasks completed
- [ ] OAuth2 flow fully functional
- [ ] Token refresh working

### Milestone 4: Testing Complete (Target: 3 days)
- [ ] All Phase 4 tasks completed
- [ ] > 90% test coverage
- [ ] All integration tests passing

### Milestone 5: Ready for Use (Target: 2 days)
- [ ] All Phase 5 tasks completed
- [ ] Documentation complete
- [ ] Deployment guides available

**Total Estimated Time**: 15 days

## How to Use This Document

1. **Update Status**: Change "Not Started" to "In Progress" when beginning a task
2. **Mark Complete**: Change to "Completed" and add completion date
3. **Add Notes**: Document any issues, decisions, or important information
4. **Track Progress**: Update overall and phase percentages regularly
5. **Review Dependencies**: Ensure prerequisites are met before starting tasks

## Change Log

- 2025-01-21: Initial task list created based on specifications