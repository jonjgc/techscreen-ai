"""criar tabela submissions

Revision ID: 001
Revises: 
Create Date: 2026-06-11 00:00:00.000000+00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── ENUMs ──────────────────────────────────────────────────────────────────
    submission_status = postgresql.ENUM(
        "pending", "processing", "completed", "failed",
        name="submission_status_enum",
        create_type=True,
    )
    submission_status.create(op.get_bind(), checkfirst=True)

    challenge_type = postgresql.ENUM(
        "code_review", "architecture", "algorithm", "system_design", "debugging",
        name="challenge_type_enum",
        create_type=True,
    )
    challenge_type.create(op.get_bind(), checkfirst=True)

    # ── Tabela submissions ─────────────────────────────────────────────────────
    op.create_table(
        "submissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            comment="Identificador único da submissão (UUID v4)",
        ),
        sa.Column(
            "user_email",
            sa.String(),
            nullable=False,
            comment="E-mail do desenvolvedor que submeteu o desafio",
        ),
        sa.Column(
            "challenge_type",
            postgresql.ENUM(
                "code_review", "architecture", "algorithm", "system_design", "debugging",
                name="challenge_type_enum",
                create_type=False,
            ),
            nullable=False,
            comment="Tipo do desafio técnico",
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
            comment="Código, arquitetura ou texto enviado pelo candidato",
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending", "processing", "completed", "failed",
                name="submission_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
            comment="Estado atual do processamento da submissão",
        ),
        sa.Column(
            "ai_feedback",
            sa.Text(),
            nullable=True,
            comment="Feedback gerado pelo agente de IA após avaliação",
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Mensagem de erro caso o processamento falhe",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Data/hora de criação da submissão (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Data/hora da última atualização (UTC)",
        ),
    )

    # ── Índices ────────────────────────────────────────────────────────────────
    op.create_index("ix_submissions_id", "submissions", ["id"], unique=False)
    op.create_index("ix_submissions_user_email", "submissions", ["user_email"], unique=False)
    op.create_index("ix_submissions_status", "submissions", ["status"], unique=False)

    # ── Trigger para atualizar updated_at automaticamente ──────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER update_submissions_updated_at
            BEFORE UPDATE ON submissions
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_submissions_updated_at ON submissions")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column")
    op.drop_index("ix_submissions_status", table_name="submissions")
    op.drop_index("ix_submissions_user_email", table_name="submissions")
    op.drop_index("ix_submissions_id", table_name="submissions")
    op.drop_table("submissions")

    # Remove ENUMs
    postgresql.ENUM(name="submission_status_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="challenge_type_enum").drop(op.get_bind(), checkfirst=True)
