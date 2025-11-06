# Testing Checklist for Dispatcher Agents v2.0

## Pre-Testing Setup

### 1. Environment Configuration
- [ ] Backend `.env` file has:
  - [ ] `LIVEKIT_URL=ws://localhost:7880`
  - [ ] `LIVEKIT_API_KEY=<your_key>`
  - [ ] `LIVEKIT_API_SECRET=<your_secret>`
  - [ ] `OPENAI_API_KEY=<your_key>` (optional if not using LLM)

### 2. Services Running
- [ ] LiveKit server: `livekit-server` or Docker container
- [ ] Backend API: `python -m uvicorn backend/src/api/main:app --reload`
- [ ] Frontend: `cd frontend && npm run dev`
- [ ] Multi-agent worker: `cd backend && python agents/multi_agent_worker.py dev`

---

## Test 1: Custom Agent Prompts

### Objective
Verify that agents use UI-provided prompts instead of hardcoded defaults

### Steps

1. **Open Frontend**
   - Navigate to http://localhost:5173
   - See "AI Voice Agent Conversation" form

2. **Modify Agent Prompts**
   - Dispatcher prompt field:
     ```
     You are Tom, an aggressive dispatcher. 
     Push hard to get the driver to accept. 
     Be persuasive and mention top pay.
     ```
   - Driver prompt field:
     ```
     You are Sarah, a cautious driver.
     Ask lots of questions before committing.
     Only accept high-paying loads.
     ```

3. **Set Acting Notes** (Optional)
   - Dispatcher: "Be pushy about payment terms"
   - Driver: "Be skeptical about new companies"

4. **Create Room**
   - Click "Start Live Conversation" button
   - Wait for room to be created

5. **Verify Custom Prompts**
   - Check backend console output
   - Look for: `[PASS] Custom dispatcher prompt loaded from room metadata`
   - Should NOT see default prompts in agent behavior

### Expected Behavior
- ✅ Agents greet each other according to custom personalities
- ✅ Dispatcher emphasizes payment terms
- ✅ Driver asks critical questions
- ✅ Conversation tone matches custom prompts

### Verification
```bash
# In backend terminal, should see:
# "Custom dispatcher prompt loaded from room metadata"
# "Custom driver prompt loaded from room metadata"
```

---

## Test 2: Agent Tool Calling & Auto-Disconnect

### Objective
Verify agents can call `end_conversation()` tool and disconnect when done

### Steps

1. **Start Conversation**
   - From previous test, wait for agents to join
   - Listen to audio and watch participant list

2. **Wait for Conclusion**
   - Conversation naturally progresses
   - One agent should call `end_conversation()` when:
     - Agreement reached, OR
     - Driver rejects and won't reconsider, OR
     - Natural conclusion point reached

3. **Monitor Participant Disconnect**
   - Watch participant count in UI
   - Should go from 2 agents → 0 agents
   - Check backend logs

### Expected Behavior
- ✅ Agents converse naturally
- ✅ One agent calls `end_conversation()` tool
- ✅ Both agents disconnect from room
- ✅ Participant list shows 0 agents
- ✅ UI transitions from "connected" to "disconnected"

### Verification
```bash
# In backend terminal, should see:
# "=== DISPATCHER CALLING END CONVERSATION ==="
#  OR
# "=== DRIVER CALLING END CONVERSATION ==="
# "Dispatcher concluding - closing session"
# "Driver concluding - closing session"
```

---

## Test 3: Conversation Player & Playback

### Objective
Verify playback UI appears after conversation ends and controls work

### Steps

1. **Wait for Call Conclusion**
   - Continue from Test 2
   - Wait for agents to disconnect

2. **Player Appearance**
   - Check if playback player appears automatically
   - Should show:
     - [PASS] Conversation ID
     - [PASS] Current speaker and text
     - [PASS] Play/Pause/Next/Previous/Reset buttons
     - [PASS] Speed selector (0.75x - 2x)
     - [PASS] Transcript list

3. **Test Playback Controls**
   
   a) **Play/Pause**
   - [PASS] Click Play button
   - [PASS] Current turn displays
   - [PASS] Click Pause
   - [PASS] Stays on same turn

   b) **Navigation**
   - [PASS] Click Previous → goes to turn N-1
   - [PASS] Click Next → goes to turn N+1
   - [PASS] Click Reset → returns to turn 1
   - [PASS] Disabled buttons on boundaries (first/last turn)

   c) **Speed Control**
   - [PASS] Select 0.75x - displays correctly
   - [PASS] Select 1x (Normal) - base speed
   - [PASS] Select 2x - double speed
   - [PASS] Speed preference saved

   d) **Transcript Clicking**
   - [PASS] Click any turn in transcript list
   - [PASS] Jumps to that turn
   - [PASS] Current turn highlights in blue
   - [PASS] Progress bar updates

