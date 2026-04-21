from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────

class AgentCreate(BaseModel):
    name: str
    role: str
    system_prompt: str

class TaskCreate(BaseModel):
    agent_id: int
    instruction: str

class ChatMessage(BaseModel):
    message: str
    agent_id: Optional[int] = None

# ── AI call helper ────────────────────────────────────────────────

def call_ai(system_prompt: str, messages: list) -> str:
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}] + messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI unavailable: {str(e)}"

# ── Routes ────────────────────────────────────────────────────────

@router.post("/agents")
def create_agent(data: AgentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.ai_agents.models import Agent
    agent = Agent(**data.model_dump(), user_id=user.id)
    db.add(agent); db.commit(); db.refresh(agent)
    return agent

@router.get("/agents")
def list_agents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.ai_agents.models import Agent
    return db.query(Agent).filter(Agent.user_id == user.id).all()

@router.post("/tasks")
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.ai_agents.models import AgentTask, Agent
    agent = db.query(Agent).filter(Agent.id == data.agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")

    # Run the task through AI
    result = call_ai(agent.system_prompt, [{"role": "user", "content": data.instruction}])

    task = AgentTask(
        agent_id=data.agent_id,
        instruction=data.instruction,
        result=result,
        status="done",
        completed_at=datetime.utcnow()
    )
    db.add(task); db.commit(); db.refresh(task)
    return task

@router.post("/chat")
def chat(data: ChatMessage, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.ai_agents.models import Conversation, Agent

    # Get chat history for context
    history = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).order_by(Conversation.created_at).limit(10).all()

    messages = [{"role": h.role, "content": h.content} for h in history]
    messages.append({"role": "user", "content": data.message})

    # Get agent system prompt if agent specified
    system_prompt = "You are a helpful assistant."
    if data.agent_id:
        agent = db.query(Agent).filter(Agent.id == data.agent_id).first()
        if agent:
            system_prompt = agent.system_prompt

    # Save user message
    user_msg = Conversation(user_id=user.id, role="user", content=data.message, agent_id=data.agent_id)
    db.add(user_msg)

    # Get AI reply
    reply = call_ai(system_prompt, messages)

    # Save assistant reply
    ai_msg = Conversation(user_id=user.id, role="assistant", content=reply, agent_id=data.agent_id)
    db.add(ai_msg)
    db.commit()

    return {"reply": reply, "agent_id": data.agent_id}

@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.ai_agents.models import Conversation
    return db.query(Conversation).filter(Conversation.user_id == user.id).all()
