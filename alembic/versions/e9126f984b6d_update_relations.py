"""update relations

Revision ID: e9126f984b6d
Revises: 7a238f8590e5
Create Date: 2025-12-10 14:45:09.328631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9126f984b6d'
down_revision: Union[str, Sequence[str], None] = '7a238f8590e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'updated_at', nullable=True)
    op.alter_column('products', 'updated_at', nullable=True)


def downgrade() -> None:
    # сначала заполняем NULL-значения, иначе Postgres не даст поставить NOT NULL
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute("UPDATE products SET updated_at = created_at WHERE updated_at IS NULL")

    op.alter_column('users', 'updated_at', nullable=False)
    op.alter_column('products', 'updated_at', nullable=False)