4. **Audio Player** (if recording available)
   - [PASS] Audio player visible
   - [PASS] Can play full conversation
   - [PASS] Standard HTML5 controls work

### Expected Behavior
- ✅ Player auto-appears when agents disconnect
- ✅ All controls are functional and responsive
- ✅ Transcript is complete and accurate
- ✅ Smooth animations/transitions
- ✅ Speed control updates in real-time

---

## Test 4: Conversation With Different Scenarios

### Objective
Test system works with various scenario configurations

### Scenarios to Test

1. **High-Value Load Acceptance**
   - Prompt Dispatcher: "You have a high-paying load"
   - Prompt Driver: "Only interested in premium rates"
   - Expected: Driver accepts quickly
   - Verify: ✅ Auto-disconnect when agreement reached

2. **Low-Rate Rejection**
   - Prompt Dispatcher: "Offering below-market rate"
   - Prompt Driver: "Must maintain high margin"
   - Expected: Driver declines
   - Verify: ✅ Auto-disconnect after rejection

3. **Negotiation Scenario**
   - Prompt Dispatcher: "Open to negotiating rate"
   - Prompt Driver: "Willing to negotiate payment"
   - Expected: Back-and-forth discussion
   - Verify: ✅ Players reach agreement or mutual conclusion

4. **Problem Scenario**
   - Prompt Dispatcher: "Complex load with issues"
   - Prompt Driver: "Careful about problem loads"
   - Expected: Questions and clarifications
   - Verify: ✅ Both agents handle complexity

### Expected Outcome
- ✅ Each scenario completes independently
- ✅ Playback available for each
- ✅ Conversation quality varies by scenario
- ✅ No cross-contamination between tests

---

## Test 5: API Endpoints

### Objective
Verify backend endpoints respond correctly

### 1. Create Room Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/rooms/create \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": {
      "loadId": "TEST-001",
      "loadType": "Test",
      "weight": 1000,
      "pickupLocation": "Test",
      "pickupTime": "9 AM",
      "pickupType": "drop",
      "deliveryLocation": "Test",
      "deliveryDeadline": "5 PM",
      "trailerType": "van",
      "ratePerMile": 1.5,
      "totalRate": 1000,
      "accessorials": "none",
      "securementRequirements": "basic",
      "tmsUpdate": "none"
    },
    "dispatcherAgent": {
      "role": "dispatcher",
      "prompt": "Test dispatcher"
    },
    "driverAgent": {
      "role": "driver",
      "prompt": "Test driver"
    }
  }'
