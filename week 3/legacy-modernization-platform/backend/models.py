import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LegacySystem(Base):
    __tablename__ = "legacy_systems"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"sys-{uuid.uuid4().hex[:8]}"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    model_elements = relationship(
        "ModelElementIndex", back_populates="system", cascade="all, delete-orphan"
    )
    artifact_versions = relationship(
        "ArtifactVersion", back_populates="system", cascade="all, delete-orphan"
    )
    jobs = relationship("Job", back_populates="system", cascade="all, delete-orphan")
    evidence_sources = relationship(
        "EvidenceSource", back_populates="system", cascade="all, delete-orphan"
    )


class ModelElementIndex(Base):
    __tablename__ = "model_element_index"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    system_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("legacy_systems.id", ondelete="CASCADE"), nullable=False
    )
    layer: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # motivation, strategy, business, application, technology
    archimate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    git_path: Mapped[str] = mapped_column(String(255), nullable=False)
    current_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    system = relationship("LegacySystem", back_populates="model_elements")


class ArtifactVersion(Base):
    __tablename__ = "artifact_versions"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"ver-{uuid.uuid4().hex[:8]}"
    )
    system_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("legacy_systems.id", ondelete="CASCADE"), nullable=False
    )
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    phase: Mapped[str] = mapped_column(String(20), nullable=False, default="as-is")
    tag: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. as-is/v1
    author_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # agent | human
    run_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # Join key to LangSmith trace
    approval_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending | approved | rejected
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    system = relationship("LegacySystem", back_populates="artifact_versions")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"job-{uuid.uuid4().hex[:8]}"
    )
    system_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("legacy_systems.id", ondelete="CASCADE"), nullable=False
    )
    phase: Mapped[str] = mapped_column(String(20), nullable=False, default="as-is")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="queued"
    )  # queued | running | succeeded | failed
    run_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    system = relationship("LegacySystem", back_populates="jobs")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"src-{uuid.uuid4().hex[:8]}"
    )
    system_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("legacy_systems.id", ondelete="CASCADE"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # code, iac, doc, transcript
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    system = relationship("LegacySystem", back_populates="evidence_sources")
