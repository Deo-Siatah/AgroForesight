"""
api/v1/__init__.py
Aggregates all v1 routers into a single include-able router.
"""
from fastapi import APIRouter

from api import risk_assessments
from api.v1 import auth, saccos, farmers, farms, seasons, loans,recommendations,risk_assessments

router = APIRouter()

router.include_router(auth.router)
router.include_router(saccos.router)
router.include_router(farmers.router)
router.include_router(farms.router)
router.include_router(seasons.router)
router.include_router(loans.router)
router.include_router(recommendations.router)
router.include_router(risk_assessments.router)
