import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(user="postgres2",
                                  password="botbotbot",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="botdb")

    cursor = connection.cursor()

    q = """DROP TABLE tasks"""
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
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")