import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.database import insertar_registro
from utils.text_proccesing import tupla_categorys
from utils.openai_client import get_openai_client
from airflow.models import Variable
import logging

logger = logging.getLogger(__name__)
conn_params = Variable.get('conn_params', deserialize_json=True)

def procesar_fila(fila, idx, client, valor_variable,prompt_seleccionado, query):
    """
    Procesa una fila individual de comentario:
    - Llama a la API según el tipo de procesamiento
    - Inserta el resultado en la tabla correspondiente
    """
    try:
        
 
        id_comments = fila.iloc[0]
        comentario = fila.iloc[1]
        
        
        if pd.isna(comentario) or not isinstance(comentario, str):
            return idx, 'SIN CATEGORIA'
        
        # Realizar llamada a la API
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": f'''{valor_variable}:{comentario}'''}
            ],
            temperature=0,
        )

        
        registro = completion.choices[0].message.content.strip()
        
     
        # Insertar según el tipo de procesamiento
        if prompt_seleccionado == 'categorys':
            tupla = tupla_categorys(registro, int(id_comments))
            logger.info(f'TUPLA {tupla}')
            datos = [tupla]
            
            logger.info(f'DATOS EN TUPLA {datos}')
            insert_query = query['tables']["categorys"]
            data_insert(datos, insert_query, conn_params)
        
        elif prompt_seleccionado == 'sentiments':
            
            datos = [(int(id_comments), registro)]
            insert_query = query['tables']["sentiments"]
            data_insert(datos, insert_query, conn_params)
            
        elif prompt_seleccionado == 'traslate':
            datos = [(int(id_comments), registro)]
            insert_query = query['tables']["traslate"]
            data_insert(datos, insert_query, conn_params)
        
        return idx, registro
        
    except Exception as e:
        logger.error(f"Error procesando fila {idx}: {e}")
        return idx, 'ERROR'

def procesar_lote_comentarios(df_lote, prompt_seleccionado, valor_variable):
    """
    Procesa un lote completo de comentarios usando ThreadPoolExecutor
    """
    client = get_openai_client()
    df_lote[prompt_seleccionado] = None
    query = Variable.get('query', deserialize_json=True)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for idx in df_lote.index:
            fila = df_lote.loc[idx]
            future = executor.submit(procesar_fila, fila, idx, client, valor_variable, prompt_seleccionado, query)
            futures.append(future)
        
        for future in as_completed(futures):
            idx, categoria = future.result()
            df_lote.at[idx, prompt_seleccionado] = categoria
    
    return 