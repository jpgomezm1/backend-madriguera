"""empty message

Revision ID: 08f999c620ca
Revises: 8482e599648c
Create Date: 2024-04-28 12:20:30.698443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08f999c620ca'
down_revision = '8482e599648c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pedido', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comprobante_pago', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pedido', schema=None) as batch_op:
        batch_op.drop_column('comprobante_pago')

    # ### end Alembic commands ###
