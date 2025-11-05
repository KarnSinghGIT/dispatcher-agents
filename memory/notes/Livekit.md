# Welcome to LiveKit

> Learn to build voice, video, and multimodal AI applications on the world's best open source realtime platform.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Build your first voice AI agent in less than 10 minutes.

- **[Intro to LiveKit](https://docs.livekit.io/home/get-started/intro-to-livekit.md)**: An overview of the LiveKit ecosystem and advantages.

- **[AI Agents](https://docs.livekit.io/agents.md)**: The LiveKit framework for building realtime multimodal AI agents.

- **[Telephony](https://docs.livekit.io/sip.md)**: LiveKit SIP integration for telephony applications.

- **[SDK Quickstarts](https://docs.livekit.io/home/quickstarts.md)**: Explore our collection of platform quickstarts to get up and running fast.

- **[LiveKit Cloud](https://docs.livekit.io/home/cloud.md)**: The fully-managed, globally distributed LiveKit deployment option.

- **[Recipes](https://docs.livekit.io/recipes.md)**: A comprehensive collection of LiveKit examples, guides, and demos.

---
LiveKit docs › Getting started › Introduction

---

# LiveKit Agents

> Realtime framework for production-grade multimodal and voice AI agents.

## Introduction

The Agents framework allows you to add a Python or Node.js program to any LiveKit room as a full realtime participant. It's primarily an SDK that includes a complete set of tools and abstractions that make it easy to feed realtime media and data through an AI pipeline that works with any provider, and to publish realtime results back to the room.

While the framework excels at AI-powered voice agents, it's designed to support any type of programmatic participant. You can deploy custom logic that processes realtime audio, video, and data streams, making it suitable for a wide range of applications beyond traditional AI agents. To learn more about this use case, see [Worker lifecycle](https://docs.livekit.io/agents/worker.md).

You can deploy your agents to [LiveKit Cloud](https://docs.livekit.io/agents/ops/deployment.md) or any other [custom environment](https://docs.livekit.io/agents/ops/deployment/custom.md) of your choice.

If you want to get your hands on the code for building an agent right away, follow the Voice AI quickstart guide. It takes just a few minutes to build your first voice agent.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Build and deploy a simple voice assistant with Python or Node.js in less than 10 minutes.

- **[Deeplearning.ai course](https://www.deeplearning.ai/short-courses/building-ai-voice-agents-for-production/)**: Learn to build and deploy voice agents with LiveKit in this free course from Deeplearning.ai.

- **[Deploying to LiveKit Cloud](https://docs.livekit.io/agents/ops/deployment.md)**: Run your agent on LiveKit Cloud's global infrastructure.

- **[GitHub repository](https://github.com/livekit/agents)**: Python source code and examples for the LiveKit Agents SDK.

- **[SDK reference](https://docs.livekit.io/reference/python/v1/livekit/agents/index.html.md)**: Python reference docs for the LiveKit Agents SDK.

## Use cases

Some applications for agents include:

- **Multimodal assistant**: Talk, text, or screen share with an AI assistant.
- **Telehealth**: Bring AI into realtime telemedicine consultations, with or without humans in the loop.
- **Call center**: Deploy AI to the front lines of customer service with inbound and outbound call support.
- **Realtime translation**: Translate conversations in realtime.
- **NPCs**: Add lifelike NPCs backed by language models instead of static scripts.
- **Robotics**: Put your robot's brain in the cloud, giving it access to the most powerful models.

The following [recipes](https://docs.livekit.io/recipes.md) demonstrate some of these use cases:

- **[Medical Office Triage](https://github.com/livekit-examples/python-agents-examples/tree/main/complex-agents/medical_office_triage)**: Agent that triages patients based on symptoms and medical history.

- **[Restaurant Agent](https://github.com/livekit/agents/blob/main/examples/voice_agents/restaurant_agent.py)**: A restaurant front-of-house agent that can take orders, add items to a shared cart, and checkout.

- **[Company Directory](https://docs.livekit.io/recipes/company-directory.md)**: Build a AI company directory agent. The agent can respond to DTMF tones and voice prompts, then redirect callers.

- **[Pipeline Translator](https://github.com/livekit-examples/python-agents-examples/tree/main/translators/pipeline_translator.py)**: Implement translation in the processing pipeline.

## Framework overview

![Diagram showing framework overview.](/images/agents/framework-overview.svg)

Your agent code operates as a stateful, realtime bridge between powerful AI models and your users. While AI models typically run in data centers with reliable connectivity, users often connect from mobile networks with varying quality.

WebRTC ensures smooth communication between agents and users, even over unstable connections. LiveKit WebRTC is used between the frontend and the agent, while the agent communicates with your backend using HTTP and WebSockets. This setup provides the benefits of WebRTC without its typical complexity.

The agents SDK includes components for handling the core challenges of realtime voice AI, such as streaming audio through an STT-LLM-TTS pipeline, reliable turn detection, handling interruptions, and LLM orchestration. It supports plugins for most major AI providers, with more continually added. The framework is fully open source and supported by an active community.

Other framework features include:

- **Voice, video, and text**: Build agents that can process realtime input and produce output in any modality.
- **Tool use**: Define tools that are compatible with any LLM, and even forward tool calls to your frontend.
- **Multi-agent handoff**: Break down complex workflows into simpler tasks.
- **Extensive integrations**: Integrate with nearly every AI provider there is for LLMs, STT, TTS, and more.
- **State-of-the-art turn detection**: Use the custom turn detection model for lifelike conversation flow.
- **Made for developers**: Build your agents in code, not configuration.
- **Production ready**: Includes built-in worker orchestration, load balancing, and Kubernetes compatibility.
- **Open source**: The framework and entire LiveKit ecosystem are open source under the Apache 2.0 license.

## How agents connect to LiveKit

![Diagram showing a high-level view of how agents work.](/images/agents/agents-jobs-overview.svg)

When your agent code starts, it first registers with a LiveKit server (either [self hosted](https://docs.livekit.io/home/self-hosting/deployment.md) or [LiveKit Cloud](https://cloud.livekit.io)) to run as a "worker" process. The worker waits until it receives a dispatch request. To fulfill this request, the worker boots a "job" subprocess which joins the room. By default, your workers are dispatched to each new room created in your LiveKit Cloud project (or self-hosted server). To learn more about workers, see the [Worker lifecycle](https://docs.livekit.io/agents/worker.md) guide.

After your agent and user join a room, the agent and your frontend app can communicate using LiveKit WebRTC. This enables reliable and fast realtime communication in any network conditions. LiveKit also includes full support for telephony, so the user can join the call from a phone instead of a frontend app.

To learn more about how LiveKit works overall, see the [Intro to LiveKit](https://docs.livekit.io/home/get-started/intro-to-livekit.md) guide.

## Getting started

Follow these guides to learn more and get started with LiveKit Agents.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Build a simple voice assistant with Python or Node.js in less than 10 minutes.

- **[Recipes](https://docs.livekit.io/recipes.md)**: A comprehensive collection of examples, guides, and recipes for LiveKit Agents.

- **[Intro to LiveKit](https://docs.livekit.io/home/get-started/intro-to-livekit.md)**: An overview of the LiveKit ecosystem.

- **[Web and mobile frontends](https://docs.livekit.io/agents/start/frontend.md)**: Put your agent in your pocket with a custom web or mobile app.

- **[Telephony integration](https://docs.livekit.io/agents/start/telephony.md)**: Your agent can place and receive calls with LiveKit's SIP integration.

- **[Building voice agents](https://docs.livekit.io/agents/build.md)**: Comprehensive documentation to build advanced voice AI apps with LiveKit.

- **[Worker lifecycle](https://docs.livekit.io/agents/worker.md)**: Learn how to manage your agents with workers and jobs.

- **[Deploying to production](https://docs.livekit.io/agents/ops/deployment.md)**: Guide to deploying your voice agent in a production environment.

- **[AI models](https://docs.livekit.io/agents/models.md)**: Explore the full list of AI models available for LiveKit Agents.

---

This document was rendered at 2025-11-05T14:59:45.331Z.
For the latest version of this document, see [https://docs.livekit.io/agents.md](https://docs.livekit.io/agents.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt)..

LiveKit docs › Partner spotlight › OpenAI › Realtime API Plugin

---

# OpenAI Realtime API plugin guide

> How to use the OpenAI Realtime API with LiveKit Agents.

Available in:
- [x] Node.js
- [x] Python

- **[OpenAI Playground](https://playground.livekit.io/)**: Experiment with OpenAI's Realtime API in the playground with personalities like the **Snarky Teenager** or **Opera Singer**.

## Overview

OpenAI's Realtime API enables low-latency, multimodal interactions with realtime text, audio image, and video features. Use LiveKit's OpenAI plugin to create an agent that uses the Realtime API.

> ℹ️ **Note**
> 
> Using Azure OpenAI? See our [Azure OpenAI Realtime API guide](https://docs.livekit.io/agents/models/realtime/plugins/azure-openai.md).

## Quick reference

This section includes a basic usage example and some reference material. For links to more detailed documentation, see [Additional resources](#additional-resources).

### Installation

Install the OpenAI plugin:

**Python**:

```shell
uv add "livekit-agents[openai]~=1.2"

```

---

**Node.js**:

```shell
pnpm add "@livekit/agents-plugin-openai@1.x"

```

### Authentication

The OpenAI plugin requires an [OpenAI API key](https://platform.openai.com/api-keys).

Set `OPENAI_API_KEY` in your `.env` file.

### Usage

Use the OpenAI Realtime API within an `AgentSession`. For example, you can use it in the [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md).

**Python**:

```python
from livekit.plugins import openai

session = AgentSession(
    llm=openai.realtime.RealtimeModel(voice="marin"),
)

```

---

**Node.js**:

```typescript
import * as openai from '@livekit/agents-plugin-openai';

const session = new voice.AgentSession({
   llm: new openai.realtime.RealtimeModel({ voice: "marin" }),
});

```

### Parameters

This section describes some of the available parameters. For a complete reference of all available parameters, see the plugin reference links in the [Additional resources](#additional-resources) section.

- **`model`** _(str)_ (optional) - Default: `'gpt-realtime'`: ID of the Realtime model to use. For a list of available models, see the [Models](https://platform.openai.com/docs/models).

- **`voice`** _(str)_ (optional) - Default: `'alloy'`: Voice to use for speech generation. For a list of available voices, see [Voice options](https://platform.openai.com/docs/guides/realtime-conversations#voice-options).

- **`temperature`** _(float)_ (optional) - Default: `0.8`: Valid values are between `0.6` and `1.2`. To learn more, see [temperature](https://platform.openai.com/docs/api-reference/realtime-sessions/create#realtime-sessions-create-temperature).

- **`turn_detection`** _(TurnDetection | None)_ (optional): Configuration for turn detection, see the section on [Turn detection](#turn-detection) for more information.

- **`modalities`** _(list[str])_ (optional) - Default: `['text', 'audio']`: List of response modalities to use for the session. Set to `['text']` to use the model in text-only mode with a [separate TTS plugin](https://docs.livekit.io/llms.txt#separate-tts).

## Turn detection

OpenAI's Realtime API includes [voice activity detection (VAD)](https://platform.openai.com/docs/guides/realtime-vad) to automatically detect when a user has started or stopped speaking. This feature is enabled by default.

There are two modes for VAD:

- **Server VAD** (default): Uses periods of silence to automatically chunk the audio.
- **Semantic VAD**: Uses a semantic classifier to detect when the user has finished speaking based on their words.

### Server VAD

Server VAD is the default mode and can be configured with the following properties:

**Python**:

```python
from livekit.plugins.openai import realtime
from openai.types.beta.realtime.session import TurnDetection

session = AgentSession(
    llm=realtime.RealtimeModel(
        turn_detection=TurnDetection(
            type="server_vad",
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=500,
            create_response=True,
            interrupt_response=True,
        )
    ),
)

```

---

**Node.js**:

```typescript
import * as openai from '@livekit/agents-plugin-openai';

const session = new voice.AgentSession({
   llm: new openai.realtime.RealtimeModel({
      turnDetection: {
         type: "server_vad",
         threshold: 0.5,
         prefix_padding_ms: 300,
         silence_duration_ms: 500,
         create_response: true,
         interrupt_response: true,
      },
   }),
});

```

- `threshold`: Higher values require louder audio to activate, better for noisy environments.
- `prefix_padding_ms`: Amount of audio to include before detected speech.
- `silence_duration_ms`: Duration of silence to detect speech stop (shorter = faster turn detection).

### Semantic VAD

Semantic VAD uses a classifier to determine when the user is done speaking based on their words. This mode is less likely to interrupt users mid-sentence or chunk transcripts prematurely.

**Python**:

```python
from livekit.plugins.openai import realtime
from openai.types.beta.realtime.session import TurnDetection

session = AgentSession(
    llm=realtime.RealtimeModel(
        turn_detection=TurnDetection(
            type="semantic_vad",
            eagerness="auto",
            create_response=True,
            interrupt_response=True,
        )
    ),
)

```

---

**Node.js**:

```typescript
import * as openai from '@livekit/agents-plugin-openai';

const session = new voice.AgentSession({
   llm: new openai.realtime.RealtimeModel({
      turnDetection: null,
   })
   turnDetection: new livekit.turnDetector.EnglishModel(),
});

```

The `eagerness` property controls how quickly the model responds:

- `auto` (default) - Equivalent to `medium`.
- `low` - Lets users take their time speaking.
- `high` - Chunks audio as soon as possible.
- `medium` - Balanced approach.

For more information about turn detection in general, see the [Turn detection guide](https://docs.livekit.io/agents/build/turns.md).

## Usage with separate TTS

To use the OpenAI Realtime API with a different [TTS instance](https://docs.livekit.io/agents/models/tts.md), configure it with a text-only response modality and include a TTS instance in your `AgentSession` configuration. This configuration allows you to gain the benefits of realtime speech comprehension while maintaining complete control over the speech output.

**Python**:

```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel(modalities=["text"]),
    tts="cartesia/sonic-3" # Or other TTS instance of your choice
)

```

---

**Node.js**:

```typescript
import * as openai from '@livekit/agents-plugin-openai';

const session = new voice.AgentSession({
   llm: new openai.realtime.RealtimeModel({ 
      modalities: ["text"]
   }),
   tts: "cartesia/sonic-3", // Or other TTS instance of your choice
});

```

## Loading conversation history

If you load conversation history into the model, it might respond with text output even if configured for audio response. To work around this issue, use the model [with a separate TTS instance](#separate-tts) and text-only response modality. You can use the [Azure OpenAI TTS plugin](https://docs.livekit.io/agents/models/tts/plugins/azure-openai.md) to continue using the same voices supported by the Realtime API.

For additional workaround options, see the OpenAI [thread](https://community.openai.com/t/trouble-loading-previous-messages-with-realtime-api) on this topic.

## Additional resources

The following resources provide more information about using OpenAI with LiveKit Agents.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Build a simple realtime model voice assistant using the OpenAI Realtime API in less than 10 minutes.

- **[OpenAI docs](https://platform.openai.com/docs/guides/realtime)**: OpenAI Realtime API documentation.

- **[OpenAI ecosystem overview](https://docs.livekit.io/agents/integrations/openai.md)**: Overview of the entire OpenAI and LiveKit Agents integration.

---

This document was rendered at 2025-11-05T15:54:51.230Z.
For the latest version of this document, see [https://docs.livekit.io/agents/models/realtime/plugins/openai.md](https://docs.livekit.io/agents/models/realtime/plugins/openai.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).