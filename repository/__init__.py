"""
repository/__init__.py
Exports all repository classes for convenient imports.

"""
from repository.farmer_repository import FarmerRepository
from repository.farm_repository import FarmRepository
from repository.season_repository import SeasonRepository
from repository.loan_repository import LoanRepository
from repository.recommendation_repository import RecommendationRepository

__all__ = [
    "FarmerRepository",
    "FarmRepository",
    "SeasonRepository",
    "LoanRepository",
    "RecommendationRepository",
]
