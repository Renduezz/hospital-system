"""
=============================================================
MÓDULO: CONEXIÓN Y CONSULTAS A POSTGRESQL (SUPABASE)
=============================================================
"""

import psycopg2
import pandas as pd
import streamlit as st


POSTGRES_CONFIG = {
    "host":     "aws-1-us-west-2.pooler.supabase.com",
    "port":     5432,
    "database": "postgres",
    "user":     "postgres.hnyirvighntyxijokuvk",
    "password": "cZPoPmROhYNF9KEo",
}


def conectar_sqlserver():
    try:
        conexion = psycopg2.connect(
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            database=POSTGRES_CONFIG["database"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            sslmode="require",
            connect_timeout=10,
        )
        return conexion
    except Exception as e:
        st.error(f"Error de conexión a PostgreSQL (Supabase): {e}")
        return None


def consultar_vista_citas():
    conn = conectar_sqlserver()
    if conn is None:
        return None
    try:
        query = "SELECT * FROM vw_citas_detalle ORDER BY id_cita"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error al consultar la vista de citas: {e}")
        return None
    finally:
        conn.close()


def consultar_vista_medicos():
    conn = conectar_sqlserver()
    if conn is None:
        return None
    try:
        query = "SELECT * FROM vw_medicos_especialidad_sede ORDER BY id_medico"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error al consultar la vista de médicos: {e}")
        return None
    finally:
        conn.close()


def consultar_vista_pacientes_habitaciones():
    conn = conectar_sqlserver()
    if conn is None:
        return None
    try:
        query = "SELECT * FROM vw_pacientes_habitaciones ORDER BY paciente"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error al consultar la vista de pacientes y habitaciones: {e}")
        return None
    finally:
        conn.close()


def ejecutar_procedimiento_citas_por_medico(id_medico: int):
    conn = conectar_sqlserver()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sp_citas_por_medico(%s)", (id_medico,))
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        df = pd.DataFrame(filas, columns=columnas)
        return df
    except Exception as e:
        st.error(f"Error al ejecutar sp_citas_por_medico: {e}")
        return None
    finally:
        conn.close()


def ejecutar_funcion_total_citas_paciente(id_paciente: int):
    conn = conectar_sqlserver()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT fn_total_citas_paciente(%s)", (id_paciente,))
        fila = cursor.fetchone()
        if fila:
            return fila[0]
        return 0
    except Exception as e:
        st.error(f"Error al ejecutar fn_total_citas_paciente: {e}")
        return None
    finally:
        conn.close()


def consultar_join_avanzado(nombre_consulta: str):
    conn = conectar_sqlserver()
    if conn is None:
        return None

    consultas = {
        "Citas por estado (GROUP BY)": """
            SELECT
                estado          AS "Estado",
                COUNT(*)        AS "Total Citas"
            FROM cita
            GROUP BY estado
            ORDER BY "Total Citas" DESC
        """,
        "Pacientes con su historial y tratamiento (JOIN múltiple)": """
            SELECT
                p.nombre || ' ' || p.apellido  AS "Paciente",
                hm.diagnostico                 AS "Diagnóstico",
                t.nombre                       AS "Tratamiento",
                hm.fecha                       AS "Fecha"
            FROM historial_medico hm
            JOIN paciente    p ON p.id_paciente    = hm.id_paciente
            JOIN tratamiento t ON t.id_tratamiento = hm.id_tratamiento
            ORDER BY hm.fecha
        """,
        "Médicos y cantidad de citas atendidas (GROUP BY + JOIN)": """
            SELECT
                m.nombre                  AS "Médico",
                e.nombre                  AS "Especialidad",
                COUNT(c.id_cita)          AS "Citas Atendidas"
            FROM medico m
            JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            LEFT JOIN cita    c ON c.id_medico = m.id_medico
                               AND c.estado = 'Atendida'
            GROUP BY m.nombre, e.nombre
            ORDER BY "Citas Atendidas" DESC
        """,
    }

    try:
        sql = consultas.get(nombre_consulta, "SELECT 1")
        df = pd.read_sql(sql, conn)
        return df
    except Exception as e:
        st.error(f"Error al ejecutar la consulta avanzada: {e}")
        return None
    finally:
        conn.close()
