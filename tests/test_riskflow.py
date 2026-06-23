from db.session import SessionLocal

from repository.loan_repository import LoanRepository
from repository.season_repository import SeasonRepository
from repository.farm_repository import FarmRepository
from ai.weather.weather_repository import WeatherRepository
from repository.recommendation_repository import (
    RecommendationRepository,
)

from services.risk_assesment_service import (
    RiskAssessmentService,
)


LOAN_ID = "0376042a-c9f8-4ba2-94aa-7fbbb801028f"


def divider(title: str):

    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)


def main():

    db = SessionLocal()

    try:

        # ------------------------------------
        # STEP 1
        # ------------------------------------

        divider("STEP 1 - LOAN")

        loan_repo = LoanRepository(db)

        loan = loan_repo.get_loan(
            LOAN_ID
        )

        print(loan)

        if loan is None:
            raise Exception(
                "Loan not found"
            )

        # ------------------------------------
        # STEP 2
        # ------------------------------------

        divider("STEP 2 - SEASON")

        season_repo = SeasonRepository(db)

        season = season_repo.get_season(
            loan.season_id
        )

        print(season)

        # ------------------------------------
        # STEP 3
        # ------------------------------------

        divider("STEP 3 - FARM")

        farm_repo = FarmRepository(db)

        farm = farm_repo.get_farm(
            season.farm_id
        )

        print(farm)

        # ------------------------------------
        # STEP 4
        # ------------------------------------

        divider("STEP 4 - WEATHER")

        weather_repo = WeatherRepository(db)

        weather = (
            weather_repo
            .get_latest_snapshot(
                farm.id
            )
        )

        from services.weather_service import WeatherService


        divider("UPDATING WEATHER")


        weather_snapshot = WeatherService(
            db
        ).update_farm_weather(
            farm
        )


        print(weather_snapshot)

        print(weather)

        # ------------------------------------
        # STEP 5
        # ------------------------------------

        divider("STEP 5 - RECOMMENDATIONS")

        recommendation_repo = (
            RecommendationRepository(db)
        )

        recommendations = (
            recommendation_repo
            .list_season_recommendations(
                season.id
            )
        )

        print(
            f"Recommendation Count: "
            f"{len(recommendations)}"
        )

        # ------------------------------------
        # STEP 6
        # ------------------------------------

        divider("STEP 6 - CALCULATE RISK")

        service = RiskAssessmentService(
            db
        )

        assessment = (
            service.calculate_risk(
                loan.id
            )
        )

        print(
            f"Assessment ID: "
            f"{assessment.id}"
        )

        print(
            f"Score: "
            f"{assessment.score}"
        )

        print(
            f"Level: "
            f"{assessment.risk_level}"
        )

        print(
            f"Action: "
            f"{assessment.action}"
        )

        # ------------------------------------
        # STEP 7
        # ------------------------------------

        divider("STEP 7 - FETCH LATEST")

        latest = (
            service.get_latest_risk(
                loan.id
            )
        )

        print(latest)
        print("\nBreakdown of risk components:")
        print(f"  Weather Risk:     {assessment.weather_risk}")
        print(f"  Season Risk:      {assessment.season_risk}")
        print(f"  Harvest Risk:     {assessment.harvest_risk}")
        print(f"  Financial Risk:   {assessment.financial_risk}")
        print(f"  Farmer Risk:      {assessment.farmer_risk}")
        print(f"  Report Risk:      {assessment.report_risk}")
        print(f"  Compliance Risk:  {assessment.compliance_risk}")


        # ------------------------------------
        # STEP 8
        # ------------------------------------

        divider("STEP 8 - HISTORY")

        history = (
            service.get_risk_history(
                loan.id
            )
        )

        print(
            f"History Count: "
            f"{len(history)}"
        )

        for item in history:

            print(
                item.id,
                item.score,
                item.risk_level,
            )

        divider("SUCCESS")

    finally:

        db.close()


if __name__ == "__main__":
    main()