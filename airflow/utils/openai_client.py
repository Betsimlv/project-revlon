from openai import OpenAI
from airflow.models import Variable
import logging

logger = logging.getLogger(__name__)
def get_openai_client():
    """Configura y retorna el cliente de OpenAI"""
    API_KEY = Variable.get('API_KEY')
    logger.info(f'API_KEY SELECCIONADA {API_KEY}')

    return OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")