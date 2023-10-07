import bootstrap

db = bootstrap.DB().getInstance()



async def create_table_users(conn):
    sql = """ 
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR NOT NULL,
        username VARCHAR NOT NULL,
        premium boolean NOT NULL DEFAULT FALSE,
        premium_time DATE,
        active_time DATE DEFAULT now(),
        reg_date DATE DEFAULT now(),
        winrate integer NOT NULL DEFAULT 0,
        win integer NOT NULL DEFAULT 0,
        lose integer NOT NULL DEFAULT 0,
        elo INT NOT NULL DEFAULT 500,
        reffer_id VARCHAR default NULL,
        balance integer NOT NULL default 0,
        PRIMARY KEY (id)
    );
    """
    await conn.execute(sql)


async def create_table_partners(conn):
    sql = """ 
    CREATE TABLE IF NOT EXISTS games_history (
        w VARCHAR NOT NULL,
        b VARCHAR NOT NULL,
        history VARCHAR NOT NULL,
        date DATE NOT NULL DEFAULT now()
    );
    """
    await conn.execute(sql)


async def run():
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            await create_table_users(conn)
            await create_table_partners(conn)