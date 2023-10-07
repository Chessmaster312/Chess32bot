import datetime
import math
from typing import Union

import asyncpg
from asyncpg.pool import Pool


class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool: Union[Pool, None] = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    @staticmethod
    def formar_args(sql, parameters: dict):
        sql += ' AND '.join([
            f'{item} = ${num}' for num, item in enumerate(parameters, start=1)
        ])
        return sql, tuple(parameters.values())

    async def get_top_10_active_users(self):
        sql = """
        SELECT *
        FROM users
        WHERE active_time >= CURRENT_DATE - INTERVAL '7 days' AND (premium = true OR balance = 10)
        ORDER BY winrate DESC
        LIMIT 10;
        """
        return await self.pool.fetch(sql)

    async def get_last_10_games(self, user_id):
        sql = """
        SELECT date, 'w' AS side, history
        FROM games_history
        WHERE w = $1
        UNION ALL
        SELECT date, 'b' AS side, history
        FROM games_history
        WHERE b = $1
        ORDER BY date DESC
        LIMIT 10;
        """
        return await self.pool.fetch(sql, user_id)

    async def check_premium(self, user_id):
        # Сначала обновляем статус подписки, если необходимо
        update_sql = """
        UPDATE users
        SET premium = FALSE
        WHERE id = $1 AND premium = TRUE AND premium_time < CURRENT_DATE;
        """
        await self.pool.execute(update_sql, user_id)

        # Затем выполняем запрос для проверки подписки
        check_sql = """
        SELECT EXISTS (
            SELECT 1
            FROM users
            WHERE id = $1 AND premium = TRUE AND premium_time >= CURRENT_DATE
        );
        """
        result = await self.pool.fetchval(check_sql, user_id)
        return result

    async def get_user(self, user_id):
        sql = """
        SELECT *
        FROM users
        WHERE id = $1
        """
        return await self.pool.fetchrow(sql, user_id)

    async def get_all_ref_week(self):
        sql = """
        SELECT
        COUNT(*) 
        AS count
        FROM users
        WHERE reg_date >= CURRENT_DATE - INTERVAL '7 days' AND reffer_id IS NOT NULL
        """
        return await self.pool.fetchval(sql)

    async def add_user(self, user_id, username, reffer_id=None):
        sql = """
        DELETE FROM users
        WHERE id = $1
        """
        await self.pool.execute(sql, user_id)
        sql = """
        INSERT INTO users (id, username, reffer_id)
        VALUES ($1, $2, $3)
        ON CONFLICT (id) DO NOTHING
        RETURNING id, username, reffer_id
        """
        return await self.pool.fetchrow(sql, user_id,username,reffer_id)

    async def add_balance(self, user_id):
        sql = "UPDATE users SET balance = balance + 5  WHERE id = ($1)"
        await self.pool.execute(sql, user_id)

    async def add_premium(self, user_id):
        sql = "UPDATE users SET premium = TRUE, premium_time = now() + interval '1 month' WHERE id = ($1)"
        await self.pool.execute(sql, user_id)

    async def count_ref(self, user_id):
        sql = "SELECT COUNT(*) AS count FROM users WHERE reffer_id = ($1)"
        return await self.pool.fetchval(sql, user_id)
    async def games_count(self, ):
        sql = "SELECT COUNT(*) AS count FROM games_history"
        return await self.pool.fetchval(sql,)
    async def add_game_history(self, w, b, history):
        sql = """INSERT INTO games_history (w, b, history) VALUES ($1, $2, $3) """
        return await self.pool.execute(sql, w, b, history)

    async def update_users_stats(self, winner_id, loser_id, k_factor=32):
            # Step 1: Retrieve Elo ratings for winner and loser
            sql = """
            SELECT *
            FROM users
            WHERE id IN ($1, $2);
            """
            elo_results = await self.pool.fetch(sql, winner_id, loser_id)
            winner_elo, loser_elo = elo_results[0]['elo'], elo_results[1]['elo']
            k_factor_w, k_factor_l = elo_results[0]['winrate'], elo_results[1]['winrate']
            # Step 2: Calculate the expected scores for the winner and loser

            expected_score_winner = 1 / (1 + math.pow(10, (loser_elo - winner_elo) / 400))
            expected_score_loser = 1 - expected_score_winner

            # Step 3: Calculate the actual scores (1 for winner, 0 for loser)
            score_winner = 1
            score_loser = 0

            # Step 4: Update the Elo ratings for both the winner and loser
            winner_new_elo = winner_elo + k_factor * (score_winner - expected_score_winner)
            loser_new_elo = loser_elo + k_factor * (score_loser - expected_score_loser)

            # Perform the updates in a transaction to ensure data consistency
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    update_winner_sql = """
                    UPDATE users
                    SET elo = $1, win = win + 1,
                        winrate = (win + 1) * 100 / (win + 1 + lose),
                        active_time = now()
    
                    WHERE id = $2;
                    """
                    update_loser_sql = """
                    UPDATE users
                    SET elo = $1, lose = lose + 1,
                        winrate = (win + 1) * 100 / (win + 1 + lose),
                        active_time = now()
                    WHERE id = $2;
                    """

                    await conn.execute(update_winner_sql, winner_new_elo, winner_id)
                    await conn.execute(update_loser_sql, loser_new_elo, loser_id)

            return

    async def delete_partner(self, number: str) -> bool:
        sql = """DELETE FROM partners WHERE number = $1 RETURNING 1"""
        result = await self.pool.fetchval(sql, number)
        return bool(result)

    async def update_user(self, user_id: str, bio: str, number: str):
        sql = "UPDATE users SET bio = ($2), number = ($3) WHERE id = ($1)"
        await self.pool.execute(sql, user_id, bio, number)

    async def update_order_status(self, order_id: str, status: str):
        sql = "UPDATE orders SET status = ($2) WHERE order_id = ($1)"
        await self.pool.fetchrow(sql, order_id, status)

    async def check_number_in_partners(self, user_id: str) -> bool:
        sql = """
            SELECT EXISTS(
                SELECT 1
                FROM partners
                WHERE number = (SELECT number FROM users WHERE id = $1)
            )
        """
        result = await self.pool.fetchval(sql, user_id)
        return bool(result)

    async def get_all_user_ids(self, ):
        sql = "SELECT id FROM users"
        return await self.pool.fetch(sql, )

    async def get_order(self, order_id: str):
        sql = """
            SELECT o.*, u.*
            FROM orders AS o
            JOIN users AS u ON o.user_id = u.id
            WHERE o.order_id = $1
            """
        return await self.pool.fetchrow(sql, order_id)

    async def create_order(self, order_id: str, user_id: str, product: str, pvz: str, delivery: str, cost: int,
                           count: int):
        sql = """
            WITH inserted_order AS (
                INSERT INTO orders (order_id, user_id, product, pvz, delivery, cost, count) 
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (order_id) DO UPDATE 
                SET user_id = EXCLUDED.user_id, 
                product = EXCLUDED.product, 
                pvz = EXCLUDED.pvz, 
                delivery = EXCLUDED.delivery, 
                cost = EXCLUDED.cost, 
                count = EXCLUDED.count 
                RETURNING *
            )
            SELECT io.*, u.*
            FROM inserted_order AS io
            JOIN users AS u ON io.user_id = u.id
        """
        return await self.pool.fetchrow(sql, order_id, user_id, product, pvz, delivery, cost, count)

    async def get_post_by_url(self, url: str):
        sql = "SELECT * FROM posts WHERE url = ($1)"
        return await self.pool.fetch(sql, url)

    async def set_post_user(self, user_id: int, post_id: int):
        sql = "UPDATE users SET post_id = ($2) WHERE id = ($1)"
        await self.pool.execute(sql, user_id, post_id)

    async def check_user(self, id: str):
        sql = "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)"
        return await self.pool.fetchval(sql, id)

    async def delete_post(self, url: str):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                sql_delete = "DELETE FROM posts WHERE url = ($1) RETURNING *"
                result = await conn.fetchrow(sql_delete, url)
                deleted_id = result["id"]
                sql_update = "UPDATE posts SET id = id - 1 WHERE id > $1"
                await conn.execute(sql_update, deleted_id)
                sql_max_id = "SELECT MAX(id) FROM posts"
                max_id = await conn.fetchval(sql_max_id)
                if not max_id:
                    sql_reset_sequence = "ALTER SEQUENCE posts_id_seq RESTART WITH 1"
                    await conn.execute(sql_reset_sequence)
                else:
                    sql_reset_sequence = "SELECT SETVAL('posts_id_seq', $1)"
                    await conn.fetchval(sql_reset_sequence, max_id)
                return result

    async def get_post(self, post_id: int):
        sql = "SELECT * FROM posts WHERE id = ($1)"
        return await self.pool.fetch(sql, post_id, )

    async def add_post(self, text: str, path: str, url: str):
        sql = """
        INSERT INTO posts (text, path, url)
        VALUES ($1, $2, $3)
        ON CONFLICT (path,url) DO NOTHING
        RETURNING TRUE
        """
        return await self.pool.fetchrow(sql, text, path, url)

    async def likes_post(self, post_id: int):
        sql = "UPDATE posts SET likes = likes + 1 WHERE id = ($1)"
        return await self.pool.fetchrow(sql, post_id)

    async def dislikes_post(self, post_id: int):
        sql = "UPDATE posts SET dislikes = dislikes + 1 WHERE id = ($1)"
        return await self.pool.fetchrow(sql, post_id)

    async def count_users(self):
        return await self.pool.fetchval("SELECT COUNT(*) FROM users")

    async def get_users(self, **kwargs):
        sql = "SELECT id FROM users"
        return await self.pool.fetch(sql)
