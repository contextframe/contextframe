# Tool Calling Integration Guide for Frontend Team

## Overview

This guide provides complete documentation for integrating tool calling functionality between Tavus CVI and the backend. The frontend acts as a bridge, catching tool call events from Tavus (via Daily.co) and executing them through the backend API.

## Architecture Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │────▶│    Tavus    │────▶│   Daily     │────▶│  Frontend   │
│             │     │   Agent     │     │    Room     │     │  (React)    │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                                                          POST /tools/execute
                                                                    ▼
                                                          ┌─────────────────┐
                                                          │   Backend API   │
                                                          │  (FastAPI)      │
                                                          └─────────────────┘
```

## Event Flow Sequence

1. **User asks question** → Tavus agent processes it
2. **Agent decides to use tool** → Sends tool call event via Daily
3. **Frontend receives event** → Extracts tool name and arguments
4. **Frontend calls backend** → POST /api/v1/tools/execute
5. **Backend executes tool** → Returns result
6. **Frontend sends result to Tavus** → Via Daily sendAppMessage
7. **Tavus uses result** → Continues conversation with user

## Daily.co Event Structure

### Incoming Tool Call Event (from Tavus)

```javascript
{
  "type": "tool-call",        // or "app-message" with event: "tool_call"
  "tool_name": "sql_query",   // Name of the tool to execute
  "arguments": {              // Tool-specific arguments
    "query": "SELECT COUNT(*) FROM patients",
    "params": {}
  },
  "call_id": "call_abc123",   // Unique ID to track this call
  "participant_id": "tavus-agent-id"
}
```

### Outgoing Tool Result Event (to Tavus)

```javascript
// Success case
{
  "type": "tool-result",
  "call_id": "call_abc123",  // Must match the original call_id
  "success": true,
  "result": {                 // Tool execution result
    "rows": [{"count": 42}]
  }
}

// Error case
{
  "type": "tool-result",
  "call_id": "call_abc123",
  "success": false,
  "error": "Tool not found: invalid_tool"
}
```

## Backend API Integration

### Endpoint: POST /api/v1/tools/execute

**Request:**
```http
POST /api/v1/tools/execute
Content-Type: application/json
Authorization: Bearer <api_key>
X-Service-Id: <service_id>        # REQUIRED for service-scoped keys
X-Tenant-Id: <tenant_id>          # Optional

{
  "tool_name": "sql_query",
  "arguments": {
    "query": "SELECT * FROM patients LIMIT 10",
    "params": {}
  },
  "persona_config_id": "persona_123"  // From current session
}
```

**Response (Success):**
```json
{
  "success": true,
  "result": {
    "rows": [
      {"id": 1, "name": "John Doe", "age": 45},
      {"id": 2, "name": "Jane Smith", "age": 32}
    ]
  },
  "error": null
}
```

**Response (Error):**
```json
{
  "success": false,
  "result": null,
  "error": "Tool 'invalid_tool' not found for agent"
}
```

## Frontend Implementation

### 1. Complete React Component Example

```jsx
import React, { useEffect, useRef, useCallback } from 'react';
import DailyIframe from '@daily-co/daily-js';

function TavusConversationWithTools({ 
  conversationUrl, 
  dailyToken, 
  authToken,
  serviceId,
  tenantId,
  personaConfigId 
}) {
  const callObjectRef = useRef(null);
  
  // Handle incoming app messages from Daily
  const handleAppMessage = useCallback(async (event) => {
    console.log('[Daily Event]', event);
    
    // Check if this is a tool call
    if (event.data?.type === 'tool-call' || event.data?.event === 'tool_call') {
      const { tool_name, arguments: args, call_id } = event.data;
      
      console.log('[Tool Call Received]', {
        tool_name,
        arguments: args,
        call_id
      });
      
      try {
        // Execute tool via backend
        const result = await executeToolOnBackend(
          tool_name,
          args,
          personaConfigId,
          { authToken, serviceId, tenantId }
        );
        
        // Send success result back
        await sendToolResult(call_id, result, true);
      } catch (error) {
        console.error('[Tool Execution Error]', error);
        // Send error result back
        await sendToolResult(call_id, null, false, error.message);
      }
    }
  }, [personaConfigId, authToken, serviceId, tenantId]);
  
  // Execute tool on backend
  const executeToolOnBackend = async (toolName, toolArgs, personaId, auth) => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/tools/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${auth.authToken}`,
        'X-Service-Id': auth.serviceId,
        'X-Tenant-Id': auth.tenantId
      },
      body: JSON.stringify({
        tool_name: toolName,
        arguments: toolArgs,
        persona_config_id: personaId
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Tool execution failed');
    }
    
    return data.result;
  };
  
  // Send tool result back to Tavus
  const sendToolResult = useCallback(async (callId, result, success, error = null) => {
    if (!callObjectRef.current) return;
    
    const message = {
      type: 'tool-result',
      call_id: callId,
      success: success,
      result: success ? result : null,
      error: success ? null : error
    };
    
    console.log('[Sending Tool Result]', message);
    
    try {
      await callObjectRef.current.sendAppMessage(message, '*');
    } catch (err) {
      console.error('[Send Message Error]', err);
    }
  }, []);
  
  // Set up Daily room
  useEffect(() => {
    if (!conversationUrl || !dailyToken) return;
    
    const setupDaily = async () => {
      try {
        const callObject = DailyIframe.createCallObject({
          url: conversationUrl,
          token: dailyToken
        });
        
        callObjectRef.current = callObject;
        
        // Set up event handlers
        callObject.on('app-message', handleAppMessage);
        
        callObject.on('joined-meeting', () => {
          console.log('[Daily] Joined meeting');
        });
        
        callObject.on('error', (error) => {
          console.error('[Daily Error]', error);
        });
        
        // Join the call
        await callObject.join();
      } catch (error) {
        console.error('[Daily Setup Error]', error);
      }
    };
    
    setupDaily();
    
    // Cleanup
    return () => {
      if (callObjectRef.current) {
        callObjectRef.current.leave();
        callObjectRef.current.destroy();
      }
    };
  }, [conversationUrl, dailyToken, handleAppMessage]);
  
  return (
    <div className="tavus-conversation-container">
      <div id="daily-video-container" style={{ width: '100%', height: '600px' }} />
    </div>
  );
}

export default TavusConversationWithTools;
```

### 2. Error Handling and Retry Logic

```javascript
// Robust tool execution with retry
async function executeToolWithRetry(toolName, args, config, maxRetries = 3) {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`[Tool Execute] Attempt ${attempt}/${maxRetries}`);
      
      const result = await executeToolOnBackend(toolName, args, config);
      return result;
      
    } catch (error) {
      lastError = error;
      console.error(`[Tool Execute] Attempt ${attempt} failed:`, error);
      
      // Don't retry on client errors (4xx)
      if (error.status && error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      // Exponential backoff
      if (attempt < maxRetries) {
        const delay = Math.pow(2, attempt - 1) * 1000;
        console.log(`[Tool Execute] Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
}
```

### 3. TypeScript Interfaces

```typescript
// Event types
interface ToolCallEvent {
  type: 'tool-call' | 'app-message';
  event?: 'tool_call';
  tool_name: string;
  arguments: Record<string, any>;
  call_id: string;
  participant_id?: string;
}

