"""empty message

Revision ID: 1f1008fcccee
Revises: 49396120ca92
Create Date: 2026-05-07 11:46:46.579568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f1008fcccee'
down_revision: Union[str, Sequence[str], None] = '49396120ca92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("ALTER TABLE users ALTER COLUMN created_at TYPE timestamptz USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at TYPE timestamptz USING updated_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE products ALTER COLUMN created_at TYPE timestamptz USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE products ALTER COLUMN updated_at TYPE timestamptz USING updated_at AT TIME ZONE 'UTC'")

def downgrade():
    op.execute("ALTER TABLE products ALTER COLUMN updated_at TYPE timestamp USING updated_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE products ALTER COLUMN created_at TYPE timestamp USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at TYPE timestamp USING updated_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE users ALTER COLUMN created_at TYPE timestamp USING created_at AT TIME ZONE 'UTC'")
