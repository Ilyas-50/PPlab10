import psycopg2
import csv

# Прямо здесь прописываем настройки подключения
DB_NAME = "phonebook_db"
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

def create_table():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50),
                    phone VARCHAR(20)
                )
            """)
        conn.commit()

def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)", (name, phone))
        conn.commit()

def insert_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        with connect() as conn:
            with conn.cursor() as cur:
                for row in reader:
                    cur.execute("INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)", (row[0], row[1]))
            conn.commit()

def update_user():
    name = input("Enter name to update: ")
    new_phone = input("Enter new phone: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE phonebook SET phone = %s WHERE first_name = %s", (new_phone, name))
        conn.commit()

def query_all():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM phonebook")
            rows = cur.fetchall()
            for row in rows:
                print(row)

def delete_user():
    name = input("Enter name to delete: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM phonebook WHERE first_name = %s", (name,))
        conn.commit()

def menu():
    create_table()
    while True:
        print("\n1. Add from console")
        print("2. Add from CSV")
        print("3. Update user")
        print("4. Show all")
        print("5. Delete user")
        print("6. Exit")

        choice = input("Enter choice: ")
        if choice == "1":
            insert_from_console()
        elif choice == "2":
            insert_from_csv(input("Enter CSV file path: "))
        elif choice == "3":
            update_user()
        elif choice == "4":
            query_all()
        elif choice == "5":
            delete_user()
        elif choice == "6":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    menu()
