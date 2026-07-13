from datetime import datetime
from enum import StrEnum
from typing import Any

from backend.models.startup_profile import StartupProfile
from backend.models.validation_job import ValidationJob
from backend.models.validation_report import ValidationReport
from backend.teams.discovery_team import DiscoveryTeam
from backend.teams.validation_team import ValidationTeam
from backend.utils.exceptions import PipelineError
from backend.utils.logger import get_logger

logger = get_logger(__name__)

VALID_JOB_STATUSES = ["queued", "running", "completed", "failed", "cancelled"]

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "queued": {"running", "cancelled"},
    "running": {"completed", "failed", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}

STAGE_PROGRESS_MAP: dict[str, int] = {
    "Discovery": 10,
    "Planning": 20,
    "Research": 50,
    "Competition": 65,
    "Analysis": 80,
    "Reporting": 95,
    "Review": 100,
}

STAGE_ORDER = [
    "Discovery",
    "Planning",
    "Research",
    "Competition",
    "Analysis",
    "Reporting",
    "Review",
]


def _generate_job_id() -> str:
    import uuid

    return f"job_{uuid.uuid4().hex[:6]}"


class PipelineStage(StrEnum):
    DISCOVERY = "Discovery"
    PLANNING = "Planning"
    RESEARCH = "Research"
    COMPETITION = "Competition"
    ANALYSIS = "Analysis"
    REPORTING = "Reporting"
    REVIEW = "Review"
    COMPLETE = "Complete"


PIPELINE_STAGES = list(PipelineStage)


