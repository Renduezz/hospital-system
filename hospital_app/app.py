"""
=============================================================
SISTEMA HOSPITALARIO - APLICACIÓN PRINCIPAL
=============================================================
Este archivo es el punto de entrada de la aplicación Streamlit.
Conecta con PostgreSQL (Supabase) y MongoDB para mostrar
información del sistema hospitalario.

Para ejecutar: streamlit run app.py
=============================================================
"""

import streamlit as st

from conexion_sqlserver import (
    conectar_sqlserver,
    consultar_vista_citas,
    consultar_vista_medicos,
    consultar_vista_pacientes_habitaciones,
    ejecutar_procedimiento_citas_por_medico,
    ejecutar_funcion_total_citas_paciente,
    consultar_join_avanzado,
)
from conexion_mongodb import (
    conectar_mongodb,
    obtener_todos_los_pacientes,
    buscar_paciente_por_nombre,
    buscar_pacientes_por_rango_id,
    buscar_pacientes_por_nombres,
)

st.set_page_config(
    page_title="Sistema Hospitalario",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏥 Sistema Hospitalario — HospitalDB")
st.markdown(
    "Aplicación que integra **PostgreSQL en Supabase** (datos relacionales) "
    "y **MongoDB Atlas** (historial médico documental)."
)
st.divider()

st.sidebar.title("📋 Menú de navegación")
seccion = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "🔌 Estado de conexiones",
        "📊 Vistas SQL Server",
        "⚙️ Procedimientos almacenados",
        "🔢 Funciones SQL Server",
        "🔗 Consultas avanzadas (JOIN/GROUP BY)",
        "🍃 MongoDB — Pacientes y Historial",
    ],
)

st.sidebar.divider()
st.sidebar.info(
    "Esta aplicación fue desarrollada como proyecto final de Bases de Datos II. "
    "Integra SQL Server y MongoDB en una sola interfaz."
)


