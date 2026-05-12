"""updated_at_nullable

Revision ID: 57e2ce3f1fc6
Revises: 1f1008fcccee
Create Date: 2026-05-12 14:14:45.257595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '57e2ce3f1fc6'
down_revision: Union[str, Sequence[str], None] = '1f1008fcccee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('products', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)

def downgrade() -> None:
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute("UPDATE products SET updated_at = created_at WHERE updated_at IS NULL")
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('products', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
