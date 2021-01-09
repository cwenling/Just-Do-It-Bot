import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(user="nuryqcnukhhtay",
                                  password="f898e8d7ad3c53f29763b0758498d07923068b506522eb80096577ca0f53d2c4",
                                  host="ec2-52-44-166-58.compute-1.amazonaws.com",
                                  port="5432",
                                  database="d3t932c9q69007")

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
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")