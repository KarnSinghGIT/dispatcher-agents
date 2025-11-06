# Quick Start Guide: Dispatcher Agents v2.0

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.8+
- Node.js 16+
- LiveKit running locally
- Backend `.env` configured

---

## Step 1: Verify Environment

```bash
# Check Python
python --version  # Should be 3.8+

# Check Node
node --version   # Should be 16+

# Check .env exists
cat backend/.env  # Should have LIVEKIT_URL, API_KEY, API_SECRET
```

---

## Step 2: Start Backend Services

### Terminal 1: Backend API
```bash
cd backend
python -m uvicorn src/api/main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Multi-Agent Worker
```bash
cd backend
python agents/multi_agent_worker.py dev
```

Expected output:
```
Worker registered with room function
Listening for rooms to join...
```

### Terminal 3: Frontend
```bash
cd frontend
npm install  # (only first time)
npm run dev
```

Expected output:
```
Local: http://localhost:5173/
```

---

## Step 3: Open Application

1. Open browser: http://localhost:5173
2. You should see the "AI Voice Agent Conversation" form

---

## Step 4: Run a Test Conversation

### Simple Test (Use Defaults)
1. Scroll to bottom of form
2. Click **"🚀 Start Live Conversation"**
3. Wait 5-10 seconds for agents to join
4. Listen to conversation
5. Watch playback player appear when done

### Custom Behavior Test
1. In "Dispatcher Agent Configuration" section:
   ```
   Replace prompt with:
   "You are aggressive. Push hard. Mention top pay ($3/mile)."
   ```

2. In "Driver Agent Configuration" section:
   ```
   Replace prompt with:
   "You are skeptical. Ask lots of questions. Only accept premium rates."
   ```

3. Click **"🚀 Start Live Conversation"**
4. Observe agents following your custom instructions
5. Review playback

---

## Step 5: Verify Everything Works

### Check Integration Tests
```bash
cd backend
python test_integration_v2.py
```

Should show: **5/5 tests passed ✅**

### Check Console (Browser F12)
- [ ] No JavaScript errors
- [ ] API calls showing 200 responses
- [ ] WebSocket connected

### Check Terminals
- [ ] Backend: Room created message
- [ ] Worker: Agents joined message
- [ ] Worker: Agent calls end_conversation

---

## Common Scenarios to Test

### Scenario 1: Quick Agreement
**Dispatcher Prompt:**
```
You are Tom, a friendly dispatcher offering a great deal.
Rate is $2.50/mile.
Be upbeat and close the deal quickly.
```

**Driver Prompt:**
```
You are Rick, an experienced driver.
If the rate is good and conditions work, accept quickly.
Keep it simple.
```

**Expected:** Agents agree within 1-2 minutes

### Scenario 2: Tough Negotiation
**Dispatcher Prompt:**
```
You are a tough negotiator. Offer $1.50/mile.
Try to defend the low rate but be willing to negotiate up to $1.80.
```

**Driver Prompt:**
```
You need at least $2.00/mile. 
Push back on low offers.
Walk away if they won't meet your minimum.
```

**Expected:** Negotiation back-and-forth, possible rejection

### Scenario 3: Problem Solving
**Dispatcher Prompt:**
```
This load has some issues:
- Night delivery required
- Unusual securement needed
- Limited availability

Honestly discuss challenges but emphasize premium rate ($2.80/mile).
```

**Driver Prompt:**
```
You care about safety and legality.
Ask detailed questions about unusual requirements.
Factor in extra risk when pricing.
```

**Expected:** Deep discussion with many questions

---

## Playback Controls Explained

Once a conversation completes:

| Button | Action |
|--------|--------|
| ▶️ Play/Pause | Start/stop playback |
| ⏮ Previous | Go to previous turn |
| Next ⏭ | Go to next turn |
| 🔄 Reset | Return to beginning |
| Speed | Select playback speed (0.75x-2x) |
| Audio Player | Play full recording (if available) |
| Transcript | Click any turn to jump to it |

---

## Troubleshooting

### Issue: "Waiting for agents to join..." (stays stuck)

**Solution 1: Check Worker Running**
```bash
# Terminal 2 should show:
# "Worker registered with room function"
# If not, restart worker
cd backend
python agents/multi_agent_worker.py dev
```

**Solution 2: Check LiveKit**
```bash
# Verify LiveKit is running
# Should be accessible at ws://localhost:7880
# Check your LiveKit setup
```

**Solution 3: Check Credentials**
```bash
# Verify backend/.env has:
# LIVEKIT_URL=ws://localhost:7880
# LIVEKIT_API_KEY=<your_key>
# LIVEKIT_API_SECRET=<your_secret>
cat backend/.env
```

### Issue: "Failed to create room" error

**Solution:**
```bash
# Check backend logs
# Should see POST /api/v1/rooms/create in logs
# Verify response includes roomName and token

