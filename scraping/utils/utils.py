import psycopg2
from psycopg2 import sql, Error
from contextlib import contextmanager



@contextmanager
def get_db_connection(conn_params):
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        yield conn  
    finally:
        if conn:
            conn.close()
            
def get_ids(conn_params, tabla, columna, columna_es_igual):
    """Obtiene todos los product_link de la tabla collections"""
    
    try:
        with get_db_connection(conn_params) as conn:
            with conn.cursor() as cursor:  
                cursor.execute(f"SELECT id FROM {tabla} WHERE {columna} = '{columna_es_igual}'")
                id = [row[0] for row in cursor.fetchall()]
                
    except Error as e:
        print(f"Error al consultar links: {e}")
    
    return id

 
def data_insert(datos, insert_query, conn_params):
    """Inserta un registro en la tabla collections"""
    try:
        with get_db_connection(conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.executemany(insert_query, datos)
                conn.commit()
                print(f"Registros insertados correctamente. {len(datos)}")
                
    except Error as e:
        print(f"Error al insertar: {e}")
        
        
def safe_extract(elements, index, attribute='text', default=""):
    """Extrae datos de forma segura"""
    try:
        element = elements[index]
        if attribute == 'text':
            return element.text
        return element.get_attribute(attribute)
    except (IndexError, AttributeError):
        return (default)

