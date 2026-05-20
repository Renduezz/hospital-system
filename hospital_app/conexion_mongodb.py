"""
=============================================================
MÓDULO: CONEXIÓN Y CONSULTAS A MONGODB ATLAS
=============================================================
"""

from pymongo import MongoClient
import streamlit as st


MONGO_URL = (
    "mongodb+srv://nesp:nesp1234"
    "@clusterdbhospitalario.nifcbm9.mongodb.net/"
    "?appName=ClusterDBhospitalario"
)

MONGO_BASE_DATOS = "hospitalDB"
MONGO_COLECCION_PACIENTES = "pacientes"


def conectar_mongodb():
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except Exception as e:
        st.error(f"Error de conexión a MongoDB Atlas: {e}")
        return None


def _obtener_coleccion():
    client = conectar_mongodb()
    if client is None:
        return None, None
    db = client[MONGO_BASE_DATOS]
    coleccion = db[MONGO_COLECCION_PACIENTES]
    return client, coleccion


def obtener_todos_los_pacientes():
    client, coleccion = _obtener_coleccion()
    if coleccion is None:
        return None
    try:
        resultados = list(coleccion.find({}))
        return resultados
    except Exception as e:
        st.error(f"Error al obtener pacientes de MongoDB: {e}")
        return None
    finally:
        client.close()


def buscar_paciente_por_nombre(nombre: str):
    client, coleccion = _obtener_coleccion()
    if coleccion is None:
        return None
    try:
        resultados = list(coleccion.find({"nombre": nombre}))
        return resultados
    except Exception as e:
        st.error(f"Error al buscar paciente por nombre: {e}")
        return None
    finally:
        client.close()


def buscar_pacientes_por_rango_id(id_min: int, id_max: int):
    client, coleccion = _obtener_coleccion()
    if coleccion is None:
        return None
    try:
        filtro = {"_id": {"$gte": id_min, "$lte": id_max}}
        resultados = list(coleccion.find(filtro))
        return resultados
    except Exception as e:
        st.error(f"Error al buscar pacientes por rango de ID: {e}")
        return None
    finally:
        client.close()


def buscar_pacientes_por_nombres(nombres: list):
    client, coleccion = _obtener_coleccion()
    if coleccion is None:
        return None
    try:
        filtro = {"nombre": {"$in": nombres}}
        resultados = list(coleccion.find(filtro))
        return resultados
    except Exception as e:
        st.error(f"Error al buscar pacientes por lista de nombres: {e}")
        return None
    finally:
        client.close()
