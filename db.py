import asyncpg

async def create_pool(db_url):
    return await asyncpg.create_pool(dsn=db_url)

async def register_opening_balance(conn, seller_id, today, amount):
    await conn.execute(
        """
        INSERT INTO cash_register (seller_id, date, opening_balance, total_sales, total_expenses)
        VALUES ($1, $2, $3, 0, 0)
        ON CONFLICT (seller_id, date) DO NOTHING
        """, seller_id, today, amount
    )

async def update_cash_sales(conn, seller_id, today, amount):
    await conn.execute(
        """
        UPDATE cash_register
        SET total_sales = total_sales + $1
        WHERE seller_id=$2 AND date=$3
        """, amount, seller_id, today
    )

async def update_cash_expenses(conn, seller_id, today, amount):
    await conn.execute(
        """
        UPDATE cash_register
        SET total_expenses = total_expenses + $1
        WHERE seller_id=$2 AND date=$3
        """, amount, seller_id, today
    )

async def get_cash_info(conn, seller_id, today):
    return await conn.fetchrow(
        """
        SELECT opening_balance, total_sales, total_expenses,
               (opening_balance + total_sales - total_expenses) AS current_balance
        FROM cash_register
        WHERE seller_id=$1 AND date=$2
        """, seller_id, today
    )

async def add_product(conn, product_data):
    await conn.execute(
        """
        INSERT INTO products (brand, model, memory, battery, condition, imei, purchase_price, supplier_name, supplier_phone, is_sold)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, FALSE)
        """,
        product_data['brand'], product_data['model'], product_data['memory'],
        product_data['battery'], product_data['condition'], product_data['imei'],
        product_data['price'], product_data['supplier_name'], product_data['supplier_phone']
    )

async def mark_product_as_sold(conn, product_id):
    await conn.execute("UPDATE products SET is_sold=TRUE WHERE id=$1", product_id)

async def get_product_by_imei(conn, imei):
    return await conn.fetchrow("SELECT * FROM products WHERE imei=$1 AND is_sold=FALSE", imei)

async def get_stock_summary(conn):
    return await conn.fetch(
        """
        SELECT brand, model, memory, COUNT(*) as count
        FROM products
        WHERE is_sold=FALSE
        GROUP BY brand, model, memory
        """
    )

async def register_sale(conn, sale_data):
    await conn.execute(
        """
        INSERT INTO sales (product_id, sale_price, customer_name, customer_phone, sold_by_seller_id)
        VALUES ($1, $2, $3, $4, $5)
        """,
        sale_data['product_id'], sale_data['sale_price'],
        sale_data['customer_name'], sale_data['customer_phone'],
        sale_data['seller_id']
    )

async def add_expense(conn, amount, description, seller_id):
    await conn.execute(
        """
        INSERT INTO expenses (amount, description, seller_id)
        VALUES ($1, $2, $3)
        """, amount, description, seller_id
    )
