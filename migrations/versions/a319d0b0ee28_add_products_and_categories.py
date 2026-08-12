"""add products and categories

Revision ID: a319d0b0ee28
Revises: 
Create Date: 2026-08-08 15:51:13.566491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a319d0b0ee28'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------
    # 1. Create categories
    # -----------------------------
    op.create_table(
        "categories",
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("returnable", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("category_id"),
        sa.UniqueConstraint("name"),
    )

    # -----------------------------
    # 2. Create products
    # -----------------------------
    op.create_table(
        "products",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.category_id"],
        ),
        sa.PrimaryKeyConstraint("product_id"),
    )

    # -----------------------------
    # 3. Insert categories
    # -----------------------------
    categories = sa.table(
        "categories",
        sa.column("category_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("returnable", sa.Boolean),
    )

    op.bulk_insert(
        categories,
        [
            {
                "category_id": 1,
                "name": "Clothing",
                "returnable": True,
            },
            {
                "category_id": 2,
                "name": "Electronics",
                "returnable": True,
            },
            {
                "category_id": 3,
                "name": "Home",
                "returnable": True,
            },
        ],
    )

    # -----------------------------
    # 4. Insert existing products
    # -----------------------------
    products = sa.table(
        "products",
        sa.column("product_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("category_id", sa.Integer),
        sa.column("price", sa.Numeric),
    )

    op.bulk_insert(
        products,
        [
            {
                "product_id": 1,
                "name": "T-shirt",
                "category_id": 1,
                "price": 1299.99,
            },
            {
                "product_id": 2,
                "name": "Mechanical Keyboard",
                "category_id": 2,
                "price": 249.50,
            },
            {
                "product_id": 3,
                "name": "Logitech MX Master 3S",
                "category_id": 2,
                "price": 159.99,
            },
            {
                "product_id": 4,
                "name": "Samsung 55 Inch 4K TV",
                "category_id": 2,
                "price": 3499.00,
            },
            {
                "product_id": 5,
                "name": "Anker USB-C Charger",
                "category_id": 2,
                "price": 89.90,
            },
            {
                "product_id": 6,
                "name": "towel",
                "category_id": 3,
                "price": 799.00,
            },
        ],
    )

    # -----------------------------
    # 5. Add product_id to orders
    # -----------------------------
    op.add_column(
        "orders",
        sa.Column("product_id", sa.Integer(), nullable=True),
    )

    # -----------------------------
    # 6. Populate product_id
    # -----------------------------
    op.execute("""
        UPDATE orders
        SET product_id = products.product_id
        FROM products
        WHERE orders.products = products.name
    """)

    # -----------------------------
    # 7. Add Foreign Key
    # -----------------------------
    op.create_foreign_key(
        "fk_orders_product_id",
        "orders",
        "products",
        ["product_id"],
        ["product_id"],
    )

    # -----------------------------
    # 8. Make product_id NOT NULL
    # -----------------------------
    op.alter_column(
        "orders",
        "product_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # -----------------------------
    # 9. Remove old products column
    # -----------------------------
    op.drop_column("orders", "products")

    # -----------------------------
    # 10. Fix tickets primary key name
    # -----------------------------
    op.add_column(
        "tickets",
        sa.Column("ticket_id", sa.Integer(), nullable=True),
    )

    op.execute("""
        UPDATE tickets
        SET ticket_id = ticked_id
    """)

    op.alter_column(
        "tickets",
        "ticket_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_column("tickets", "ticked_id")

    # -----------------------------
    # 11. Existing FK columns
    # -----------------------------
    op.alter_column(
        "orders",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "tickets",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tickets', sa.Column('ticked_id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.alter_column('tickets', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('tickets', 'ticket_id')
    op.add_column('orders', sa.Column('products', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.alter_column('orders', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('orders', 'product_id')
    op.drop_table('products')
    op.drop_table('categories')
    # ### end Alembic commands ###
