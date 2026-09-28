from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.database import Dataset, User, get_db
from app.services.dataset_service import process_dataset


# ============================================================
# ROUTER CONFIGURATION
# ============================================================

router = APIRouter(
    prefix="/api/datasets",
    tags=["Datasets"],
)


# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
}

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = (
    MAX_FILE_SIZE_MB * 1024 * 1024
)


# ============================================================
# UPLOAD DATASET
# ============================================================

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Upload a CSV or Excel dataset.

    Only authenticated users can upload datasets.
    """

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename was provided.",
        )

    original_filename = file.filename

    extension = Path(
        original_filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only CSV and XLSX files are allowed."
            ),
        )

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    # --------------------------------------------------------
    # Validate file size
    # --------------------------------------------------------

    if len(file_content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File is too large. "
                f"Maximum allowed size is "
                f"{MAX_FILE_SIZE_MB} MB."
            ),
        )

    temporary_file = None

    try:

        # ----------------------------------------------------
        # Create temporary file
        # ----------------------------------------------------

        temporary_file = NamedTemporaryFile(
            suffix=extension,
            delete=False,
        )

        temporary_file.write(
            file_content
        )

        temporary_file.close()

        # ----------------------------------------------------
        # Process dataset
        # ----------------------------------------------------

        dataset_name = Path(
            original_filename
        ).stem

        result = process_dataset(
            file_path=temporary_file.name,
            dataset_name=dataset_name,
        )

        # ----------------------------------------------------
        # Save dataset metadata
        # ----------------------------------------------------

        dataset_record = Dataset(
            name=result["dataset_name"],
            original_filename=original_filename,
            table_name=result["table_name"],
            file_type=result["file_type"],
            row_count=result["row_count"],
            column_count=result["column_count"],
            owner_id=current_user.id,
        )

        db.add(dataset_record)
        db.commit()
        db.refresh(dataset_record)

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "success": True,
            "message": (
                "Dataset uploaded and "
                "processed successfully."
            ),
            "dataset": {
                "id": dataset_record.id,
                "name": dataset_record.name,
                "original_filename": (
                    dataset_record.original_filename
                ),
                "file_type": dataset_record.file_type,
                "table_name": dataset_record.table_name,
                "row_count": dataset_record.row_count,
                "column_count": dataset_record.column_count,
                "owner_id": dataset_record.owner_id,
                "profile": result["profile"],
            },
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred "
                "while processing the dataset."
            ),
        ) from exc

    finally:

        # ----------------------------------------------------
        # Remove temporary file
        # ----------------------------------------------------

        if temporary_file is not None:

            temporary_path = Path(
                temporary_file.name
            )

            if temporary_path.exists():
                temporary_path.unlink()