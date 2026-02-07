from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentResult:
    task: str
    plan: list[str]
    execution_steps: list[str]
    output: dict


class AgentRegistry:
    def create_ppt(self, topic: str) -> AgentResult:
        plan = ["Define audience and objective", "Create slide outline", "Draft speaker notes"]
        output = {
            "title": topic,
            "outline": ["Intro", "Problem", "Approach", "Roadmap", "Q&A"],
            "slides": [{"slide": i + 1, "title": t} for i, t in enumerate(["Intro", "Problem", "Approach", "Roadmap", "Q&A"])],
        }
        return AgentResult(task=f"create_ppt:{topic}", plan=plan, execution_steps=["analyze topic", "build outline", "return plan"], output=output)

    def summarize_pdf(self, path: str) -> AgentResult:
        exists = Path(path).exists()
        summary = {"path": path, "exists": exists, "summary": "Stub summary", "key_points": ["Point A", "Point B"]}
        return AgentResult(task=f"summarize_pdf:{path}", plan=["Load PDF", "Extract sections", "Generate summary"], execution_steps=["read metadata", "produce structured summary"], output=summary)

    def generate_notes(self, topic: str) -> AgentResult:
        notes = {"topic": topic, "sections": ["Overview", "Deep Dive", "Next Steps"], "notes": f"Detailed notes about {topic}."}
        return AgentResult(task=f"generate_notes:{topic}", plan=["Understand topic", "Draft sections", "Expand details"], execution_steps=["collect context", "compose notes"], output=notes)