# Test API directly:
curl -X POST http://localhost:8000/api/v1/rooms/create \
  -H "Content-Type: application/json" \
  -d '{"scenario":{"loadId":"TEST"},...}'
```

### Issue: Agents don't use custom prompts

**Solution:**
```bash
# Check worker terminal logs
# Should show: "Custom dispatcher prompt loaded from room metadata"

# If not, verify:
# 1. Custom prompt text is not empty
# 2. Form submitted with custom prompts
# 3. Room status shows metadata

curl http://localhost:8000/api/v1/rooms/{room_name}/status
```

### Issue: No playback after conversation

**Solution:**
1. Wait 2-3 seconds after agents disconnect
2. Refresh page (F5)
3. Check browser console for errors
4. Verify agents actually disconnected (participant count = 0)

---

## Understanding the Conversation Flow

```
1. You fill in form with custom prompts
         ↓
2. Click "Start Live Conversation"
         ↓
3. Room created (visible in backend logs)
         ↓
4. Agents join (2-5 seconds)
         ↓
5. Agents begin conversation
         ↓
6. Agents converse using YOUR custom prompts
         ↓
7. When done, one agent calls end_conversation()
         ↓
8. Both agents disconnect
         ↓
9. You see playback player
         ↓
10. Review and analyze conversation
```

---

## Next: Run the Full Test Suite

When ready to verify everything:

```bash
cd backend
python test_integration_v2.py
```

**You should see:**
```
Results: 5/5 tests passed

- Custom Prompts: PASS
- End Conversation Tool: PASS  
- API Endpoints: PASS
- Frontend Components: PASS
- Configuration: PASS

All tests passed! Implementation ready for testing.
```

---

## Key Differences from v1.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Agent Prompts | Hardcoded | UI-Configurable |
| Conversation Limit | Max 20 turns (fixed) | Natural conclusion |
| Disconnection | Manual loop | Tool-based |
| Playback | Not available | Full playback |
| Transcript | Not available | Full transcript |
| Speed Control | N/A | 0.75x - 2x |
| Acting Notes | Not supported | Fully supported |

---

## What's New in v2.0

✨ **Three Major Features:**

1. **UI-Driven Behavior**
   - Define agent personalities from UI
   - Acting notes for additional context
   - No code changes needed for new behaviors

2. **Automatic Conversation Conclusion**
   - Agents determine when done
   - Tool-based signaling
   - Natural conversation flow

3. **Full Conversation Playback**
   - Review entire conversation
   - Speed controls
   - Jump to any turn
   - Audio playback (if available)

---

## Tips for Best Results

1. **Clear Prompts**
   - Be specific about personality/goals
   - Keep prompts realistic
   - Include constraints/limits

2. **Reasonable Scenarios**
   - Use realistic load details
   - Set competitive rates
   - Include relevant terms

3. **Watch the Logs**
   - Backend terminal shows what agents are doing
   - Agent terminal shows each response
   - Helps understand behavior

4. **Use Playback to Learn**
   - Review conversations to see patterns
   - Experiment with different prompts
   - Measure effectiveness

---

## Performance Expectations

- **Room Creation:** < 1 second
- **Agent Join Time:** 2-5 seconds
- **First Agent Response:** 3-5 seconds
- **Conversation Duration:** 1-5 minutes
- **Playback Load:** < 500ms
- **Player Response:** < 100ms

---

## When to Stop & Review

The system runs until agents call `end_conversation()`. This typically happens when:
- Agreement reached ✅
- Driver declines repeatedly ❌
- Natural conclusion reached 🏁
- Misunderstanding resolved ✓

If agents keep talking:
- Let them finish naturally (they'll conclude)
- Agents have time limit (set by your LLM)
- You can always stop browser and check logs

---

## Next: Full Testing

When ready for production:

1. Follow `TESTING_CHECKLIST_V2.md`
2. Run manual tests for each feature
3. Test on different browsers
4. Test on mobile devices
5. Document any issues

---

## Support

**Can't get it working?**

1. Check all three terminals are running
2. Check backend `.env` configured
3. Run integration tests: `python test_integration_v2.py`
4. Check browser console (F12)
5. Review logs in all terminals

**Need more info?**

- `IMPLEMENTATION_GUIDE_V2.md` - Complete details
- `TESTING_CHECKLIST_V2.md` - Full testing procedures
- `IMPLEMENTATION_SUMMARY.md` - What changed & why

---

## You're Ready! 🎉

You now have a fully functional multi-agent conversation system with:
- ✅ Custom agent behavior from UI
- ✅ Automatic conversation conclusion
- ✅ Full conversation playback
- ✅ Professional playback controls
- ✅ Transcript review

Start a conversation and see it in action!

---

Generated: 2025-01-05
Status: Ready to Use ✅

