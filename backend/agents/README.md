# LiveKit Voice Agents - Dispatcher & Driver

This directory contains two LiveKit voice agents built with the OpenAI Realtime API following the official LiveKit Agents Framework v1.2+ architecture.

## Architecture

Both agents are built using:
- **LiveKit Agents Framework v1.2+** with the `Agent` and `AgentSession` pattern
- **OpenAI Realtime API** (gpt-4o-realtime-preview-2024-12-17) for natural conversation
- **Silero VAD** for voice activity detection
- **Function tools** for extensible agent capabilities

## Agents

### 1. Dispatcher Agent (`dispatcher_agent.py`)

**Role**: Tim, a friendly dispatcher at Dispatch Co.

**Capabilities**:
- Initiates conversations with drivers
- Presents load opportunities
- Answers questions about loads
- Tracks load acceptance/rejection

**Function Tools**:
- `mark_load_accepted(load_id)` - Mark a load as accepted
- `mark_load_rejected(load_id, reason)` - Mark a load as rejected with reason
- `get_load_details(load_id)` - Fetch additional load information

**Voice**: Alloy (OpenAI voice)

### 2. Driver Agent (`driver_agent.py`)

**Role**: Chris, an experienced truck driver

**Capabilities**:
- Responds to dispatcher calls
- Asks relevant questions about loads
- Evaluates load opportunities
- Accepts or declines loads

**Function Tools**:
- `check_availability(date)` - Check driver's availability
- `calculate_distance(origin, destination)` - Calculate route distance
- `accept_load(load_id)` - Accept a load assignment

**Voice**: Echo (OpenAI voice)

## Setup

### Prerequisites

1. **Python 3.10+** installed
2. **LiveKit Server** running (local or cloud)
3. **OpenAI API Key** with access to Realtime API

### Installation

1. Install dependencies:
```bash
cd backend
pip install --upgrade 'livekit-agents[openai,silero]>=1.2.0'
```

Or install from pyproject.toml:
```bash
cd backend
pip install -e .
```

### Configuration

Create or update `backend/.env` with the following variables:

```env
# LiveKit Configuration
LIVEKIT_URL=ws://localhost:7880  # or your LiveKit Cloud URL
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

## Running the Agents

### Testing the Implementation

First, verify everything is set up correctly:

```bash
cd backend
python test_agents.py
```

You should see:
```
======================================================================
[SUCCESS] ALL TESTS PASSED!
======================================================================
```

### Starting the Agents

The agents can be run in two modes:

#### Development Mode

**Terminal 1 - Start Dispatcher Agent:**
```bash
cd backend
python agents/dispatcher_agent.py dev
```

**Terminal 2 - Start Driver Agent:**
```bash
cd backend
python agents/driver_agent.py dev
```

In development mode, the agents:
- Auto-reload on code changes
- Show detailed logs
- Connect to any LiveKit room created in your project

#### Production Mode

For production deployment:

```bash
# Start dispatcher agent
python agents/dispatcher_agent.py start

# Start driver agent  
python agents/driver_agent.py start
```

## Agent Behavior

### Conversation Flow

1. **Room Creation**: When a LiveKit room is created, both agents can be dispatched to join
2. **Connection**: Both agents connect and initialize their OpenAI Realtime sessions
3. **Initiation**: The dispatcher agent starts the conversation by greeting the driver
4. **Conversation**: Agents communicate naturally using voice with automatic turn-taking
5. **Function Calls**: Agents can call their function tools as needed during the conversation

### Example Conversation

```
Dispatcher (Tim): "Hey Chris, this is Tim from Dispatch Co. I've got a load 
                   opportunity for you."

Driver (Chris): "Hey Tim, what've you got?"

Dispatcher: "I have a load from Dallas to Atlanta. It's 42,000 pounds of 
            HVAC units. Pickup is at 8 AM tomorrow, live load. Needs to 
            be in Atlanta before noon the next day."

Driver: "What's the rate?"

Dispatcher: "We're offering $2.10 per mile, comes out to $1,680 total, all-in."

Driver: "That works for me. I can take it."

[Driver agent calls: accept_load("HDX-2478")]
[Dispatcher agent calls: mark_load_accepted("HDX-2478")]

Dispatcher: "Perfect! I've got you booked. Look for the pickup details on 
            your macro. Remember to use two-strap securement and send a 
            Macro-1 update when you're empty."
```

## Customization

### Modifying Agent Prompts

Edit the `instructions` parameter in the Agent `__init__` method:

```python
class DispatcherAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""Your custom prompt here..."""
        )
```

### Adding Function Tools

Add new function tools using the `@function_tool` decorator:

```python
@function_tool
async def your_custom_tool(self, param1: str, param2: int):
    """Description of what this tool does."""
    # Your implementation
    return "Result"
```

### Changing Voices

Modify the `voice` parameter in the `RealtimeModel`:

```python
llm=openai.realtime.RealtimeModel(
    model="gpt-4o-realtime-preview-2024-12-17",
    voice="shimmer",  # Options: alloy, echo, shimmer, fable, onyx, nova
    temperature=0.8,
)
```

### Adjusting VAD Settings

Configure Silero VAD sensitivity:

```python
vad=silero.VAD.load(
    min_speech_duration_ms=100,
    min_silence_duration_ms=500,
)
```

## Troubleshooting

### Common Issues

1. **"No module named 'livekit.agents.voice'"**
   - Solution: Upgrade to livekit-agents >= 1.2.0
   ```bash
   pip install --upgrade 'livekit-agents[openai,silero]>=1.2.0'
   ```

2. **"API key not found"**
   - Solution: Ensure OPENAI_API_KEY and LIVEKIT credentials are in `.env`

3. **Agents not connecting**
   - Solution: Verify LIVEKIT_URL is correct and server is running
   - Check firewall settings

4. **No audio/conversation not starting**
   - Solution: Check that both agents are in the same room
   - Verify OpenAI Realtime API access
   - Check audio device permissions

### Debug Logging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

### DispatcherAgent

```python
class DispatcherAgent(Agent):
    async def mark_load_accepted(load_id: str) -> str
    async def mark_load_rejected(load_id: str, reason: str = "") -> str
    async def get_load_details(load_id: str) -> str
```

### DriverAgent

```python
class DriverAgent(Agent):
    async def check_availability(date: str) -> str
    async def calculate_distance(origin: str, destination: str) -> str
    async def accept_load(load_id: str) -> str
```

## Production Deployment

For production deployment, consider:

1. **Use LiveKit Cloud** for managed infrastructure
2. **Set up monitoring** with OpenTelemetry metrics
3. **Configure auto-scaling** based on room demand
4. **Implement error handling** and retry logic
5. **Add conversation logging** for quality assurance
6. **Set up alerts** for agent failures

See [LiveKit Cloud Deployment Guide](https://docs.livekit.io/agents/ops/deployment/) for details.

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- [LiveKit Python SDK](https://docs.livekit.io/reference/python/)
- [Example Agents](https://github.com/livekit/agents/tree/main/examples)

## License

This implementation follows the LiveKit Agents framework patterns and is built for the Dispatcher-Agents project.

