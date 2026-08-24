from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.summary import AnswerSelectIn
from app.services.indicator_service import compute_indicators
from tests.factories import make_answer, make_indicator, make_project, make_question, make_step


async def test_no_answers_gives_zero_value(db_session: AsyncSession) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step)

    result = await compute_indicators(db_session, project, "ru", [])

    assert result[0].value == 0.0


async def test_value_is_the_flat_average_of_selected_answer_weights(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step)
    question = await make_question(db_session, project, step)
    a0 = await make_answer(db_session, project, question, weight=0)
    a2 = await make_answer(db_session, project, question, weight=2, ord=2)

    answers = [
        AnswerSelectIn(step_id=step.id, question_id=question.id, answer_id=a0.id),
        AnswerSelectIn(step_id=step.id, question_id=question.id, answer_id=a2.id),
    ]

    # both answers land under the same question (a multi-select scenario) and
    # are still averaged together, exactly like answers from different questions
    result = await compute_indicators(db_session, project, "ru", answers)

    assert result[0].value == 1.0


async def test_value_rounds_to_one_decimal_place(db_session: AsyncSession) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step)
    q1 = await make_question(db_session, project, step)
    q2 = await make_question(db_session, project, step)
    q3 = await make_question(db_session, project, step)
    a1 = await make_answer(db_session, project, q1, weight=1)
    a2 = await make_answer(db_session, project, q2, weight=1)
    a3 = await make_answer(db_session, project, q3, weight=2)

    # average of [1, 1, 2] is 1.333... -> rounds to 1.3
    answers = [
        AnswerSelectIn(step_id=step.id, question_id=q1.id, answer_id=a1.id),
        AnswerSelectIn(step_id=step.id, question_id=q2.id, answer_id=a2.id),
        AnswerSelectIn(step_id=step.id, question_id=q3.id, answer_id=a3.id),
    ]

    result = await compute_indicators(db_session, project, "ru", answers)

    assert result[0].value == 1.3


async def test_answers_from_a_different_step_do_not_affect_the_indicator(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    other_step = await make_step(db_session, project, ord=2)
    await make_indicator(db_session, project, step)
    other_question = await make_question(db_session, project, other_step)
    other_answer = await make_answer(db_session, project, other_question, weight=3)

    answers = [
        AnswerSelectIn(
            step_id=other_step.id, question_id=other_question.id, answer_id=other_answer.id
        )
    ]

    result = await compute_indicators(db_session, project, "ru", answers)

    assert result[0].value == 0.0


async def test_risk_zone_boundaries_are_inclusive_on_the_lower_band(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step, high_risk_max=1, medium_risk_max=2)
    question = await make_question(db_session, project, step)
    exactly_high = await make_answer(db_session, project, question, weight=1)

    result = await compute_indicators(
        db_session,
        project,
        "ru",
        [AnswerSelectIn(step_id=step.id, question_id=question.id, answer_id=exactly_high.id)],
    )

    assert result[0].value == 1.0
    assert result[0].risk_zone == "high"
    assert result[0].risk_text == "high risk"


async def test_risk_zone_boundaries_are_inclusive_on_the_medium_band(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step, high_risk_max=1, medium_risk_max=2)
    question = await make_question(db_session, project, step)
    exactly_medium = await make_answer(db_session, project, question, weight=2)

    result = await compute_indicators(
        db_session,
        project,
        "ru",
        [AnswerSelectIn(step_id=step.id, question_id=question.id, answer_id=exactly_medium.id)],
    )

    assert result[0].risk_zone == "medium"
    assert result[0].risk_text == "medium risk"


async def test_value_above_the_medium_threshold_is_low_risk(db_session: AsyncSession) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step, high_risk_max=1, medium_risk_max=2)
    question = await make_question(db_session, project, step)
    above_medium = await make_answer(db_session, project, question, weight=3)

    result = await compute_indicators(
        db_session,
        project,
        "ru",
        [AnswerSelectIn(step_id=step.id, question_id=question.id, answer_id=above_medium.id)],
    )

    assert result[0].risk_zone == "low"
    assert result[0].risk_text == "low risk"


async def test_without_configured_thresholds_the_zone_is_always_low(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step)  # no thresholds, like zhashyl-climate

    result = await compute_indicators(db_session, project, "ru", [])

    assert result[0].risk_zone == "low"
    assert result[0].risk_text == "low risk"


async def test_indicators_from_other_projects_are_not_included(db_session: AsyncSession) -> None:
    project_a = await make_project(db_session)
    step_a = await make_step(db_session, project_a)
    await make_indicator(db_session, project_a, step_a)

    project_b = await make_project(db_session)
    step_b = await make_step(db_session, project_b)
    await make_indicator(db_session, project_b, step_b)

    result = await compute_indicators(db_session, project_a, "ru", [])

    assert len(result) == 1


async def test_risk_text_falls_back_to_the_project_default_locale(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    await make_indicator(db_session, project, step, high_risk_max=1, medium_risk_max=2)

    result = await compute_indicators(db_session, project, "ky", [])

    assert result[0].risk_text == "high risk"
