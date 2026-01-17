import aiosqlite
from aiogram import Router
from main import bot, admin_id

router = Router()

async def init_db():
    async with aiosqlite.connect('dbs/file.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         buyer_id INTEGER NOT NULL,
                         buyer_username TEXT,
                         code_type TEXT,
                         tech_spec TEXT,
                         price REAL DEFAULT 0.0,
                         status TEXT DEFAULT 'payment_pending'
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY,
                         username TEXT,
                         subscribe_status TEXT DEFAULT 'false',
                         orders INTEGER DEFAULT 0,
                         total_spent REAL DEFAULT 0.0
            )
        ''')
        await db.commit()
        await db.commit()

async def create_order(buyer_id: int, buyer_username: str, code_type: str, tech_spec: str, price: float = 0.0):
    async with aiosqlite.connect('dbs/file.db') as db:
        await db.execute('''
            INSERT INTO orders (buyer_id, buyer_username, code_type, tech_spec, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (buyer_id, buyer_username, code_type, tech_spec, price))
        await db.commit()
        cursor = await db.execute('SELECT last_insert_rowid()')
        order_id = (await cursor.fetchone())[0]
        return order_id
    
async def cancel_order(order_id: int):
    async with aiosqlite.connect('dbs/file.db') as db:
        await db.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        await db.commit()

async def get_order(order_id: int):
    async with aiosqlite.connect('dbs/file.db') as db:
        cursor = await db.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = await cursor.fetchone()
        return order

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect('dbs/file.db') as db:
        if status not in ['payment_pending', 'in_progress', 'completed']:
            raise ValueError("Статус недопустим.")
        await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()

async def orders_list():
    async with aiosqlite.connect('dbs/file.db') as db:
        cursor = await db.execute('SELECT * FROM orders DESC LIMIT 10')
        orders = await cursor.fetchall()
        return orders

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect('dbs/file.db') as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (id, username)
            VALUES (?, ?)
        ''', (user_id, username))
        await db.commit()
    
async def get_user(user_id: int, username: str = None):
    async with aiosqlite.connect('dbs/file.db') as db:
        cursor = await db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = await cursor.fetchone()
        if not user:
            try:
                user = await bot.get_chat(user_id)
                username = user.username
                await add_user(user_id, username)
                cursor = await db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = await cursor.fetchone()
            except Exception as e:
                await bot.send_message(admin_id, f"Ошибка при получении данных пользователя {user_id}: {e}")

        return user

async def update_user_stats(user_id: int, orders_increment: int = 0, total_spent_increment: float = 0.0):
    async with aiosqlite.connect('dbs/file.db') as db:
        await db.execute('''
            UPDATE users
            SET orders = orders + ?, total_spent = total_spent + ?
            WHERE id = ?
        ''', (orders_increment, total_spent_increment, user_id))
        await db.commit()

async def get_statistics():
    async with aiosqlite.connect('dbs/file.db') as db:
        cursor = await db.execute('SELECT COUNT(*) FROM users')
        total_users = (await cursor.fetchone())[0]
        
        cursor = await db.execute('SELECT COUNT(*) FROM orders')
        total_orders = (await cursor.fetchone())[0]
        
        cursor = await db.execute('SELECT SUM(price) FROM orders WHERE status = "completed"')
        total_revenue = (await cursor.fetchone())[0] or 0.0
        
        return {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': total_revenue
        }
    
async def subscribe_checking(user_id: int):
    async with aiosqlite.connect('dbs/file.db') as db:
        cursor = await db.execute('SELECT subscribe_status FROM users WHERE id = ?', (user_id,))
        result = await cursor.fetchone()
        if result:
            return result[0] == 'true'
        return False

async def update_subscribe_status(user_id: int, status: str):
    async with aiosqlite.connect('dbs/file.db') as db:
        if status not in ['true', 'false']:
            raise ValueError("Статус подписки недопустим.")
        await db.execute('UPDATE users SET subscribe_status = ? WHERE id = ?', (status, user_id))
        await db.commit()