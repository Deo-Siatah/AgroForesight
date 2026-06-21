"""
Repository layer — Sacco
Responsibility: DB access ONLY. No validation, no business logic.
"""
from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from db.models.sacco import Sacco


class SaccoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_sacco(self, sacco: Sacco) -> Sacco:
        self.db.add(sacco)
        self.db.flush()
        return sacco

    def get_sacco(self, sacco_id: uuid.UUID) -> Sacco | None:
        return self.db.get(Sacco, sacco_id)

    def list_saccos(self, *, offset: int = 0, limit: int = 20) -> List[Sacco]:
        return self.db.query(Sacco).offset(offset).limit(limit).all()