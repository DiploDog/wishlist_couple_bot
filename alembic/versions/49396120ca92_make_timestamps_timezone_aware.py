from alembic import op
import sqlalchemy as sa

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "49396120ca92"
down_revision: Union[str, Sequence[str], None] = "e9126f984b6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "users", "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users", "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,  # поставь True, если у тебя nullable=True в реальной схеме
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "products", "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "products", "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,  # или True под твою схему
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )

def downgrade() -> None:
    op.alter_column("products", "updated_at", existing_type=sa.DateTime(timezone=True), type_=sa.DateTime(), existing_nullable=False)
    op.alter_column("products", "created_at", existing_type=sa.DateTime(timezone=True), type_=sa.DateTime(), existing_nullable=False)
    op.alter_column("users", "updated_at", existing_type=sa.DateTime(timezone=True), type_=sa.DateTime(), existing_nullable=False)
    op.alter_column("users", "created_at", existing_type=sa.DateTime(timezone=True), type_=sa.DateTime(), existing_nullable=False)
