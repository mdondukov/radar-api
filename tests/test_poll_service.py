from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Area, Region
from app.models.step import StepType
from app.services import poll_service
from tests.factories import make_answer, make_project, make_question, make_step


async def test_get_steps_localizes_and_reports_type(db_session: AsyncSession) -> None:
    project = await make_project(db_session)
    await make_step(db_session, project, type_=StepType.RADAR)

    result = await poll_service.get_steps(db_session, project, "ru")

    assert result[0].type == "RADAR"
    assert result[0].name == "Шаг"


async def test_get_regions_nests_areas_sorted_by_ord(db_session: AsyncSession) -> None:
    project = await make_project(db_session)
    region = Region(project_id=project.id, code="region-1", name={"ru": "Область"}, ord=1)
    db_session.add(region)
    await db_session.flush()

    area_2 = Area(
        project_id=project.id, region_id=region.id, code="area-2", name={"ru": "Второй"}, ord=2
    )
    area_1 = Area(
        project_id=project.id, region_id=region.id, code="area-1", name={"ru": "Первый"}, ord=1
    )
    db_session.add_all([area_2, area_1])
    await db_session.flush()

    result = await poll_service.get_regions(db_session, project, "ru")

    assert [a.name for a in result[0].areas] == ["Первый", "Второй"]


async def test_get_regions_returns_empty_areas_list_for_region_without_areas(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    db_session.add(Region(project_id=project.id, code="region-1", name={"ru": "Область"}, ord=1))
    await db_session.flush()

    result = await poll_service.get_regions(db_session, project, "ru")

    assert result[0].areas == []


async def test_get_questions_nests_answers_with_recommendation_and_multi_select_flag(
    db_session: AsyncSession,
) -> None:
    project = await make_project(db_session)
    step = await make_step(db_session, project)
    question = await make_question(db_session, project, step, is_multi_select=True)
    await make_answer(
        db_session, project, question, weight=0, recommendation={"ru": "Совет"}
    )
    await make_answer(db_session, project, question, weight=3)

    result = await poll_service.get_questions(db_session, project, "ru")

    assert result[0].is_multi_select is True
    assert [a.recommendation for a in result[0].answers] == ["Совет", None]
