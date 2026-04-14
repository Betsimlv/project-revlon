import json
import re

def limpiar_respuesta_json(respuesta):
    """
    Limpia una respuesta cruda de API eliminando markdown y formato JSON
    """
    respuesta_limpia = respuesta.strip()
    respuesta_limpia = re.sub(r'^```json\s*', '', respuesta_limpia)
    respuesta_limpia = re.sub(r'^```\s*', '', respuesta_limpia)
    respuesta_limpia = re.sub(r'\s*```$', '', respuesta_limpia)
    return respuesta_limpia

def parsear_json_seguro(respuesta):
    """
    Intenta parsear JSON de forma segura, retorna None si falla
    """
    try:
        return json.loads(respuesta)
    except json.JSONDecodeError:
        return None

def tupla_categorys(respuesta, id_comments):
    """
    Convierte una respuesta cruda de la API en una tupla para insertar en PostgreSQL
    """
    respuesta_limpia = limpiar_respuesta_json(respuesta)
    datos = parsear_json_seguro(respuesta_limpia)
    
    if not datos:
        return (id_comments, None, "", "", "", None, "", None, None, "", None, None, "", "", "")
    
    # Función auxiliar para convertir a booleano
    def convertir_booleano(valor):
        if valor is None:
            return None
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, str):
            valor_lower = valor.lower()
            if valor_lower in ['true', 'verdadero', 'sí', 'si', 'yes', '1']:
                return True
            elif valor_lower in ['false', 'falso', 'no', '0']:
                return False
        return None
    
    return (
        id_comments,
        convertir_booleano(datos.get("buena_difuminacion")),
        datos.get("aplicacion", ""),
        datos.get("textura", ""),
        datos.get("aroma", ""),
        datos.get("comparacion", ""),
        convertir_booleano(datos.get("buena_cobertura")),
        datos.get("tipo_piel", ""),
        convertir_booleano(datos.get("tono_piel")),
        convertir_booleano(datos.get("pigmentacion_conforme")),
        datos.get("efecto_estetico", ""),
        convertir_booleano(datos.get("precio_conforme")),
        convertir_booleano(datos.get("recomendacion")),
        datos.get("caracteristica_favorable", ""),
        datos.get("envase", "")
    )