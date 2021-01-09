import psycopg2
import config

from psycopg2 import Error

try:
    connection = psycopg2.connect(user="nuryqcnukhhtay",
                                  password=config.postgres_password,
                                  host=config.postgres_host,
                                  port="5432",
                                  database=config.postgres_database)

    cursor = connection.cursor()

    q = """DROP TABLE IF EXISTS tasks"""
    cursor.execute(q)
    connection.commit()
    print("Table dropped successfully in PostgreSQL ")

    # SQL query to create a new table
    create_table_query = '''CREATE TABLE IF NOT EXISTS tasks
              (USERID    TEXT                NOT NULL,
               NAME      TEXT                NOT NULL,
               DEADLINE  TEXT); '''
    # Execute a command: this creates a new table
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")


except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")