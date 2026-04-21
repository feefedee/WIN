# Theme: AI Agents / Open Innovation (Omnidimension Track)

## Likely problem statements
- Multi-agent task automation system
- Natural language interface for bookings / phone calls
- AI assistant with memory and context
- Orchestrated agents (planner → executor → reviewer)

## Your models (already built)
- Agent — name, role, system_prompt (defines personality/function)
- AgentTask — instruction, result, status
- Conversation — full chat history with context

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /ai/agents | Create a new agent with a role |
| GET  | /ai/agents | List your agents |
| POST | /ai/tasks | Give an agent a task → returns AI result |
| POST | /ai/chat | Chat with context + optional agent |
| GET  | /ai/chat/history | Full conversation history |

## Extra pip installs needed
```
pip install openai
```

## Add to .env
```
OPENAI_API_KEY=your_key_here
```

## Example agents to create at the hackathon
```json
{ "name": "Scheduler", "role": "scheduler",
  "system_prompt": "You book appointments and manage calendars. Extract date, time, and purpose from natural language." }

{ "name": "Researcher", "role": "researcher",
  "system_prompt": "You search and summarize information. Always cite your sources and be concise." }

{ "name": "Support Agent", "role": "support",
  "system_prompt": "You handle customer support. Be empathetic, solve problems, escalate when needed." }
```

## How to plug into main.py
```python
from theme_starters.ai_agents.routes import router as ai_router
app.include_router(ai_router, prefix="/ai", tags=["AI Agents"])
```
