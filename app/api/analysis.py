from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.agents.sql_agent import generate_sql
from app.analysis.analysis_pipeline import analyze_result
from app.auth.dependencies import get_current_user
from app.database.database import (AnalysisHistory,User,)
from app.database.database import SessionLocal
from app.services.sql_service import run_sql_query
from app.visualization.chart_service import chart_to_json


router = APIRouter(
    prefix="/api/analysis",
    tags=["AI Analysis"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class AnalysisRequest(BaseModel):
    question: str
    table_name: str


# ============================================================
# ANALYSIS ENDPOINT
# ============================================================

@router.post("/query")
def analyze_question(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Convert a natural-language question into SQL,
    execute the SQL safely, analyze the result,
    generate an AI insight, and return chart-ready data.
    """

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        # ----------------------------------------------------
        # STEP 1: Generate SQL
        # ----------------------------------------------------

        generated_sql = generate_sql(
            question,
            request.table_name,
        )

        # ----------------------------------------------------
        # STEP 2: Execute SQL
        # ----------------------------------------------------

        sql_result = run_sql_query(
            generated_sql
        )

        dataframe = sql_result["data"]

        # ----------------------------------------------------
        # STEP 3: Complete analysis
        # ----------------------------------------------------

        analysis_result = analyze_result(
            user_question=question,
            dataframe=dataframe,
        )

        # ----------------------------------------------------
        # STEP 4: Convert result to JSON
        # ----------------------------------------------------

        result_data = dataframe.to_dict(
            orient="records"
        )

        # ----------------------------------------------------
        # STEP 5: Convert chart to JSON
        # ----------------------------------------------------

        chart_json = chart_to_json(
            analysis_result["chart"]
        )

        db = SessionLocal()

        try:
            history_record = AnalysisHistory(
                question=question,
                table_name=request.table_name,
                generated_sql=generated_sql,
                insight=analysis_result["insight"],
                owner_id=current_user.id,
            )

            db.add(history_record)
            db.commit()

        except Exception:
            db.rollback()

        finally:
            db.close()

        # ----------------------------------------------------
        # STEP 6: Return complete response
        # ----------------------------------------------------

        return {
            "success": True,
            "question": question,
            "sql": generated_sql,
            "row_count": int(
                len(dataframe)
            ),
            "column_count": int(
                len(dataframe.columns)
            ),
            "columns": [
                str(column)
                for column in dataframe.columns
            ],
            "data": result_data,
            "analysis": analysis_result[
                "analysis"
            ],
            "formatted_analysis": analysis_result[
                "formatted_analysis"
            ],
            "insight": analysis_result[
                "insight"
            ],
            "chart_available": (
                chart_json is not None
            ),
            "chart": chart_json,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please try again.",
        )

@router.get("/history")
def get_analysis_history(
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        history = (
            db.query(AnalysisHistory)
            .filter(
                AnalysisHistory.owner_id == current_user.id
            )
            .order_by(
                AnalysisHistory.created_at.desc()
            )
            .all()
        )

        return {
            "success": True,
            "history": [
                {
                    "id": item.id,
                    "question": item.question,
                    "table_name": item.table_name,
                    "generated_sql": item.generated_sql,
                    "insight": item.insight,
                    "created_at": item.created_at.isoformat(),
                }
                for item in history
            ],
        }

    finally:
        db.close()


@router.delete("/history/{history_id}")
def delete_analysis_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        history_item = (
            db.query(AnalysisHistory)
            .filter(
                AnalysisHistory.id == history_id,
                AnalysisHistory.owner_id == current_user.id,
            )
            .first()
        )

        if history_item is None:
            raise HTTPException(
                status_code=404,
                detail="History item not found.",
            )

        db.delete(history_item)
        db.commit()

        return {
            "success": True,
            "message": "History item deleted successfully.",
        }

    finally:
        db.close()