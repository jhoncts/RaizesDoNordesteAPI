"""adiciona campos de fidelidade ao usuario

Revision ID: 02386f059e2a
Revises: 942be96f8c7f
Create Date: 2026-09-08 13:06:48.715975
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "02386f059e2a"
down_revision: Union[str, Sequence[str], None] = "942be96f8c7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "consentimento_fidelidade",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "usuarios",
        sa.Column(
            "pontos_fidelidade",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "usuarios",
        "pontos_fidelidade",
    )

    op.drop_column(
        "usuarios",
        "consentimento_fidelidade",
    )