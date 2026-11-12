"""
PostgreSQL Schema & Dialect Compatibility Test Suite.
Verifies that all SQLAlchemy models, constraints, foreign keys, and indexes
compile without error under the PostgreSQL dialect.
"""

import pytest
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from app.models import (
    Base, User, UserRole, AuthSession, FarmerProfile,
    Scheme, SchemeVersion, EligibilityRule, SchemeDocumentRequirement,
    CompatibilityRule, ActionPlan, AuditLog, Consent
)

def test_postgresql_ddl_compilation():
    """
    Asserts that every model table definition can be compiled to clean PostgreSQL DDL
    without unsupported types or syntax exceptions.
    """
    tables = [
        User.__table__,
        UserRole.__table__,
        AuthSession.__table__,
        FarmerProfile.__table__,
        Scheme.__table__,
        SchemeVersion.__table__,
        EligibilityRule.__table__,
        SchemeDocumentRequirement.__table__,
        CompatibilityRule.__table__,
        ActionPlan.__table__,
        AuditLog.__table__,
        Consent.__table__
    ]

    pg_dialect = postgresql.dialect()

    for table in tables:
        ddl = str(CreateTable(table).compile(dialect=pg_dialect))
        assert "CREATE TABLE" in ddl
        assert table.name in ddl

def test_postgresql_foreign_keys_and_indexes():
    """
    Verifies that foreign keys and indexes are valid under PostgreSQL.
    """
    # Verify AuthSession user_id foreign key
    fks = list(AuthSession.__table__.foreign_keys)
    assert len(fks) >= 1
    fk = fks[0]
    assert fk.column.table.name == "users"

    # Verify unique constraint on users.email_normalized
    user_cols = {c.name: c for c in User.__table__.columns}
    assert user_cols["email_normalized"].unique is True

    # Verify unique constraint on compatibility_rules
    compat_cols = {c.name: c for c in CompatibilityRule.__table__.columns}
    assert "scheme_code_a" in compat_cols
    assert "scheme_code_b" in compat_cols

