import psycopg2

DB_NAME = "snake_game"
DB_USER = "postgres"
DB_PASSWORD = "hello123"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def query_all():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_score.username, user_score.score FROM user_score ORDER BY score DESC;")
            rows = cur.fetchall()
            for row in rows:
                print(row)

query_all()
