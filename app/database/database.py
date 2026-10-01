import os
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/ai_data_analyst.db",
)


# ============================================================
# DATABASE ENGINE
# ============================================================

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1,
    )

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg2://",
        1,
    )


if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        },
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# BASE MODEL
# ============================================================

Base = declarative_base()


# ============================================================
# USER MODEL
# ============================================================

class User(Base):
    """
    Stores application users.

    Passwords will NOT be stored directly.
    Authentication logic will store password hashes.
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    datasets = relationship(
        "Dataset",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    analysis_history = relationship(
        "AnalysisHistory",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


# ============================================================
# DATASET MODEL
# ============================================================

class Dataset(Base):
    """
    Stores metadata about datasets uploaded by users.

    The actual uploaded data will be represented separately
    as SQL tables.
    """

    __tablename__ = "datasets"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    table_name = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    file_type = Column(
        String(20),
        nullable=False,
    )

    row_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    column_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    owner = relationship(
        "User",
        back_populates="datasets",
    )


# ============================================================
# ANALYSIS HISTORY MODEL
# ============================================================

class AnalysisHistory(Base):
    """
    Stores analysis history for each user.
    """

    __tablename__ = "analysis_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    question = Column(
        String(1000),
        nullable=False,
    )

    table_name = Column(
        String(255),
        nullable=False,
    )

    generated_sql = Column(
        String(5000),
        nullable=False,
    )

    insight = Column(
        String(5000),
        nullable=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    owner = relationship(
        "User",
        back_populates="analysis_history",
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def create_database_tables():
    """
    Create all application metadata tables if they
    do not already exist.
    """

    Base.metadata.create_all(
        bind=engine
    )


# ============================================================
# DATABASE SESSION DEPENDENCY
# ============================================================

def get_db():
    """
    Provide a database session to application components.

    The session is automatically closed after use.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()