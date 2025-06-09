# Frontend Tool Integration Guide

## Overview

This guide explains how to integrate tool calling functionality in your frontend application when using Tavus CVI with the backend template. The frontend acts as a bridge between Tavus tool call events (sent via Daily room) and the backend tool execution endpoint.

## Prerequisites

- Daily.js SDK integrated in your frontend
- Authentication token for backend API calls
- Access to the Daily room where Tavus is running

## Integration Steps

### 1. Set Up Daily Event Listeners

First, set up listeners for Daily room events to catch tool call requests from Tavus:

```javascript
// Initialize Daily room
const callObject = DailyIframe.createCallObject({
  url: conversationUrl,
  token: dailyToken
});

// Listen for app messages (tool calls come through here)
callObject.on('app-message', handleAppMessage);

// Join the call
await callObject.join();
```

### 2. Handle Tool Call Events

Implement the handler to process tool call events from Tavus:

```javascript
async function handleAppMessage(event) {
  // Check if this is a tool call event
  if (event.data.type === 'tool-call' || event.data.event === 'tool_call') {
    const { tool_name, arguments, call_id } = event.data;
    
    console.log('Received tool call:', {
      tool_name,
      arguments,
      call_id
    });
    
    try {
      // Execute the tool via backend
      const result = await executeToolOnBackend(tool_name, arguments);
      
      // Send result back to Tavus
      await sendToolResultToTavus(call_id, result);
    } catch (error) {
      // Send error back to Tavus
      await sendToolErrorToTavus(call_id, error.message);
    }
  }
}
```

### 3. Execute Tool on Backend

Make the API call to execute the tool:

```javascript
async function executeToolOnBackend(toolName, toolArguments) {
  const response = await fetch(`${BACKEND_URL}/api/v1/tools/execute`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
      'X-Tenant-ID': tenantId,
      'X-Service-ID': serviceId
    },
    body: JSON.stringify({
      tool_name: toolName,
      arguments: toolArguments,
      persona_config_id: currentPersonaConfigId
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Tool execution failed');
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Tool execution failed');
  }
  
  return data.result;
}
```

### 4. Send Results Back to Tavus

Send the tool execution results back through the Daily room:

```javascript
async function sendToolResultToTavus(callId, result) {
  await callObject.sendAppMessage({
    type: 'tool-result',
    call_id: callId,
    result: result,
    success: true
  }, '*');
}

async function sendToolErrorToTavus(callId, errorMessage) {
  await callObject.sendAppMessage({
    type: 'tool-result',
    call_id: callId,
    error: errorMessage,
    success: false
  }, '*');
}
```

## Complete Integration Example

Here's a complete example of a React component handling tool calls:

