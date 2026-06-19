"""
api/v1/__init__.py
Aggregates all v1 routers into a single include-able router.
"""
from fastapi import APIRouter

from api.v1 import farmers, farms, seasons, loans

router = APIRouter()

router.include_router(farmers.router)
router.include_router(farms.router)
router.include_router(seasons.router)
router.include_router(loans.router)
