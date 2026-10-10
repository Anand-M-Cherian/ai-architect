"""Manual check: run the requirements agent on canned conversations and print the specs.

Needs Postgres (config.yaml `memory`, DB_USER/DB_PASSWORD) and OPENAI_API_KEY in .env.
Run from the project root:  uv run python scripts/try_requirements_agent.py
"""

import os
import re
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
from langchain_core.messages import ToolMessage  # noqa: E402
from langgraph.types import Command  # noqa: E402

load_dotenv(ROOT / ".env")

from agent.factory import build_req_agent  # noqa: E402
from schemas import RequirementSpec  # noqa: E402

FALLBACK_ANSWER = "No preference, use your judgement."
DAU_QUESTION = re.compile(
    r"daily active|\bDAU\b|how many (users|people)", re.IGNORECASE
)


def run(agent, first_message, answers):
    """Run one conversation, answering each ask_user question from `answers`."""
    config = {
        "configurable": {"thread_id": "try-" + uuid4().hex[:8]},
        "recursion_limit": 25,
    }
    answers = iter(answers)
    questions = []
    result = agent.invoke(
        {"messages": [{"role": "user", "content": first_message}]}, config
    )
    while result.get("__interrupt__"):
        decisions = []
        for request in result["__interrupt__"][0].value["action_requests"]:
            question = request["args"].get("question") or request["description"]
            answer = next(answers, FALLBACK_ANSWER)
            questions.append(question)
            print(f"  Q: {question}\n  A: {answer}")
            decisions.append({"type": "respond", "message": answer})
        result = agent.invoke(Command(resume={"decisions": decisions}), config)

    spec = result.get("structured_response")
    if not isinstance(spec, RequirementSpec):
        raise RuntimeError("requirements agent finished without a structured spec")
    retries = sum(
        1
        for m in result["messages"]
        if isinstance(m, ToolMessage)
        and m.name == RequirementSpec.__name__
        and not str(m.content).startswith("Returning structured response")
    )
    return questions, spec, retries


def budget_recorded(spec):
    return any(
        "budget" in (key + " " + value).lower()
        for key, value in spec.clarifications.items()
    )


def check(label, ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    return ok


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "OPENAI_API_KEY is not set. Add it to .env (and DB_USER/DB_PASSWORD if not postgres/postgres)."
        )
        sys.exit(1)

    agent, _memory, database = build_req_agent()
    results = []
    try:
        print("\n=== Run 1: WhatsApp, 1M DAU, budget given ===")
        questions, spec, retries = run(
            agent,
            "Design WhatsApp for 1M daily active users in India.",
            [
                "Yes, voice and video calls.",
                "$12,000 per month.",
                "India and Singapore.",
                "No compliance needs.",
            ],
        )
        print(spec.model_dump_json(indent=2))
        print(f"  structured-output retries: {retries}")
        results.append(
            check(
                "budget is 12000",
                spec.explicit_requirements.monthly_budget_usd == 12000,
            )
        )
        results.append(
            check("clarifications record the budget answer", budget_recorded(spec))
        )

        print("\n=== Run 2: food delivery, no DAU given ===")
        questions, spec, retries = run(
            agent,
            "Build me a food delivery app for Bangalore",
            [
                "About 500,000 daily active users.",
                "No budget ceiling.",
                "No compliance needs.",
            ],
        )
        print(spec.model_dump_json(indent=2))
        print(f"  structured-output retries: {retries}")
        asked_dau = any(DAU_QUESTION.search(q) for q in questions)
        results.append(check("agent asked for DAU via ask_user", asked_dau))
        results.append(
            check(
                "DAU is the user's 500000",
                spec.explicit_requirements.daily_active_users == 500_000,
            )
        )

        print("\n=== Run 3: WhatsApp, 1M DAU, budget declined ===")
        questions, spec, retries = run(
            agent,
            "Design WhatsApp for 1M daily active users in India.",
            [
                "Yes, voice and video calls.",
                "I'd rather not say.",
                "India and Singapore.",
                "No compliance needs.",
            ],
        )
        print(spec.model_dump_json(indent=2))
        print(f"  structured-output retries: {retries}")
        results.append(
            check(
                "budget is null", spec.explicit_requirements.monthly_budget_usd is None
            )
        )
        results.append(
            check("clarifications record the declined budget", budget_recorded(spec))
        )
    finally:
        database.close()

    print(f"\n{sum(results)}/{len(results)} checks passed")


if __name__ == "__main__":
    main()
