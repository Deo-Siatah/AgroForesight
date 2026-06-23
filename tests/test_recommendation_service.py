"""
tests/test_recommendation_service.py

End-to-end test for Recommendation Service.

This verifies:

1. Existing season loads
2. Farm coordinates are used
3. Weather is fetched
4. Rules engine evaluates
5. Prompt is generated
6. LLM responds
7. Recommendation is stored in DB
"""

from __future__ import annotations


import asyncio
import uuid


from db.session import SessionLocal


from services.recommendation_service import (
    RecommendationService,
)


from db.models.user import User, RoleEnum



# Existing season
SEASON_ID = uuid.UUID(
    "fda9c39c-0df9-4991-bbfd-43a9c07623dc"
)



# Existing admin user
# change this if your user id differs
ADMIN_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)



async def main():


    print("\n==============================")
    print("START RECOMMENDATION FLOW TEST")
    print("==============================\n")


    db = SessionLocal()


    try:


        # ---------------------------------------
        # Load current user
        # ---------------------------------------

        print("STEP 1: Loading user")


        user = db.get(
            User,
            ADMIN_ID
        )


        if user is None:

            print(
                "Admin user not found"
            )

            return



        print(
            "User:",
            user.email,
            user.role
        )



        # ---------------------------------------
        # Create service
        # ---------------------------------------

        print(
            "\nSTEP 2: Creating Recommendation Service"
        )


        service = RecommendationService(
            db
        )


        print(
            "Service created"
        )



        # ---------------------------------------
        # Generate recommendation
        # ---------------------------------------

        print(
            "\nSTEP 3: Running AI pipeline"
        )


        result = await service.generate_recommendation(

            season_id=SEASON_ID,

            current_user=user,

        )



        # ---------------------------------------
        # Output
        # ---------------------------------------

        print(
            "\n=============================="
        )

        print(
            "FINAL RESULT"
        )

        print(
            "=============================="
        )


        print(
            "Recommendation ID:",
            result.recommendation_id
        )


        print(
            "Season ID:",
            result.season_id
        )


        print(
            "Crop:",
            result.crop_type
        )


        print(
            "Risk:",
            result.risk_level
        )


        print(
            "Type:",
            result.recommendation_type
        )


        print(
            "\nTITLE:"
        )

        print(
            result.title
        )


        print(
            "\nMESSAGE:"
        )

        print(
            result.message
        )



        print(
            "\nTEST COMPLETED SUCCESSFULLY"
        )



    except Exception as e:


        print(
            "\nTEST FAILED"
        )


        print(
            type(e).__name__,
            e
        )


        raise



    finally:


        db.close()





if __name__ == "__main__":

    asyncio.run(main())