```jsx
import React, { useEffect, useRef } from 'react';
import DailyIframe from '@daily-co/daily-js';

function TavusConversation({ conversationUrl, dailyToken, authToken, personaConfigId }) {
  const callObjectRef = useRef(null);
  
  useEffect(() => {
    if (!conversationUrl || !dailyToken) return;
    
    async function setupDaily() {
      // Create call object
      const callObject = DailyIframe.createCallObject({
        url: conversationUrl,
        token: dailyToken
      });
      
      callObjectRef.current = callObject;
      
      // Set up event handlers
      callObject.on('app-message', async (event) => {
        if (event.data.type === 'tool-call') {
          await handleToolCall(event.data);
        }
      });
      
      callObject.on('participant-joined', (event) => {
        console.log('Participant joined:', event);
      });
      
      callObject.on('error', (error) => {
        console.error('Daily error:', error);
      });
      
      // Join the call
      await callObject.join();
    }
    
    setupDaily();
    
    // Cleanup
    return () => {
      if (callObjectRef.current) {
        callObjectRef.current.leave();
        callObjectRef.current.destroy();
      }
    };
  }, [conversationUrl, dailyToken]);
  
  async function handleToolCall(toolCallData) {
    const { tool_name, arguments: args, call_id } = toolCallData;
    
    try {
      // Call backend
      const response = await fetch(`/api/v1/tools/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          tool_name,
          arguments: args,
          persona_config_id: personaConfigId
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Send success result
        await callObjectRef.current.sendAppMessage({
          type: 'tool-result',
          call_id,
          result: data.result,
          success: true
        }, '*');
      } else {
        // Send error
        await callObjectRef.current.sendAppMessage({
          type: 'tool-result',
          call_id,
          error: data.error,
          success: false
        }, '*');
      }
    } catch (error) {
      // Send error
      await callObjectRef.current.sendAppMessage({
        type: 'tool-result',
        call_id,
        error: error.message,
        success: false
      }, '*');
    }
  }
  
  return (
    <div className="tavus-container">
      <div id="daily-video-container" />
    </div>
  );
}
```

## Event Formats

### Tool Call Event (from Tavus)

```json
{
  "type": "tool-call",
  "tool_name": "sql_query",
  "arguments": {
    "query": "SELECT COUNT(*) FROM patients"
  },
  "call_id": "call_123456789"
}
```

### Tool Result Event (to Tavus)

Success:
```json
{
  "type": "tool-result",
  "call_id": "call_123456789",
  "result": {
    "rows": [{"count": 42}]
  },
  "success": true
}
```

Error:
```json
{
  "type": "tool-result",
  "call_id": "call_123456789",
  "error": "Tool not found: invalid_tool",
  "success": false
}
```

## Error Handling

1. **Network Errors**: Implement retry logic for transient failures
2. **Authentication Errors**: Refresh tokens and retry
3. **Tool Errors**: Display user-friendly messages
4. **Timeout Handling**: Set reasonable timeouts for tool execution

```javascript
async function executeToolWithRetry(toolName, args, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await executeToolOnBackend(toolName, args);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
}
```

## Security Considerations

1. **Token Management**: Never expose backend API tokens in frontend code
2. **Input Validation**: Validate tool arguments before sending to backend
3. **CORS Configuration**: Ensure proper CORS settings for API calls
4. **Rate Limiting**: Implement client-side rate limiting to prevent abuse

## Testing

### Manual Testing

1. Start a conversation with a tool-enabled persona
2. Ask questions that would trigger tool usage
3. Monitor browser console for tool call events
4. Verify tool results are properly displayed

### Automated Testing

```javascript
// Mock Daily call object
const mockCallObject = {
  sendAppMessage: jest.fn(),
  on: jest.fn(),
  join: jest.fn(),
  leave: jest.fn()
};

// Test tool call handling
test('handles tool call event', async () => {
  const handler = getAppMessageHandler(mockCallObject);
  
  await handler({
    data: {
      type: 'tool-call',
      tool_name: 'sql_query',
      arguments: { query: 'SELECT 1' },
      call_id: 'test_123'
    }
  });
  
  expect(mockCallObject.sendAppMessage).toHaveBeenCalledWith(
    expect.objectContaining({
      type: 'tool-result',
      call_id: 'test_123',
      success: true
    }),
    '*'
  );
});
```

## Debugging Tips

1. **Enable Verbose Logging**: Log all Daily events during development
2. **Use Browser DevTools**: Monitor network requests to backend
3. **Check Event Formats**: Ensure events match expected schemas
4. **Test Error Scenarios**: Deliberately trigger errors to test handling

```javascript
// Debug logging
callObject.on('app-message', (event) => {
  console.log('[Daily Event]', event);
});

// Log all tool executions
async function executeToolOnBackend(toolName, args) {
  console.log('[Tool Execute]', { toolName, args });
  const result = await /* ... */;
  console.log('[Tool Result]', result);
  return result;
}
```

## Common Issues

### Issue: Tool calls not being received
- Check Daily room permissions
- Verify event listener is properly attached
- Ensure Tavus persona has tools configured

### Issue: Authentication failures
- Verify token is included in headers
- Check token expiration
- Ensure tenant/service IDs are correct

### Issue: Tool results not affecting conversation
- Verify result format matches Tavus expectations
- Check call_id is correctly passed back
- Ensure success flag is set appropriately

## Next Steps

1. Implement comprehensive error handling
2. Add loading states during tool execution
3. Create UI indicators for tool usage
4. Implement tool result visualization
5. Add analytics for tool usage tracking