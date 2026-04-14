from datetime import datetime
import pandas as pd
import psycopg2
import os
import sys
import logging

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.sdk.definitions.param import Param

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.database import get_db_connection
from utils.comment_processor import procesar_lote_comentarios

logger = logging.getLogger(__name__)
conn_params = Variable.get("conn_params", deserialize_json=True)
query_get_comments = Variable.get("query_get_comments")
CANTIDAD_LOTES = 3


@task
def get_comments():
    """Obtiene los comentarios de la tabla product_comments_new"""
    try:
        with get_db_connection(conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query_get_comments)
                rows = cursor.fetchall()

                # Obtener nombres de columnas
                colnames = [desc[0] for desc in cursor.description]
                comentarios = [dict(zip(colnames, row)) for row in rows]

                total_comentarios = len(comentarios)
                print(
                    f"{total_comentarios} Comentarios encontrados en la base de datos"
                )

                # Dividir  en 3 lotes
                tamano_lote = (
                    total_comentarios + CANTIDAD_LOTES - 1
                ) // CANTIDAD_LOTES  

                lotes = []
                for i in range(0, total_comentarios, tamano_lote):
                    lote = comentarios[i : i + tamano_lote]
                    lotes.append(
                        {
                            "lote_numero": len(lotes) + 1,
                            "registros": lote,
                            "cantidad": len(lote),
                        }
                    )

                print(
                    f"Divididos en {len(lotes)} lotes (tamaño promedio: {tamano_lote} comentarios)"
                )
                for lote in lotes:
                    print(
                        f"  - Lote {lote['lote_numero']}: {lote['cantidad']} comentarios"
                    )

                return lotes

    except Exception as e:
        logger.error(f"Error al consultar o dividir comentarios: {e}")
        raise


@task
def categorizar_lote(info_lote: dict, **context):
    """Procesa un lote de comentarios usando Dynamic Task Mapping"""
    df_lote = pd.DataFrame(info_lote["registros"])
    num_lote = info_lote["lote_numero"]
    cantidad = info_lote["cantidad"]

    params = context["params"]
    prompt_seleccionado = params.get("prompt_seleccionado", "sentiments")
    valor_variable = Variable.get(prompt_seleccionado)

    logger.info(
        f"Iniciando procesamiento del Lote {num_lote} con {cantidad} comentarios"
    )

    procesar_lote_comentarios(df_lote, prompt_seleccionado, valor_variable)

    logger.info(f"Lote {num_lote} procesado exitosamente")

    # Retornar metadata del lote procesado
    return logger.info("EJECUTADA LA CATEGORIZACIÓN")


# Definición del DAG
with DAG(
    dag_id="comments_category",
    schedule=None,
    catchup=False,
    params={
        "prompt_seleccionado": Param(
            default="sentiments",
            type="string",
            title="Prompts disponibles",
            description="Selecciona el prompt que quieres utilizar para categorizar",
            enum=["sentiments", "traduccion", "categorys"],
            values_display={
                "sentiments": "Categorización de Sentimientos de las Publicaciones",
                "traduccion": "Traducción del texto de ingles a Español",
                "categorys": "Categorización para los productos revlon",
            },
        )
    },
) as dag:
    # Obtener comentarios y dividir en 3 lotes
    lotes = get_comments()

    # Dynamic Task Mapping: Airflow crea automáticamente 3 tareas (una por cada lote)
    resultados = categorizar_lote.expand(info_lote=lotes)

    # Definir dependencias
    lotes >> resultados
