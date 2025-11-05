# Use Cases

## Primary Use Cases

### 1. Voice Agent Conversation Generation
**Description:** Generate realistic audio conversations between two AI agents (dispatcher and driver) based on scenario descriptions and agent prompts.

**Key Actors:**
- User (Dispatcher/Dispatch Co employee)
- Dispatcher Agent (AI)
- Driver Agent (AI)

**Flow:**
1. User inputs scenario description (load details, driver information)
2. User configures dispatcher agent prompt
3. User configures driver agent prompt
4. User optionally adds acting notes for agents
5. System generates conversation transcript
6. System generates audio file from conversation
7. User plays back the generated conversation

**Inputs:**
- Scenario description (load parameters, driver context)
- Dispatcher agent prompt
- Driver agent prompt
- Acting notes (optional)

**Outputs:**
- Conversation transcript
- Audio file (.wav or .mp3)

### 2. Load Assignment Simulation
**Description:** Simulate realistic dispatcher-driver phone conversations for load assignments with specific parameters.

**Key Load Parameters:**
- Load ID
- Pickup location and time
- Delivery location and deadline
- Load type (HVAC units, etc.)
- Weight (42,000 lbs)
- Trailer type (dry-van)
- Rate ($/mile and total)
- Accessorials
- Securement requirements
- TMS update requirements (Macro-1)

**Conversation Elements:**
- Greeting and context
- Load details discussion
- Pickup window negotiation
- Rate discussion
- Load type and requirements
- Confirmation and logistics
- Closing

### 3. Agent Configuration Management
**Description:** Configure and manage AI agent personalities, prompts, and behavior.

**Capabilities:**
- Set dispatcher agent personality and communication style
- Set driver agent personality and communication style
- Add acting notes to guide agent behavior
- Test agent configurations with sample scenarios

## Typical User Journeys

### Journey 1: Generate a Load Assignment Conversation
1. **User opens application**
   - Sees input form with scenario fields
   - Sees agent configuration sections

2. **User enters scenario details**
   - Fills in load ID (e.g., HDX-2478)
   - Enters pickup location and time (Dallas TX, 8 AM)
   - Enters delivery location and deadline (Atlanta GA, before noon next day)
   - Enters load details (HVAC units, 42,000 lbs, dry-van)
   - Enters rate information ($2.10/mi, $1,680 total)
   - Enters special requirements (two-strap securement, Macro-1 update)

3. **User configures dispatcher agent**
   - Enters dispatcher prompt (e.g., "You are Tim, dispatcher at Dispatch Co...")
   - Optionally adds acting notes

4. **User configures driver agent**
   - Enters driver prompt (e.g., "You are Chris, a driver...")
   - Optionally adds acting notes

5. **User clicks Generate button**
   - System validates inputs
   - System generates conversation transcript using AI agents
   - System converts transcript to audio using TTS
   - System displays conversation transcript
   - System provides audio player

6. **User reviews conversation**
   - Reads transcript to verify accuracy
   - Plays audio to hear conversation quality
   - Optionally regenerates if needed

### Journey 2: Experiment with Different Agent Personalities
1. User opens application
2. User selects a saved scenario template
3. User modifies dispatcher prompt to change personality (e.g., more formal vs casual)
4. User modifies driver prompt to change response style
5. User generates conversation
6. User compares with previous conversation
7. User saves preferred configuration

### Journey 3: Batch Conversation Generation
1. User prepares multiple scenarios (CSV or JSON)
2. User sets default agent prompts
3. User uploads scenarios
4. System generates multiple conversations
5. User downloads all audio files and transcripts

