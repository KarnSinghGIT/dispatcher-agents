# Multi-Agent Worker Guide

## Overview

To have both the Dispatcher and Driver agents join the same room, we use a **single multi-agent worker** instead of running two separate workers. This approach ensures both agents are part of the same LiveKit room session.

## Why This Approach?

LiveKit's worker dispatch system is designed for **load balancing** - by default, it dispatches only **one worker per room**. When you run multiple workers with the same configuration:
- They compete for room assignments
- Only one gets dispatched to each room
- This is intentional for horizontal scaling

To have **multiple agents in the same room**, we need a **single worker process** that manages both agents simultaneously.

## Architecture

```
┌─────────────────────────────────────┐
│   Multi-Agent Worker Process        │
│                                      │
│  ┌──────────────┐  ┌──────────────┐│
│  │ Dispatcher   │  │ Driver       ││
│  │ AgentSession │  │ AgentSession ││
│  │   (Tim)      │  │   (Chris)    ││
│  └──────────────┘  └──────────────┘│
│                                      │
│  Both sessions running concurrently  │
│  in the same room                    │
└─────────────────────────────────────┘
```

## Usage

### 1. Start the Multi-Agent Worker

```bash
cd backend
python agents/multi_agent_worker.py dev
```

You should see:
```
INFO:livekit.agents:Worker registered
INFO:multi_agent_worker:=== MULTI-AGENT WORKER STARTING ===
INFO:multi_agent_worker:Room: conv_HDX-2478_...
INFO:multi_agent_worker:✓ Dispatcher agent session started
INFO:multi_agent_worker:✓ Driver agent session started
```

### 2. Create a Room

Use the frontend to create a room or call the API:

```bash
curl -X POST http://localhost:8000/api/v1/rooms/create \
  -H "Content-Type: application/json" \
  -d @scenario.json
```

### 3. Both Agents Join Automatically

The single worker process will:
1. Receive the dispatch request
2. Start both agent sessions
3. Both agents join the room
4. Dispatcher initiates the conversation

## Files

- **`backend/agents/multi_agent_worker.py`**: Main worker that runs both agents
- **`backend/agents/dispatcher_agent.py`**: Dispatcher agent class (used by multi-agent worker)
- **`backend/agents/driver_agent.py`**: Driver agent class (used by multi-agent worker)

## Agent Configuration

Each agent gets its own `AgentSession` with:

### Dispatcher (Tim)
- Model: `gpt-4o-realtime-preview-2024-12-17`
- Voice: `alloy`
- Temperature: `0.8`
- Initiates conversation

### Driver (Chris)
- Model: `gpt-4o-realtime-preview-2024-12-17`
- Voice: `echo`
- Temperature: `0.7`
- Responds to dispatcher

## Troubleshooting

### Both agents not appearing in UI

The frontend looks for participants with specific keywords:
- Dispatcher: "dispatcher", "tim", or identity contains "dispatcher"
- Driver: "driver", "chris", or identity contains "driver"

Check the worker logs to see what participant identities are being used:

```
INFO:multi_agent_worker:Local participant identity: agent_abc123
INFO:multi_agent_worker:Local participant name: None
```

If the identities don't match the frontend filters, the agents won't appear in the UI even though they're in the room.

### Only one agent speaking

If both agents are in the room but only one speaks, check:
1. Both `AgentSession.start()` calls completed successfully
2. Both agents have audio tracks
3. No errors in the worker logs

### Worker not dispatching to rooms

Ensure:
1. Worker is registered before room creation
2. LiveKit credentials are correct in `.env`
3. LiveKit server is running

## Comparing Approaches

### ❌ Two Separate Workers (Doesn't Work)

```bash
# Terminal 1
python agents/dispatcher_agent.py dev

# Terminal 2
python agents/driver_agent.py dev
```

**Problem**: Only one worker gets dispatched to each room (load balancing behavior)

### ✅ Single Multi-Agent Worker (Works)

```bash
# Single Terminal
python agents/multi_agent_worker.py dev
```

**Solution**: One worker manages both agents in the same room

## Advanced: Custom Participant Names

If you need to set custom participant identities for the agents, you can configure the connection options when starting the session. However, this requires modifying the LiveKit Agents framework's internal behavior and is not currently exposed in the public API.

## Next Steps

- Monitor the worker logs to understand participant identities
- Update frontend filters if needed to match actual participant names
- Add more agents by creating additional `AgentSession` instances in the worker
- Implement agent-to-agent communication patterns

