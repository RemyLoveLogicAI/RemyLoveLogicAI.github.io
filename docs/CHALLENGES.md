# Challenges: The Ghost and the Grinds

## 1. Infrastructure "Ghosts"
Unidentified agent loops in the OpenClaw bridge are mirroring logs to iMessage. Strategy: Isolate the 5-min cron alert and terminate the mirrored session.

## 2. API Quota Limitations
OpenAI Realtime quota resets are breaking the live voice bridge. Pivot: Deep-dive into Groq + Deepgram + ElevenLabs for high-performance, cost-effective inference.

## 3. High Compute Load
Mac Mini M4 is redlining (Load 100+). Strategy: Offload heavy video-normalization to the NaughtyOS worker-pool.
