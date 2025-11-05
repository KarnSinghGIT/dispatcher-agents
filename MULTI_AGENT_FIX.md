# Fix: Multiple Agents Joining Same Room

## Problem
Only one agent was joining the room because LiveKit's worker dispatch system uses **load balancing** - it dispatches only **one worker per room** by default. Running two separate workers causes them to compete for room assignments.

## Solution
Created a **single multi-agent worker** (`multi_agent_worker.py`) that manages both agents (Dispatcher and Driver) in the same room, running them as two separate `AgentSession` instances within one worker process.

## Changes Made

### 1. Multi-Agent Worker (`backend/agents/multi_agent_worker.py`) - NEW
- Created a single worker process that runs both agents
- Manages two separate `AgentSession` instances:
  - Dispatcher session with "alloy" voice
  - Driver session with "echo" voice
- Both sessions start concurrently in the same room
- Enhanced logging to track participant info and session startup

### 2. Frontend Updates
- Updated `App.tsx` instructions to use `multi_agent_worker.py`
- Updated `ConversationRoom.tsx` warning message
- Changed from "run two terminals" to "run single worker"

### 3. Documentation
- Created `MULTI_AGENT_WORKER_GUIDE.md` with detailed explanation
- Updated this fix document to reflect new approach

## How It Works Now

1. **Single worker process** runs both agents:
   - One `multi_agent_worker.py` process
   - Two `AgentSession` instances within it

2. **When a room is created**, LiveKit dispatches to the worker, which:
   - Starts dispatcher `AgentSession`
   - Starts driver `AgentSession`
   - Both sessions connect to the same room

3. **Both agents join the same room** and can interact with each other through their separate sessions

## Testing

To verify both agents join:

1. **Start the multi-agent worker**:
   ```bash
   cd backend
   python agents/multi_agent_worker.py dev
   ```
   
   You should see:
   ```
   Worker registered
   === MULTI-AGENT WORKER STARTING ===
   Room: conv_HDX-2478_20250106_...
   ✓ Dispatcher agent session started
   ✓ Driver agent session started
   ```

2. **Create a room** via the frontend or API

3. **Check the logs** - you should see both sessions starting and participant info

4. **Check the UI** - both agents should appear (if participant identities match frontend filters)

## Key Points

- **Single worker process** manages both agents
- Both agents run as separate `AgentSession` instances
- Worker must be **running before** creating a room
- Agents automatically join when the worker is dispatched
- Logs show participant information for debugging

## Troubleshooting

If agents don't appear or only one seems active:

1. **Verify worker is running** - check for "Worker registered" in logs
2. **Check both sessions started** - look for "✓ Dispatcher agent session started" and "✓ Driver agent session started"
3. **Check participant info** - logs show participant identities and names
4. **Verify LiveKit connection** - ensure worker connects to correct LiveKit server
5. **Check frontend filters** - participant names/identities must match frontend detection logic
6. **Check room status** - use `/api/v1/rooms/{room_name}/status` endpoint

## Expected Behavior

When a room is created and worker is dispatched:
- ✅ Multi-agent worker logs: "=== MULTI-AGENT WORKER STARTING ==="
- ✅ Both sessions start: "✓ Dispatcher agent session started" and "✓ Driver agent session started"
- ✅ Participant info logged showing both agents (or remote participants)
- ✅ Dispatcher initiates conversation
- ✅ Driver responds naturally

## Why Not Two Separate Workers?

LiveKit's design uses worker load balancing:
- Multiple workers = horizontal scaling for high traffic
- Each room gets ONE worker (for resource efficiency)
- To have multiple agents in ONE room = ONE worker managing multiple agents

This is the intended design pattern for multi-agent conversations.

