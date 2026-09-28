"""Material Embedding Database Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class MaterialEmbedding(Base):
    __tablename__ = "material_embeddings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Embedding vector stored as JSON array of floats (compatible with pgvector and SQLite)
    embedding = Column(JSON, nullable=False)
    model_name = Column(String(100), default="all-MiniLM-L6-v2", nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    material = relationship("Material", back_populates="embedding")
