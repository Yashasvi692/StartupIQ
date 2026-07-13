from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.profile_generator import (
    REQUIRED_PROFILE_FIELDS,
    _build_prompt_from_input,
    generate_startup_profile,
)
from backend.models.startup_profile import StartupProfile


def _make_mock_agent(profile: StartupProfile):
    agent = MagicMock()
    agent.run_structured = AsyncMock(return_value=profile)
    return agent


class TestBuildPromptFromInput:
    def test_builds_prompt_with_all_fields(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "Big problem",
            "target_customers": "Devs",
            "solution": "Great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing",
            "technical_information": "Python",
            "founder_assumptions": "Assumption",
            "validation_objectives": "Validation",
            "industry": "Tech",
            "stage": "idea",
        }
        prompt = _build_prompt_from_input(data)
        assert "TestCo" in prompt
        assert "Big problem" in prompt
        assert "StartupProfile" in prompt

    def test_omits_empty_fields(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "Big problem",
            "target_customers": "Devs",
            "solution": "Great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing",
            "technical_information": "Python",
        }
        prompt = _build_prompt_from_input(data)
        assert "Founder Assumptions" not in prompt
        assert "Validation Objectives" not in prompt

    def test_includes_confidence_instruction(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "Big problem",
            "target_customers": "Devs",
            "solution": "Great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing",
            "technical_information": "Python",
        }
        prompt = _build_prompt_from_input(data)
        assert "confidence" in prompt.lower()

    def test_empty_input_returns_basic_prompt(self):
        prompt = _build_prompt_from_input({})
        assert "StartupProfile" in prompt