class ValidationPipeline:
    name = "Validation Pipeline"

    def __init__(
        self,
        discovery_team: DiscoveryTeam | None = None,
        validation_team: ValidationTeam | None = None,
    ) -> None:
        self._discovery_team = discovery_team or DiscoveryTeam()
        self._validation_team = validation_team or ValidationTeam()
        self._jobs: dict[str, ValidationJob] = {}
        logger.info("Validation Pipeline initialized")

    # ── Team Execution ─────────────────────────────────────────────────────

    async def run_discovery(self, founder_input: dict[str, Any]) -> StartupProfile:
        logger.info("Pipeline running Discovery Team")
        profile = await self._discovery_team.run_discovery(founder_input)
        logger.info(f"Discovery complete: {profile.startup_name}")
        return profile

    async def run_validation(
        self,
        startup_profile: StartupProfile,
    ) -> ValidationReport:
        logger.info(f"Pipeline running Validation Team for: {startup_profile.startup_name}")
        result = await self._validation_team.run_validation(startup_profile)
        logger.info("Validation complete")
        return result.validation_report

    async def run_full_validation(
        self,
        founder_input: dict[str, Any],
        mode: str = "deep",
    ) -> ValidationJob:
        logger.info("Pipeline running full validation")
        job = None
        try:
            profile = await self.run_discovery(founder_input)
            job = self.create_job(profile, mode=mode)
            self.start_job(job.job_id)
            report = await self.run_validation(profile)
            self.complete_job(job.job_id, report=report)
            logger.info(f"Full validation complete: {job.job_id} - {profile.startup_name}")
            return self._jobs[job.job_id]
        except Exception as e:
            error_msg = str(e)
            if job is not None:
                logger.exception(f"Full validation failed for job: {job.job_id}: {error_msg}")
                self.fail_job(job.job_id, error_message=error_msg)
                return self._jobs[job.job_id]
            logger.exception(f"Full validation failed before job creation: {error_msg}")
            raise

    # ── Job Lifecycle ──────────────────────────────────────────────────────

    def create_job(
        self,
        startup_profile: StartupProfile,
        mode: str = "deep",
    ) -> ValidationJob:
        if not startup_profile.startup_name:
            raise PipelineError("startup_profile must have a startup_name")

        job_id = _generate_job_id()
        remaining = list(STAGE_ORDER)
        job = ValidationJob(
            job_id=job_id,
            status="queued",
            mode=mode,
            startup_profile=startup_profile,
            progress=0,
            current_stage="Discovery",
            completed_stages=[],
            remaining_stages=remaining,
            created_at=datetime.utcnow(),
        )
        self._jobs[job_id] = job
        logger.info(f"Job created: {job_id} (mode={mode})")
        return job

    def get_job(self, job_id: str) -> ValidationJob | None:
        return self._jobs.get(job_id)

    def _validate_transition(self, current: str, new: str) -> None:
        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if new not in allowed:
            raise PipelineError(f"Invalid status transition: {current} -> {new}")

    def _update_stage(self, job_id: str, stage: str) -> None:
        job = self._get_job_or_raise(job_id)
        job.current_stage = stage
        job.progress = STAGE_PROGRESS_MAP.get(stage, job.progress)

        if stage in job.remaining_stages:
            job.remaining_stages.remove(stage)

        if stage not in job.completed_stages:
            job.completed_stages.append(stage)

        logger.info(f"Job {job_id} stage: {stage} ({job.progress}%)")

    def advance_stage(self, job_id: str) -> str:
        job = self._get_job_or_raise(job_id)
        if job.status != "running":
            raise PipelineError(f"Cannot advance stage for job in status: {job.status}")

        self._complete_current_stage(job)

        try:
            current_idx = STAGE_ORDER.index(job.current_stage)
        except ValueError:
            current_idx = -1

        next_idx = current_idx + 1
        if next_idx >= len(STAGE_ORDER):
            raise PipelineError(f"No more stages to advance from: {job.current_stage}")

        next_stage = STAGE_ORDER[next_idx]
        self._update_stage(job_id, next_stage)
        return next_stage

    def _complete_current_stage(self, job: ValidationJob) -> None:
        stage = job.current_stage
        if stage in STAGE_ORDER and stage not in job.completed_stages:
            job.progress = STAGE_PROGRESS_MAP.get(stage, job.progress)
            if stage in job.remaining_stages:
                job.remaining_stages.remove(stage)
            job.completed_stages.append(stage)
            logger.info(f"Job {job.job_id} stage completed: {stage}")

    def start_job(self, job_id: str) -> ValidationJob:
        job = self._get_job_or_raise(job_id)
        self._validate_transition(job.status, "running")

        job.status = "running"
        job.current_stage = "Discovery"
        job.progress = 0
        job.remaining_stages = list(STAGE_ORDER)
        job.completed_stages = []
        logger.info(f"Job started: {job_id}")
        return job

    def complete_job(
        self,
        job_id: str,
        report: ValidationReport | None = None,
    ) -> ValidationJob:
        job = self._get_job_or_raise(job_id)
        self._validate_transition(job.status, "completed")

        job.status = "completed"
        job.current_stage = "Complete"
        job.progress = 100
        job.report = report
        job.completed_at = datetime.utcnow()
        job.completed_stages = list(STAGE_ORDER)
        job.remaining_stages = []
        logger.info(f"Job completed: {job_id}")
        return job

    def fail_job(
        self,
        job_id: str,
        error_message: str,
    ) -> ValidationJob:
        job = self._get_job_or_raise(job_id)
        self._validate_transition(job.status, "failed")

        job.status = "failed"
        job.error_message = error_message
        job.completed_at = datetime.utcnow()
        logger.error(f"Job failed: {job_id} - {error_message}")
        return job

    def cancel_job(self, job_id: str) -> ValidationJob:
        job = self._get_job_or_raise(job_id)
        self._validate_transition(job.status, "cancelled")

        job.status = "cancelled"
        job.completed_at = datetime.utcnow()
        logger.info(f"Job cancelled: {job_id}")
        return job

    def _get_job_or_raise(self, job_id: str) -> ValidationJob:
        job = self._jobs.get(job_id)
        if job is None:
            raise PipelineError(f"Job not found: {job_id}")
        return job
