from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

from corund import db
from corund.event_model import Event


@dataclass
class DecisionRecord:
    decision_id: str
    agent: str
    workspace: str | None
    tool_name: str
    args: dict[str, Any]
    reason: str


class MemoryStore:
    """
    Local-first memory store backed by SQLite.
    """

    def __init__(self) -> None:
        db.migrate()

    def put_event(self, event: Event) -> None:
        conn = db.connect()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO events(event_id, type, source, payload_json) VALUES (?, ?, ?, ?)",
                (
                    event.id,
                    event.type,
                    event.source,
                    json.dumps(event.payload, ensure_ascii=False),
                ),
            )
        finally:
            conn.close()

    def new_decision(self, *, agent: str, workspace: str | None, tool_name: str, args: dict, reason: str) -> DecisionRecord:
        rec = DecisionRecord(
            decision_id=str(uuid.uuid4()),
            agent=agent,
            workspace=workspace,
            tool_name=tool_name,
            args=args,
            reason=reason,
        )
        conn = db.connect()
        try:
            conn.execute(
                """
                INSERT INTO agent_decisions(decision_id, agent, workspace, tool_name, args_json, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.decision_id,
                    rec.agent,
                    rec.workspace,
                    rec.tool_name,
                    json.dumps(rec.args, ensure_ascii=False),
                    rec.reason,
                ),
            )
        finally:
            conn.close()
        return rec

    def mark_decision_executed(self, decision_id: str, result: str = "") -> None:
        conn = db.connect()
        try:
            conn.execute(
                """
                UPDATE agent_decisions
                SET executed=1, execution_result=?
                WHERE decision_id=?
                """,
                (result, decision_id),
            )
        finally: 
            conn.close()

    def mark_decision_blocked(self, decision_id: str, reason: str) -> None:
        conn = db.connect()
        try:
            conn.execute(
                """
                UPDATE agent_decisions
                SET blocked_by_privacy=1, execution_result=?
                WHERE decision_id=?
                """,
                (reason, decision_id),
            )
        finally:
            conn.close()


memory_store = MemoryStore()