class TestGenerateStartupProfile:
    @pytest.mark.asyncio
    async def test_returns_startup_profile_type(self):
        expected = StartupProfile(
            startup_name="TestCo",
            problem_statement="A big problem",
            target_customers="Developers",
            solution="A platform that solves the problem",
            business_model="Subscription SaaS",
            market_knowledge="Growing market with demand",
            technical_information="Python, React, PostgreSQL",
        )
        agent = _make_mock_agent(expected)
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Developers",
            "solution": "A platform that solves the problem",
            "business_model": "Subscription SaaS",
            "market_knowledge": "Growing market with demand",
            "technical_information": "Python, React, PostgreSQL",
        }
        result = await generate_startup_profile(data, agent=agent)
        assert isinstance(result, StartupProfile)
        assert result.startup_name == "TestCo"

    @pytest.mark.asyncio
    async def test_returns_input_values_from_agent(self):
        expected = StartupProfile(
            startup_name="MyStartup",
            problem_statement="Solves X",
            target_customers="SMBs",
            solution="AI platform",
            business_model="Freemium",
            market_knowledge="Early stage",
            technical_information="Node.js",
        )
        agent = _make_mock_agent(expected)
        data = {
            "startup_name": "MyStartup",
            "problem_statement": "Solves X",
            "target_customers": "SMBs",
            "solution": "AI platform",
            "business_model": "Freemium",
            "market_knowledge": "Early stage",
            "technical_information": "Node.js",
        }
        result = await generate_startup_profile(data, agent=agent)
        assert result.startup_name == "MyStartup"
        assert result.problem_statement == "Solves X"
        assert result.target_customers == "SMBs"

    @pytest.mark.asyncio
    async def test_required_fields_not_empty(self):
        expected = StartupProfile(
            startup_name="RequiredCo",
            problem_statement="Critical problem",
            target_customers="Enterprise",
            solution="Enterprise solution",
            business_model="Per-seat licensing",
            market_knowledge="Fortune 500 demand",
            technical_information="Java, Kubernetes",
        )
        agent = _make_mock_agent(expected)
        data = {
            "startup_name": "RequiredCo",
            "problem_statement": "Critical problem",
            "target_customers": "Enterprise",
            "solution": "Enterprise solution",
            "business_model": "Per-seat licensing",
            "market_knowledge": "Fortune 500 demand",
            "technical_information": "Java, Kubernetes",
        }
        result = await generate_startup_profile(data, agent=agent)
        assert result.startup_name.strip() != ""
        assert result.problem_statement.strip() != ""
        assert result.target_customers.strip() != ""
        assert result.solution.strip() != ""
        assert result.business_model.strip() != ""
        assert result.market_knowledge.strip() != ""
        assert result.technical_information.strip() != ""

    @pytest.mark.asyncio
    async def test_optional_fields_handled(self):
        expected = StartupProfile(
            startup_name="OptCo",
            problem_statement="A problem",
            target_customers="Everyone",
            solution="A solution",
            business_model="Free",
            market_knowledge="Big market",
            technical_information="Rust",
            tagline="We do stuff",
            founder_assumptions="People will pay",
            validation_objectives="Test demand",
            industry="Fintech",
            stage="prototype",
        )
        agent = _make_mock_agent(expected)
        data = {
            "startup_name": "OptCo",
            "problem_statement": "A problem",
            "target_customers": "Everyone",
            "solution": "A solution",
            "business_model": "Free",
            "market_knowledge": "Big market",
            "technical_information": "Rust",
            "tagline": "We do stuff",
            "founder_assumptions": "People will pay",
            "validation_objectives": "Test demand",
            "industry": "Fintech",
            "stage": "prototype",
        }
        result = await generate_startup_profile(data, agent=agent)
        assert result.tagline == "We do stuff"
        assert result.founder_assumptions == "People will pay"
        assert result.validation_objectives == "Test demand"
        assert result.industry == "Fintech"
        assert result.stage == "prototype"

    @pytest.mark.asyncio
    async def test_passes_message_to_agent_run_structured(self):
        expected = StartupProfile(
            startup_name="MsgCo",
            problem_statement="Problem",
            target_customers="Users",
            solution="Solution",
            business_model="Ads",
            market_knowledge="Big",
            technical_information="Go",
        )
        agent = MagicMock()
        agent.run_structured = AsyncMock(return_value=expected)
        data = {
            "startup_name": "MsgCo",
            "problem_statement": "Problem",
            "target_customers": "Users",
            "solution": "Solution",
            "business_model": "Ads",
            "market_knowledge": "Big",
            "technical_information": "Go",
        }
        await generate_startup_profile(data, agent=agent)
        agent.run_structured.assert_awaited_once()
        call_args = agent.run_structured.await_args[0][0]
        assert isinstance(call_args, str)
        assert "MsgCo" in call_args
        assert "Problem" in call_args
        assert "StartupProfile" in call_args

    @pytest.mark.asyncio
    async def test_all_fields_are_strings_in_mocked_output(self):
        expected = StartupProfile(
            startup_name="StringCo",
            problem_statement="Problem",
            target_customers="Users",
            solution="Solution",
            business_model="Ads",
            market_knowledge="Big",
            technical_information="Go",
        )
        agent = _make_mock_agent(expected)
        data = {
            "startup_name": "StringCo",
            "problem_statement": "Problem",
            "target_customers": "Users",
            "solution": "Solution",
            "business_model": "Ads",
            "market_knowledge": "Big",
            "technical_information": "Go",
        }
        result = await generate_startup_profile(data, agent=agent)
        for field_name in REQUIRED_PROFILE_FIELDS:
            value = getattr(result, field_name)
            assert isinstance(value, str), f"{field_name} should be str, got {type(value)}"


class TestRequiredProfileFields:
    def test_required_fields_defined(self):
        assert len(REQUIRED_PROFILE_FIELDS) >= 6
        assert "startup_name" in REQUIRED_PROFILE_FIELDS
        assert "problem_statement" in REQUIRED_PROFILE_FIELDS
        assert "solution" in REQUIRED_PROFILE_FIELDS

    def test_required_fields_correspond_to_startup_profile(self):
        profile = StartupProfile(
            startup_name="Test",
            problem_statement="P",
            target_customers="C",
            solution="S",
            business_model="B",
            market_knowledge="M",
            technical_information="T",
        )
        for field in REQUIRED_PROFILE_FIELDS:
            assert hasattr(profile, field)
