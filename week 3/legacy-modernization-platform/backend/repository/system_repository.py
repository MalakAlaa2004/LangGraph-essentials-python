from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import (
    ArtifactVersion,
    EvidenceSource,
    Job,
    LegacySystem,
    ModelElementIndex,
)

# ==========================================
# Legacy Systems Repository
# ==========================================


def create_legacy_system(
    db: Session, name: str, description: Optional[str] = None
) -> LegacySystem:
    system = LegacySystem(name=name, description=description)
    db.add(system)
    db.commit()
    db.refresh(system)
    return system


def get_legacy_system(db: Session, system_id: str) -> Optional[LegacySystem]:
    return db.scalar(select(LegacySystem).where(LegacySystem.id == system_id))


def list_legacy_systems(db: Session) -> List[LegacySystem]:
    return list(db.scalars(select(LegacySystem)).all())


# ==========================================
# Model Element Index Repository
# ==========================================


def upsert_model_element_index(
    db: Session,
    element_id: str,
    system_id: str,
    layer: str,
    archimate_type: str,
    name: str,
    git_path: str,
    current_commit: str,
) -> ModelElementIndex:
    """Idempotently insert or update a model element index record."""
    element = db.scalar(
        select(ModelElementIndex).where(ModelElementIndex.id == element_id)
    )
    if element:
        element.system_id = system_id
        element.layer = layer
        element.archimate_type = archimate_type
        element.name = name
        element.git_path = git_path
        element.current_commit = current_commit
        element.updated_at = datetime.utcnow()
    else:
        element = ModelElementIndex(
            id=element_id,
            system_id=system_id,
            layer=layer,
            archimate_type=archimate_type,
            name=name,
            git_path=git_path,
            current_commit=current_commit,
        )
        db.add(element)
    db.commit()
    db.refresh(element)
    return element


def get_model_element_index(
    db: Session, element_id: str
) -> Optional[ModelElementIndex]:
    return db.scalar(
        select(ModelElementIndex).where(ModelElementIndex.id == element_id)
    )


def list_model_elements(
    db: Session, system_id: str, layer: Optional[str] = None
) -> List[ModelElementIndex]:
    stmt = select(ModelElementIndex).where(ModelElementIndex.system_id == system_id)
    if layer:
        stmt = stmt.where(ModelElementIndex.layer == layer)
    return list(db.scalars(stmt).all())


# ==========================================
# Artifact Versions Repository
# ==========================================


def create_artifact_version(
    db: Session,
    system_id: str,
    commit_sha: str,
    tag: str,
    author_type: str,
    phase: str = "as-is",
    run_id: Optional[str] = None,
    approval_status: str = "pending",
) -> ArtifactVersion:
    version = ArtifactVersion(
        system_id=system_id,
        commit_sha=commit_sha,
        tag=tag,
        author_type=author_type,
        phase=phase,
        run_id=run_id,
        approval_status=approval_status,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def update_artifact_version_status(
    db: Session,
    version_id: str,
    approval_status: str,
    approved_by: Optional[str] = None,
) -> Optional[ArtifactVersion]:
    version = db.scalar(select(ArtifactVersion).where(ArtifactVersion.id == version_id))
    if version:
        version.approval_status = approval_status
        if approved_by:
            version.approved_by = approved_by
        if approval_status in ["approved", "rejected"]:
            version.approved_at = datetime.utcnow()
        db.commit()
        db.refresh(version)
    return version


def list_artifact_versions(db: Session, system_id: str) -> List[ArtifactVersion]:
    return list(
        db.scalars(
            select(ArtifactVersion).where(ArtifactVersion.system_id == system_id)
        ).all()
    )


# ==========================================
# Jobs Repository (Idempotent Status Updates)
# ==========================================


def create_job(db: Session, system_id: str, phase: str = "as-is") -> Job:
    job = Job(
        system_id=system_id,
        phase=phase,
        status="queued",
        started_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job_status(
    db: Session,
    job_id: str,
    status: str,
    run_id: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Optional[Job]:
    """Idempotently update job execution status."""
    job = db.scalar(select(Job).where(Job.id == job_id))
    if job:
        job.status = status
        if run_id:
            job.run_id = run_id
        if error_message:
            job.error_message = error_message
        if status in ["succeeded", "failed"]:
            job.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> Optional[Job]:
    return db.scalar(select(Job).where(Job.id == job_id))


# ==========================================
# Evidence Sources Repository
# ==========================================


def create_evidence_source(
    db: Session,
    system_id: str,
    source_type: str,
    location: str,
    description: Optional[str] = None,
) -> EvidenceSource:
    source = EvidenceSource(
        system_id=system_id,
        source_type=source_type,
        location=location,
        description=description,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def list_evidence_sources(db: Session, system_id: str) -> List[EvidenceSource]:
    return list(
        db.scalars(
            select(EvidenceSource).where(EvidenceSource.system_id == system_id)
        ).all()
    )