# ─────────────────────────────────────────
# SECCIÓN 1: ESTADO DE CONEXIONES
# ─────────────────────────────────────────
if seccion == "🔌 Estado de conexiones":
    st.header("🔌 Estado de conexiones")
    st.markdown(
        "Aquí puedes verificar si la aplicación logra conectarse correctamente "
        "a ambas bases de datos."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("PostgreSQL (Supabase)")
        if st.button("Probar conexión PostgreSQL"):
            conn = conectar_sqlserver()
            if conn:
                st.success("✅ Conexión exitosa a PostgreSQL (Supabase)")
                conn.close()
            else:
                st.error("❌ No se pudo conectar a PostgreSQL. Revisa las credenciales en conexion_sqlserver.py")

    with col2:
        st.subheader("MongoDB")
        if st.button("Probar conexión MongoDB"):
            client = conectar_mongodb()
            if client:
                st.success("✅ Conexión exitosa a MongoDB")
                client.close()
            else:
                st.error("❌ No se pudo conectar a MongoDB. Revisa las credenciales en conexion_mongodb.py")


# ─────────────────────────────────────────
# SECCIÓN 2: VISTAS DE SQL SERVER
# ─────────────────────────────────────────
elif seccion == "📊 Vistas SQL Server":
    st.header("📊 Vistas de SQL Server")
    st.markdown(
        "Las vistas son consultas guardadas en PostgreSQL que simplifican "
        "el acceso a datos combinados de varias tablas."
    )

    vista = st.selectbox(
        "Selecciona la vista que deseas consultar:",
        [
            "Vista: Citas con paciente y médico",
            "Vista: Médicos con especialidad y sede",
            "Vista: Pacientes con habitación asignada",
        ],
    )

    if st.button("📥 Cargar vista"):
        with st.spinner("Consultando SQL Server..."):
            if vista == "Vista: Citas con paciente y médico":
                df = consultar_vista_citas()
                st.subheader("Vista: vw_Citas_Detalle")
                st.markdown("Muestra todas las citas con el nombre del paciente y el médico asignado.")
            elif vista == "Vista: Médicos con especialidad y sede":
                df = consultar_vista_medicos()
                st.subheader("Vista: vw_Medicos_Especialidad_Sede")
                st.markdown("Muestra cada médico junto con su especialidad y la sede donde trabaja.")
            else:
                df = consultar_vista_pacientes_habitaciones()
                st.subheader("Vista: vw_Pacientes_Habitaciones")
                st.markdown("Muestra los pacientes que tienen o tuvieron habitación asignada.")

            if df is not None and not df.empty:
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total de registros: {len(df)}")
            elif df is not None:
                st.warning("La vista no devolvió registros.")
            else:
                st.error("Error al consultar la vista. Verifica la conexión a SQL Server.")


# ─────────────────────────────────────────
# SECCIÓN 3: PROCEDIMIENTOS ALMACENADOS
# ─────────────────────────────────────────
elif seccion == "⚙️ Procedimientos almacenados":
    st.header("⚙️ Procedimientos almacenados")
    st.markdown(
        "En PostgreSQL los procedimientos se implementan como funciones que retornan tablas. "
        "Se ejecutan con parámetros desde la aplicación igual que un procedimiento almacenado."
    )

    st.subheader("SP: Obtener citas por médico")
    st.markdown("Ejecuta el procedimiento `sp_CitasPorMedico` que recibe el ID de un médico y devuelve sus citas.")

    id_medico = st.number_input(
        "Ingresa el ID del médico (1 al 15):",
        min_value=1,
        max_value=15,
        value=1,
        step=1,
    )

    if st.button("▶️ Ejecutar procedimiento"):
        with st.spinner("Ejecutando procedimiento almacenado..."):
            df = ejecutar_procedimiento_citas_por_medico(int(id_medico))
            if df is not None and not df.empty:
                st.success(f"Citas encontradas para el médico ID {id_medico}:")
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total de citas: {len(df)}")
            elif df is not None:
                st.warning(f"El médico con ID {id_medico} no tiene citas registradas.")
            else:
                st.error("Error al ejecutar el procedimiento. Verifica la conexión a SQL Server.")


# ─────────────────────────────────────────
# SECCIÓN 4: FUNCIONES SQL SERVER
# ─────────────────────────────────────────
elif seccion == "🔢 Funciones SQL Server":
    st.header("🔢 Funciones de SQL Server")
    st.markdown(
        "Las funciones escalares en PostgreSQL reciben parámetros y devuelven un valor calculado. "
        "Se usan directamente dentro de consultas SELECT igual que en SQL Server."
    )

    st.subheader("Función: Total de citas de un paciente")
    st.markdown("Usa la función `fn_TotalCitasPaciente(id_paciente)` para saber cuántas citas tiene un paciente.")

    id_paciente = st.number_input(
        "Ingresa el ID del paciente (1 al 15):",
        min_value=1,
        max_value=15,
        value=1,
        step=1,
        key="paciente_funcion",
    )

    if st.button("🔢 Calcular total de citas"):
        with st.spinner("Ejecutando función en SQL Server..."):
            total = ejecutar_funcion_total_citas_paciente(int(id_paciente))
            if total is not None:
                st.metric(
                    label=f"Total de citas del paciente ID {id_paciente}",
                    value=total,
                )
            else:
                st.error("Error al ejecutar la función. Verifica la conexión a SQL Server.")


# ─────────────────────────────────────────
# SECCIÓN 5: CONSULTAS AVANZADAS
# ─────────────────────────────────────────
elif seccion == "🔗 Consultas avanzadas (JOIN/GROUP BY)":
    st.header("🔗 Consultas avanzadas en SQL Server")
    st.markdown(
        "Estas consultas usan `JOIN`, `GROUP BY` y subconsultas para cruzar "
        "información de múltiples tablas en PostgreSQL (Supabase)."
    )

    consulta = st.selectbox(
        "Selecciona la consulta que deseas ejecutar:",
        [
            "Citas por estado (GROUP BY)",
            "Pacientes con su historial y tratamiento (JOIN múltiple)",
            "Médicos y cantidad de citas atendidas (GROUP BY + JOIN)",
        ],
    )

    if st.button("🔍 Ejecutar consulta"):
        with st.spinner("Ejecutando consulta avanzada..."):
            df = consultar_join_avanzado(consulta)
            if df is not None and not df.empty:
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total de registros: {len(df)}")
            elif df is not None:
                st.warning("La consulta no devolvió resultados.")
            else:
                st.error("Error al ejecutar la consulta. Verifica la conexión a SQL Server.")


# ─────────────────────────────────────────
# SECCIÓN 6: MONGODB
# ─────────────────────────────────────────
elif seccion == "🍃 MongoDB — Pacientes y Historial":
    st.header("🍃 MongoDB — Pacientes con historial médico")
    st.markdown(
        "MongoDB almacena los pacientes como **documentos embebidos**: "
        "cada paciente tiene su historial médico anidado dentro del mismo documento. "
        "Esto es complementario a la información relacional de SQL Server."
    )

    modo = st.radio(
        "¿Qué deseas hacer?",
        [
            "Ver todos los pacientes",
            "Buscar por nombre",
            "Buscar por rango de IDs",
            "Buscar varios nombres a la vez",
        ],
        horizontal=True,
    )

    st.divider()

    if modo == "Ver todos los pacientes":
        if st.button("📋 Cargar todos los pacientes"):
            with st.spinner("Consultando MongoDB..."):
                pacientes = obtener_todos_los_pacientes()
                if pacientes is not None:
                    st.success(f"Se encontraron {len(pacientes)} pacientes.")
                    for p in pacientes:
                        with st.expander(f"👤 {p.get('nombre')} {p.get('apellido')} (ID: {p.get('_id')})"):
                            historial = p.get("historial_medico", [])
                            if historial:
                                for h in historial:
                                    st.markdown(f"- **Diagnóstico:** {h.get('diagnostico')}  |  **Tratamiento:** {h.get('tratamiento')}")
                            else:
                                st.info("Sin historial médico registrado.")
                else:
                    st.error("Error al conectar con MongoDB.")

    elif modo == "Buscar por nombre":
        nombre = st.text_input("Escribe el nombre exacto del paciente:")
        if st.button("🔍 Buscar"):
            if nombre.strip():
                with st.spinner("Buscando en MongoDB..."):
                    pacientes = buscar_paciente_por_nombre(nombre.strip())
                    if pacientes is not None and len(pacientes) > 0:
                        for p in pacientes:
                            with st.expander(f"👤 {p.get('nombre')} {p.get('apellido')} (ID: {p.get('_id')})"):
                                historial = p.get("historial_medico", [])
                                for h in historial:
                                    st.markdown(f"- **Diagnóstico:** {h.get('diagnostico')}  |  **Tratamiento:** {h.get('tratamiento')}")
                    elif pacientes is not None:
                        st.warning(f"No se encontró ningún paciente con nombre '{nombre}'.")
                    else:
                        st.error("Error al conectar con MongoDB.")
            else:
                st.warning("Por favor escribe un nombre para buscar.")

    elif modo == "Buscar por rango de IDs":
        col1, col2 = st.columns(2)
        with col1:
            id_min = st.number_input("ID mínimo:", min_value=1, max_value=15, value=1)
        with col2:
            id_max = st.number_input("ID máximo:", min_value=1, max_value=15, value=5)

        if st.button("🔍 Buscar rango"):
            with st.spinner("Buscando en MongoDB..."):
                pacientes = buscar_pacientes_por_rango_id(int(id_min), int(id_max))
                if pacientes is not None and len(pacientes) > 0:
                    st.success(f"Se encontraron {len(pacientes)} pacientes en el rango {id_min}–{id_max}.")
                    for p in pacientes:
                        with st.expander(f"👤 {p.get('nombre')} {p.get('apellido')} (ID: {p.get('_id')})"):
                            historial = p.get("historial_medico", [])
                            for h in historial:
                                st.markdown(f"- **Diagnóstico:** {h.get('diagnostico')}  |  **Tratamiento:** {h.get('tratamiento')}")
                elif pacientes is not None:
                    st.warning(f"No se encontraron pacientes en el rango {id_min}–{id_max}.")
                else:
                    st.error("Error al conectar con MongoDB.")

    elif modo == "Buscar varios nombres a la vez":
        nombres_raw = st.text_area(
            "Escribe los nombres separados por coma (ej: Juan, Ana, Carlos):"
        )
        if st.button("🔍 Buscar múltiples"):
            nombres = [n.strip() for n in nombres_raw.split(",") if n.strip()]
            if nombres:
                with st.spinner("Buscando en MongoDB..."):
                    pacientes = buscar_pacientes_por_nombres(nombres)
                    if pacientes is not None and len(pacientes) > 0:
                        st.success(f"Se encontraron {len(pacientes)} resultados.")
                        for p in pacientes:
                            with st.expander(f"👤 {p.get('nombre')} {p.get('apellido')} (ID: {p.get('_id')})"):
                                historial = p.get("historial_medico", [])
                                for h in historial:
                                    st.markdown(f"- **Diagnóstico:** {h.get('diagnostico')}  |  **Tratamiento:** {h.get('tratamiento')}")
                    elif pacientes is not None:
                        st.warning("No se encontraron pacientes con esos nombres.")
                    else:
                        st.error("Error al conectar con MongoDB.")
            else:
                st.warning("Por favor escribe al menos un nombre.")
