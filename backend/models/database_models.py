"""
Database Models for AutoVid
PostgreSQL ORM models using SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, TimeDelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()


class Project(Base):
    """Video generation project container"""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    config = Column(JSON)  # Resolution, duration, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow())
    
    scenes = relationship("Scene", back_populates="project")
    output_video = relationship("OutputVideo", back_populates="project")


class Scene(Base):
    """Individual scene from prompt decomposition"""
    
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Decomposition fields
    description = Column(Text, nullable=False)
    mood_tone = Column(String(100))
    keywords = Column(JSON, default=list)
    scene_order = Column(Integer)
    
    # Downloaded media
    source = Column(String(50))  # pexels, pixabay
    video_path = Column(String(500), nullable=True)
    downloaded_at = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(JSON)
    
    # Processing status
    status = Column(String(20), default="pending")  # pending, downloaded, failed
    
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow())
    
    project = relationship("Project", back_populates="scenes")


class VoiceSegment(Base):
    """Voice segment for each scene"""
    
    __tablename__ = "voice_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)  # Nullable for voiceover only
    
    text = Column(Text, nullable=False)
    audio_path = Column(String(500), nullable=True)
    audio_duration = Column(Float)
    
    # Voice settings
    tts_provider = Column(String(50))  # coqui, edge-tts
    voice_id = Column(String(100))
    
    status = Column(String(20), default="pending")  # pending, synthesized, failed
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow())


class OutputVideo(Base):
    """Final output video"""
    
    __tablename__ = "output_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    
    file_path = Column(String(500), nullable=False)
    duration = Column(Float)
    resolution = Column(JSON)
    file_size = Column(Integer)  # in bytes
    
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    metadata = Column(JSON)  # Export settings, codec, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow())


class TaskLog(Base):
    """Processing logs for debugging"""
    
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=datetime.utcnow())
    level = Column(String(20), default="info")  # info, warning, error
    message = Column(Text, nullable=False)
    details = Column(JSON)