```

**Expected Response:**
```json
{
  "roomName": "conv_TEST-001_...",
  "roomToken": "eyJh...",
  "livekitUrl": "ws://localhost:7880",
  "conversationId": "conv_TEST-001_..."
}
```

- [ ] Status: 200 OK
- [ ] Response contains room name
- [ ] Response contains valid JWT token
- [ ] conversationId matches roomName

### 2. Room Status Endpoint
```bash
curl http://localhost:8000/api/v1/rooms/{room_name}/status
```

**Expected Response:**
```json
{
  "roomName": "conv_TEST-001_...",
  "participantCount": 2,
  "participants": [
    {"identity": "dispatcher", "name": "Dispatcher", "state": "..."},
    {"identity": "driver", "name": "Driver", "state": "..."}
  ]
}
```

- [ ] Status: 200 OK
- [ ] Shows correct participant count
- [ ] Lists all participants
- [ ] Updates as agents join/leave

### 3. Recording Endpoint
```bash
curl http://localhost:8000/api/v1/rooms/{room_name}/recording
```

**Expected Response (if recording available):**
```json
{
  "roomName": "conv_TEST-001_...",
  "recordingAvailable": true,
  "recordings": [...]
}
```

OR (if not available):
```json
{
  "roomName": "conv_TEST-001_...",
  "recordingAvailable": false,
  "message": "Recording functionality requires LiveKit Pro or Enterprise"
}
```

- [ ] Status: 200 OK
- [ ] Either has recording or explains why not
- [ ] Response format valid

---

## Test 6: Frontend Integration

### Objective
Verify frontend components work correctly

### UI Flow Check
- [ ] Form loads with default values
- [ ] Can edit all fields (prompts, notes, scenario)
- [ ] "Start Live Conversation" button enables
- [ ] Loading indicator appears during room creation
- [ ] Room connection status updates
- [ ] Participant cards show both agents
- [ ] Audio plays through browser
- [ ] Playback controls visible after conclusion

### Responsive Design
- [ ] Desktop (1920x1080): All elements visible and aligned
- [ ] Tablet (768x1024): Layout adapts properly
- [ ] Mobile (375x667): Scrollable, no horizontal overflow
- [ ] All buttons clickable on touch devices

### Error Handling
- [ ] Missing env variables shown as helpful error
- [ ] Network errors display gracefully
- [ ] Invalid room shows appropriate message
- [ ] Agent join failures explained

---

## Test 7: Browser DevTools Checks

### Console
```bash
# In browser console (F12 → Console tab)
```
- [ ] No JavaScript errors
- [ ] No CORS errors
- [ ] WebSocket connections successful
- [ ] API calls complete successfully

### Network Tab
- [ ] POST /api/v1/rooms/create returns 200
- [ ] GET /api/v1/rooms/{name}/status returns 200
- [ ] WebSocket connects to LiveKit
- [ ] No 404 or 500 errors

### Application Tab
- [ ] localStorage/sessionStorage not corrupted
- [ ] Cookies configured correctly

---

## Test 8: Performance

### Objective
Verify system handles conversations efficiently

### Metrics to Monitor
- [ ] Conversation starts within 5 seconds of room creation
- [ ] Agent responses occur within 2-3 seconds
- [ ] No lag during playback
- [ ] Player UI responsive (< 100ms)
- [ ] No memory leaks (DevTools → Memory)
- [ ] No excessive CPU usage (typically < 50%)

### Stress Test (Optional)
- [ ] Create 3-5 conversations in sequence
- [ ] System handles multiple concurrent rooms
- [ ] No performance degradation
- [ ] All conversations record properly

---

## Test 9: Regression Testing

### Objective
Ensure no existing functionality broken

### Existing Features
- [ ] Basic room creation still works
- [ ] Agents join correct room
- [ ] Audio streams properly
- [ ] Participant detection works
- [ ] Room status updates
- [ ] Agents can use their tools (mark_load_accepted, etc.)

---

## Issue Documentation Template

If you find issues, document them:

```
**Issue #X: [Title]**
- **Test**: [Which test found this]
- **Steps to Reproduce**:
  1. ...
  2. ...
  3. ...
- **Expected**: [What should happen]
- **Actual**: [What actually happened]
- **Logs**: [Relevant console/terminal output]
- **Screenshot**: [If applicable]
- **Severity**: [Critical/High/Medium/Low]
- **Environment**: [Browser, OS, Node version, Python version]
```

---

## Sign-Off Checklist

When all tests pass:

- [ ] All 9 test categories complete
- [ ] No critical issues remaining
- [ ] Performance acceptable
- [ ] No console errors
- [ ] Playback works smoothly
- [ ] Custom prompts working
- [ ] Auto-disconnect functioning
- [ ] API endpoints responding
- [ ] Ready for production

---

## Test Results Template

```
Test Run: [Date/Time]
Tester: [Your Name]
Environment: [Windows/Mac/Linux]
Browser: [Chrome/Firefox/Safari]

Test 1 - Custom Prompts: [PASS/FAIL]
Test 2 - Auto-Disconnect: [PASS/FAIL]
Test 3 - Playback Player: [PASS/FAIL]
Test 4 - Multiple Scenarios: [PASS/FAIL]
Test 5 - API Endpoints: [PASS/FAIL]
Test 6 - Frontend Integration: [PASS/FAIL]
Test 7 - Browser DevTools: [PASS/FAIL]
Test 8 - Performance: [PASS/FAIL]
Test 9 - Regression: [PASS/FAIL]

Overall: [PASS/FAIL]
Issues Found: [List any issues]
Notes: [Any additional notes]
```

---

## Quick Commands Reference

```bash
# Backend
cd backend
python -m uvicorn src/api/main:app --reload

# Frontend
cd frontend
npm run dev

# Multi-agent worker
cd backend
python agents/multi_agent_worker.py dev

# Integration tests
cd backend
python test_integration_v2.py

# Check room status
curl http://localhost:8000/api/v1/rooms/{room_name}/status

# Get recording
curl http://localhost:8000/api/v1/rooms/{room_name}/recording
```

---

Generated: 2025-01-05
Status: Ready for Testing ✅

