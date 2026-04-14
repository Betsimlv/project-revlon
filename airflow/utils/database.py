import psycopg2
from psycopg2 import Error
from contextlib import contextmanager
import logging
import json

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection(conn_params):
    """Context manager para conexiones de base de datos"""
    conn = None
    try:
        if isinstance(conn_params, str):
            conn_params = json.loads(conn_params)
        conn = psycopg2.connect(**conn_params)
        yield conn  
    finally:
        if conn:
            conn.close()

def data_insert(datos, insert_query, conn_params):
    """Inserta un registro en la tabla especificada"""
    try:
        with get_db_connection(conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.executemany(insert_query, datos)
                conn.commit()
                print(f"Registros insertados correctamente. {len(datos)}")
    except Error as e:
        print(f"Error al insertar: {e}")