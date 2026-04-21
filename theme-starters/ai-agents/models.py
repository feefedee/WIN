from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    name         = Column(String)
    role         = Column(String)        # e.g. "scheduler", "caller", "researcher"
    system_prompt= Column(Text)          # defines agent behaviour
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    tasks        = relationship("AgentTask", back_populates="agent")


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id           = Column(Integer, primary_key=True, index=True)
    agent_id     = Column(Integer, ForeignKey("agents.id"))
    instruction  = Column(Text)          # natural language instruction
    result       = Column(Text, nullable=True)
    status       = Column(String, default="pending")  # pending, running, done, failed
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    agent        = relationship("Agent", back_populates="tasks")


class Conversation(Base):
    __tablename__ = "conversations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    role       = Column(String)      # "user" or "assistant"
    content    = Column(Text)
    agent_id   = Column(Integer, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
