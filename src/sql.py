import psycopg2
from utils import constants as cs
import pandas as pd


def create_connection():
    conn = psycopg2.connect(
        dbname=cs.dbname,
        user=cs.user,
        password=cs.password,
        host=cs.host
    )
    return conn

def execute_query(conn, query):
    df = pd.read_sql_query(query, conn)
    print("Query executed successfully")
    return df






