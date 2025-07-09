import asyncpg

# Создать пул подключений
async def create_pool(db_url):
    return await asyncpg.create_pool(dsn=db_url)

# Зарегистрировать начальный баланс кассы
async def register_opening_balance(conn, seller_id, date, opening_balance):
    await conn.execute("""
        INSERT INTO cash_register (seller_id, date, opening_balance, closing_balance, total_sales, total_expenses)
        VALUES ($1, $2, $3, $3, 0, 0)
    """, seller_id, date, opening_balance)

# Добавить товар
async def add_product(conn, product_data):
    await conn.execute("""
        INSERT INTO products (brand, model, memory, battery, condition, imei, purchase_price, supplier_name, supplier_phone, is_sold)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, FALSE)
    """, product_data['brand'], product_data['model'], product_data['memory'],
         product_data['battery'], product_data['condition'], product_data['imei'],
         product_data['price'], product_data['supplier_name'], product_data['supplier_phone'])

# Найти товар по IMEI
async def get_product_by_imei(conn, imei):
    return await conn.fetchrow("""
        SELECT * FROM products WHERE imei=$1 AND is_sold=FALSE
    """, imei)

# Отметить товар как проданный
async def mark_product_as_sold(conn, product_id):
    await conn.execute("""
        UPDATE products SET is_sold=TRUE WHERE id=$1
    """, product_id)

# Зарегистрировать продажу
async def register_sale(conn, sale_data):
    await conn.execute("""
        INSERT INTO sales (product_id, sale_price, customer_name, customer_phone, seller_id, sale_date)
        VALUES ($1, $2, $3, $4, $5, NOW())
    """, sale_data['product_id'], sale_data['sale_price'],
         sale_data['customer_name'], sale_data['customer_phone'], sale_data['seller_id'])

# Обновить кассу (продажи)
async def update_cash_sales(conn, seller_id, date, amount):
    await conn.execute("""
        UPDATE cash_register
        SET total_sales = total_sales + $3,
            closing_balance = closing_balance + $3
        WHERE seller_id=$1 AND date=$2
    """, seller_id, date, amount)

# Добавить расход
async def add_expense(conn, amount, description, seller_id):
    await conn.execute("""
        INSERT INTO expenses (amount, description, seller_id, expense_date)
        VALUES ($1, $2, $3, NOW())
    """, amount, description, seller_id)

# Обновить кассу (расходы)
async def update_cash_expenses(conn, seller_id, date, amount):
    await conn.execute("""
        UPDATE cash_register
        SET total_expenses = total_expenses + $3,
            closing_balance = closing_balance - $3
        WHERE seller_id=$1 AND date=$2
    """, seller_id, date, amount)

# Получить инфо по кассе
async def get_cash_info(conn, seller_id, date):
    return await conn.fetchrow("""
        SELECT opening_balance, total_sales, total_expenses, closing_balance AS current_balance
        FROM cash_register
        WHERE seller_id=$1 AND date=$2
    """, seller_id, date)

# Получить склад
async def get_stock_summary(conn):
    return await conn.fetch("""
        SELECT brand, model, memory, COUNT(*) AS count
        FROM products
        WHERE is_sold=FALSE
        GROUP BY brand, model, memory
    """)
