import asyncio

from pydantic import BaseModel

from backend.agents.business_agent import BusinessAgent
from backend.agents.competition_agent import CompetitionAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.report_agent import ReportAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.reviewer_agent import ReviewerAgent
from backend.models.business_findings import BusinessFindings
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.models.research_result import ResearchResult
from backend.models.review_result import ReviewResult
from backend.models.startup_profile import StartupProfile
from backend.models.validation_plan import ValidationPlan
from backend.models.validation_report import ValidationReport
from backend.teams.base_team import StartupIQTeam
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationTeamResult(BaseModel):
    startup_profile: StartupProfile
    validation_plan: ValidationPlan
    research_result: ResearchResult
    competitor_analysis: CompetitorAnalysis
    business_findings: BusinessFindings
    validation_report: ValidationReport
    review_result: ReviewResult


def _format_context(*items: BaseModel) -> str:
    parts = []
    for item in items:
        parts.append(item.model_dump_json(indent=2))
    return "\n\n".join(parts)


class ValidationTeam(StartupIQTeam):
    name = "Validation Team"

    def __init__(
        self,
        planner_agent: PlannerAgent | None = None,
        research_agent: ResearchAgent | None = None,
        competition_agent: CompetitionAgent | None = None,
        business_agent: BusinessAgent | None = None,
        report_agent: ReportAgent | None = None,
        reviewer_agent: ReviewerAgent | None = None,
        instructions: list[str] | None = None,
        context: dict | None = None,
        markdown: bool = True,
        show_members_responses: bool = False,
    ) -> None:
        self._planner = planner_agent or PlannerAgent()
        self._researcher = research_agent or ResearchAgent()
        self._competitor = competition_agent or CompetitionAgent()
        self._analyst = business_agent or BusinessAgent()
        self._reporter = report_agent or ReportAgent()
        self._reviewer = reviewer_agent or ReviewerAgent()

        team_instructions = instructions or [
            "Transform a StartupProfile into a complete Validation Report.",
            "Plan the validation strategy first, then research.",
            "Execute research and competition analysis in parallel.",
            "Generate business insights from collected evidence.",
            "Produce a structured Validation Report with scorecard.",
            "Review the report for quality issues.",
        ]

        super().__init__(
            members=[
                self._planner,
                self._researcher,
                self._competitor,
                self._analyst,
                self._reporter,
                self._reviewer,
            ],
            instructions=team_instructions,
            context=context,
            markdown=markdown,
            show_members_responses=show_members_responses,
        )

    async def run_validation(
        self,
        startup_profile: StartupProfile,
    ) -> ValidationTeamResult:
        logger.info(f"Starting validation for startup: {startup_profile.startup_name}")

        raw_plan = await self._planner.run_structured(
            _format_context(startup_profile),
        )
        plan = (
            raw_plan
            if isinstance(raw_plan, ValidationPlan)
            else ValidationPlan.model_validate(raw_plan)
        )
        logger.info("Planner stage complete")

        research_task = self._researcher.run_structured(
            _format_context(startup_profile, plan),
        )
        competition_task = self._competitor.run_structured(
            _format_context(startup_profile),
        )
        research_raw, competition_raw = await asyncio.gather(
            research_task,
            competition_task,
        )
        research_result = (
            research_raw
            if isinstance(research_raw, ResearchResult)
            else ResearchResult.model_validate(research_raw)
        )
        competitor_analysis = (
            competition_raw
            if isinstance(competition_raw, CompetitorAnalysis)
            else CompetitorAnalysis.model_validate(competition_raw)
        )
        logger.info("Research and Competition stages complete")

        raw_business = await self._analyst.run_structured(
            _format_context(startup_profile, research_result, competitor_analysis),
        )
        business_findings = (
            raw_business
            if isinstance(raw_business, BusinessFindings)
            else BusinessFindings.model_validate(raw_business)
        )
        logger.info("Business Analysis stage complete")

        raw_report = await self._reporter.run_structured(
            _format_context(
                startup_profile,
                plan,
                research_result,
                competitor_analysis,
                business_findings,
            ),
        )
        validation_report = (
            raw_report
            if isinstance(raw_report, ValidationReport)
            else ValidationReport.model_validate(raw_report)
        )
        logger.info("Report stage complete")

        raw_review = await self._reviewer.run_structured(
            _format_context(validation_report),
        )
        review_result = (
            raw_review
            if isinstance(raw_review, ReviewResult)
            else ReviewResult.model_validate(raw_review)
        )
        logger.info("Review stage complete")

        return ValidationTeamResult(
            startup_profile=startup_profile,
            validation_plan=plan,
            research_result=research_result,
            competitor_analysis=competitor_analysis,
            business_findings=business_findings,
            validation_report=validation_report,
            review_result=review_result,
        )