interface ToolResultEvent {
  type: 'tool-result';
  call_id: string;
  success: boolean;
  result?: any;
  error?: string;
}

// API types
interface ToolExecuteRequest {
  tool_name: string;
  arguments: Record<string, any>;
  persona_config_id: string;
}

interface ToolExecuteResponse {
  success: boolean;
  result?: any;
  error?: string;
}

// Auth config
interface AuthConfig {
  authToken: string;
  serviceId: string;
  tenantId?: string;
}
```

## Available Tools by Agent

### Healthcare Agent
- **sql_query**: Execute SQL queries against patient database
  ```javascript
  {
    "tool_name": "sql_query",
    "arguments": {
      "query": "SELECT * FROM patients WHERE age > :min_age",
      "params": {"min_age": 65}
    }
  }
  ```

- **vector_search**: Search medical knowledge base
  ```javascript
  {
    "tool_name": "vector_search",
    "arguments": {
      "query": "diabetes treatment options",
      "namespace": "healthcare",
      "limit": 10
    }
  }
  ```

### Education Agent
- **sql_query**: Query student and course data
- **vector_search**: Search educational content

### Exa Agent
- **exa_search**: Web search using Exa API
  ```javascript
  {
    "tool_name": "exa_search",
    "arguments": {
      "query": "latest FDA guidelines 2024",
      "num_results": 5
    }
  }
  ```

## Testing Tool Integration

### 1. Manual Testing Script

Use the provided simulation script:
```bash
# Set your API key
export API_KEY=your_api_key_here
export SERVICE_ID=healthcare

# Run the simulation
python scripts/debugging/simulate_frontend_tool_calls.py
```

### 2. Frontend Debug Mode

Add debug logging to your frontend:
```javascript
// Debug mode flag
const DEBUG_TOOLS = process.env.REACT_APP_DEBUG_TOOLS === 'true';

// Debug logger
function debugLog(category, ...args) {
  if (DEBUG_TOOLS) {
    console.log(`[${category}]`, new Date().toISOString(), ...args);
  }
}

// Use throughout your code
debugLog('Tool Call', { tool_name, arguments: args });
debugLog('Backend Response', { status: response.status, data });
debugLog('Daily Message', { type: 'tool-result', call_id });
```

### 3. Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Missing X-Service-Id header" | Service-scoped API key without header | Always include X-Service-Id |
| "Tool not found" | Tool not available for agent | Check agent's tool list |
| "Invalid arguments" | Malformed tool arguments | Validate against tool schema |
| No response from Tavus | Wrong call_id in response | Ensure call_id matches exactly |
| Daily connection issues | Invalid token or URL | Verify conversation credentials |

## Security Considerations

1. **API Key Management**
   - Never expose API keys in frontend code
   - Use environment variables
   - Consider using a proxy endpoint

2. **Input Validation**
   - Validate tool arguments before sending
   - Sanitize any user-provided data
   - Check argument types and limits

3. **Rate Limiting**
   - Implement client-side rate limiting
   - Handle 429 responses gracefully
   - Use exponential backoff for retries

## Performance Optimization

1. **Debouncing**
   - Prevent rapid repeated tool calls
   - Implement cooldown between calls

2. **Caching**
   - Cache frequently used tool results
   - Set appropriate TTL values

3. **Loading States**
   - Show loading indicators during tool execution
   - Disable UI interactions while processing

## Example Tool Call Flow Logs

```
[Daily Event] 2024-06-06T10:30:45.123Z {type: 'tool-call', tool_name: 'sql_query', ...}
[Tool Call Received] {tool_name: 'sql_query', call_id: 'call_abc123'}
[Tool Execute] Attempt 1/3
[Backend Response] {status: 200, data: {success: true, result: {...}}}
[Sending Tool Result] {type: 'tool-result', call_id: 'call_abc123', success: true}
[Daily Message] Message sent successfully
```

## Support and Debugging

For issues or questions:
1. Check the simulation script: `scripts/debugging/simulate_frontend_tool_calls.py`
2. Review backend logs for tool execution errors
3. Use the debug scripts in `scripts/debugging/` for testing
4. Refer to the architecture documentation in `.claude/architecture/tool-calling.md`