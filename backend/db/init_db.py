from psycopg2 import connect
from psycopg2.errors import DuplicateDatabase
from psycopg2.extensions import connection as Connection

# --- Internal imports ---
from core.config import settings


def create_db():
    print("Creating database...")
    connection = connect(settings.INITIAL_DATABASE_URL)
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE my_kitchen_accountant")
        print("Database created successfully.")
    except DuplicateDatabase:
        print("Database already exists.")
    finally:
        cursor.close()
        connection.close()


def create_tables(connection: Connection):
    print("Creating tables...")
    with connection.cursor() as cursor:
        cursor.execute(open("db/schema.sql", "r").read())   
    print("Tables created successfully.") 


def seed_data(connection: Connection):
    print("Seeding data...")
    with connection.cursor() as cursor:
        cursor.execute(open("db/seeds.sql", "r").read())
    print("Data seeded successfully.")


def init_db():
    create_db()

    connection = connect(settings.DATABASE_URL)
    connection.autocommit = True

    try:
        create_tables(connection)
        seed_data(connection)
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        connection.close()