from fastmcp import FastMCP
from typing import Annotated, Literal
from pydantic import Field

mcp = FastMCP("Student Assistant Server")

COURSES = {
    "AI": [
        {"title": "Lab 1", "deadline": "2026-03-24"},
        {"title": "Projekt", "deadline": "2026-03-29"},
    ],
    "Python": [
        {"title": "Inlämning 2", "deadline": "2026-03-25"},
        {"title": "Quiz", "deadline": "2026-03-27"},
    ],
    "Databaser": [
        {"title": "ER-modell", "deadline": "2026-03-26"},
        {"title": "SQL-labb", "deadline": "2026-03-30"},
    ],
}


@mcp.tool()
def list_courses() -> dict:
    """Returnerar alla tillgängliga kurser."""
    return {
        "source": "Student Assistant",
        "message": "Tillgängliga kurser hämtade.",
        "courses": list(COURSES.keys()),
    }


@mcp.tool()
def get_assignment_deadlines(
    course_name: Annotated[str, Field(description="Namn på kursen")],
) -> dict:
    """Hämtar alla uppgifter och deadlines för en kurs."""
    assignments = COURSES.get(course_name, [])

    return {
        "source": "Student Assistant",
        "message": f"Deadlines hämtade för kursen {course_name}.",
        "course": course_name,
        "assignments": assignments,
    }


@mcp.tool()
def suggest_study_plan(
    course_name: Annotated[str, Field(description="Namn på kursen")],
    hours_available: Annotated[
        int, Field(description="Antal timmar studenten har tillgängliga")
    ] = 5,
) -> dict:
    """Föreslår en enkel studieplan baserat på kurs och tillgängliga timmar."""
    assignments = COURSES.get(course_name, [])

    if not assignments:
        return {
            "source": "Student Assistant",
            "message": f"Ingen kurs hittades med namnet {course_name}.",
            "course": course_name,
            "plan": [],
        }

    hours_per_task = max(1, hours_available // len(assignments))

    plan = [
        {
            "task": assignment["title"],
            "deadline": assignment["deadline"],
            "suggested_hours": hours_per_task,
        }
        for assignment in assignments
    ]

    return {
        "source": "Student Assistant",
        "message": f"Studieplan skapad för kursen {course_name}.",
        "course": course_name,
        "hours_available": hours_available,
        "plan": plan,
    }


@mcp.tool()
def calculate_task_priority(
    title: Annotated[str, Field(description="Namn på uppgiften")],
    days_left: Annotated[int, Field(description="Antal dagar kvar till deadline")],
    importance: Annotated[
        int, Field(description="Hur viktig uppgiften är på en skala 1-5")
    ],
) -> dict:
    """Räknar ut en enkel prioritet för en uppgift."""
    priority_score = importance * 10 - days_left

    if priority_score >= 40:
        priority = "Hög"
    elif priority_score >= 20:
        priority = "Medel"
    else:
        priority = "Låg"

    return {
        "source": "Student Assistant",
        "message": "Prioritet beräknad.",
        "task": title,
        "days_left": days_left,
        "importance": importance,
        "priority_score": priority_score,
        "priority": priority,
    }


@mcp.tool()
def export_week_plan(
    course_name: Annotated[str, Field(description="Namn på kursen")],
    week: Annotated[int, Field(description="Veckonummer")],
    format: Annotated[
        Literal["text", "json"],
        Field(description="Format för export: text eller json"),
    ] = "text",
) -> dict:
    """Exporterar en enkel veckoplan för en kurs."""
    assignments = COURSES.get(course_name, [])

    if format == "json":
        return {
            "source": "Student Assistant",
            "message": f"Veckoplan exporterad som json för {course_name}.",
            "week": week,
            "course": course_name,
            "tasks": assignments,
        }

    lines = [f"Veckoplan vecka {week} för {course_name}:"]
    for assignment in assignments:
        lines.append(f"- {assignment['title']} (deadline: {assignment['deadline']})")

    return {
        "source": "Student Assistant",
        "message": f"Veckoplan exporterad som text för {course_name}.",
        "week": week,
        "course": course_name,
        "plan_text": "\n".join(lines),
    }


if __name__ == "__main__":
    import asyncio

    print("Starting Student Assistant MCP server on port 8001...")

    asyncio.run(
        mcp.run_http_async(
            host="0.0.0.0",
            port=8001,
            log_level="warning",
        )
    )