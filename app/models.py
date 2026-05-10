import json
import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
from app.database import engine

Base = declarative_base()


class World(Base):
    __tablename__ = "worlds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    theme = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    rules = Column(Text, default="")
    history = Column(Text, default="")
    current_scene = Column(String(200), default="")
    scene_description = Column(Text, default="")
    plot_stage = Column(String(50), default="intro")
    plot_context = Column(Text, default="")
    novel_text = Column(Text, default="")
    novel_chapter_count = Column(Integer, default=0)
    mode = Column(String(20), default="normal")
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    characters = relationship("Character", back_populates="world", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="world", cascade="all, delete-orphan")
    plot_events = relationship("PlotEvent", back_populates="world", cascade="all, delete-orphan")
    novel_chapters = relationship("NovelChapter", back_populates="world", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id, "theme": self.theme, "name": self.name,
            "description": self.description, "rules": self.rules,
            "history": self.history, "current_scene": self.current_scene,
            "scene_description": self.scene_description,
            "plot_stage": self.plot_stage, "mode": self.mode,
            "created_at": str(self.created_at)
        }


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(100), nullable=False)
    role_type = Column(String(20), default="npc")  # "player" / "npc"
    personality = Column(Text, default="")
    background = Column(Text, default="")
    goals = Column(Text, default="")
    relationships = Column(Text, default="{}")
    appearance = Column(Text, default="")
    speaking_style = Column(Text, default="")
    memory_summary = Column(Text, default="")
    stats = Column(JSON, default=dict)
    is_alive = Column(Integer, default=1)
    is_present = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    world = relationship("World", back_populates="characters")
    memory_entries = relationship("MemoryEntry", back_populates="character", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "role_type": self.role_type,
            "personality": self.personality, "background": self.background,
            "goals": self.goals, "appearance": self.appearance,
            "speaking_style": self.speaking_style, "stats": self.stats,
            "is_alive": self.is_alive, "is_present": self.is_present
        }

    def memory_to_prompt(self, limit=15):
        from app.database import Session
        session = Session()
        entries = session.query(MemoryEntry).filter(
            MemoryEntry.character_id == self.id
        ).order_by(MemoryEntry.id.desc()).limit(limit).all()
        if not entries:
            return ""
        lines = []
        for e in reversed(entries):
            lines.append(f"[{e.event_type}] {e.content}")
        return "\n".join(lines)


class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    event_type = Column(String(30), default="dialogue")  # dialogue / plot / scene / stat_change
    content = Column(Text, default="")
    importance = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    character = relationship("Character", back_populates="memory_entries")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    round_num = Column(Integer, default=0)
    speaker_name = Column(String(100), nullable=False)
    speaker_type = Column(String(20), default="npc")  # player / npc / narrator / system
    content = Column(Text, nullable=False)
    action = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    world = relationship("World", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id, "round_num": self.round_num,
            "speaker_name": self.speaker_name,
            "speaker_type": self.speaker_type,
            "content": self.content, "action": self.action,
            "created_at": str(self.created_at)
        }


class PlotEvent(Base):
    __tablename__ = "plot_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    event_type = Column(String(30), default="plot_twist")
    title = Column(String(200), default="")
    description = Column(Text, default="")
    changes = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    world = relationship("World", back_populates="plot_events")

    def to_dict(self):
        return {
            "id": self.id, "event_type": self.event_type,
            "title": self.title, "description": self.description,
            "changes": self.changes, "created_at": str(self.created_at)
        }


class NovelChapter(Base):
    __tablename__ = "novel_chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    chapter_num = Column(Integer, default=0)
    title = Column(String(200), default="")
    content = Column(Text, default="")
    summary = Column(Text, default="")
    trigger_reason = Column(String(100), default="")
    is_final = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    world = relationship("World", back_populates="novel_chapters")

    def to_dict(self):
        return {
            "id": self.id, "chapter_num": self.chapter_num,
            "title": self.title, "content": self.content,
            "summary": self.summary, "trigger_reason": self.trigger_reason,
            "is_final": self.is_final, "created_at": str(self.created_at)
        }
