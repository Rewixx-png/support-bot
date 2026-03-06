import aiosqlite
from config import DB_PATH

class Database:
    def __init__(self, path=DB_PATH):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_topic_id INTEGER,
                    owner_topic_id INTEGER,
                    status TEXT DEFAULT 'open'
                )
            """)
            await db.commit()

    async def create_ticket(self, user_id: int, user_topic_id: int, owner_topic_id: int) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "INSERT INTO tickets (user_id, user_topic_id, owner_topic_id) VALUES (?, ?, ?)",
                (user_id, user_topic_id, owner_topic_id)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_ticket(self, ticket_id: int) -> dict:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def close_ticket(self, ticket_id: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,))
            await db.commit()

db = Database()