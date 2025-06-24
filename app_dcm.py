import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

# Cargar variables desde .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de página
st.set_page_config(page_title="Test de Elección Discreta", layout="centered")

# Control del flujo
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "consentimiento"
if "bloque" not in st.session_state:
    st.session_state.bloque = 1

# Pantalla 1: Consentimiento
if st.session_state.pantalla == "consentimiento":
    st.title("Test de Preferencias")
    st.info("Esta encuesta es anónima. Los datos se usan con fines académicos.")
    if st.button("Acepto participar"):
        st.session_state.pantalla = "datos"
        st.session_state.user_id = str(uuid.uuid4())
        st.experimental_rerun = None  # Eliminamos para evitar errores futuros
        st.query_params.clear()
        st._shown = False  # fuerza a Streamlit a mostrar la próxima pantalla

# Pantalla 2: Datos previos
elif st.session_state.pantalla == "datos":
    st.subheader("Datos sociodemográficos")
    edad = st.number_input("Edad", 15, 99)
    sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro", "Prefiero no decirlo"])
    nivel = st.selectbox("Nivel educativo", ["Secundario", "Terciario", "Universitario", "Posgrado"])
    if st.button("Iniciar encuesta"):
        st.session_state.datos = {
            "edad": edad,
            "sexo": sexo,
            "nivel": nivel
        }
        st.session_state.pantalla = "encuesta"

# Pantalla 3: Encuesta por bloques
elif st.session_state.pantalla == "encuesta":
    total_bloques = 4
    bloque = st.session_state.bloque
    st.markdown(f"### Bloque {bloque} de {total_bloques}")

    alt1 = {"consumo": "5 L/100km", "diseño": "Moderno"}
    alt2 = {"consumo": "8 L/100km", "diseño": "Clásico"}

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Alternativa A**")
        st.write(f"Consumo: {alt1['consumo']}")
        st.write(f"Diseño: {alt1['diseño']}")
    with col2:
        st.markdown("**Alternativa B**")
        st.write(f"Consumo: {alt2['consumo']}")
        st.write(f"Diseño: {alt2['diseño']}")

    eleccion = st.radio("¿Cuál preferís?", ["Alternativa A", "Alternativa B"], key=f"radio_{bloque}")

    if st.button("Guardar y continuar"):
        supabase.table("respuestas").insert({
            "user_id": st.session_state.user_id,
            "bloque": bloque,
            "alternativa_elegida": eleccion,
            "consumo_alt1": alt1["consumo"],
            "diseño_alt1": alt1["diseño"],
            "consumo_alt2": alt2["consumo"],
            "diseño_alt2": alt2["diseño"],
            "timestamp": datetime.now().isoformat(),
            "edad": st.session_state.datos["edad"],
            "sexo": st.session_state.datos["sexo"],
            "nivel": st.session_state.datos["nivel"]
        }).execute()

        if bloque < total_bloques:
            st.session_state.bloque += 1
        else:
            st.session_state.pantalla = "fin"

# Pantalla final
elif st.session_state.pantalla == "fin":
    st.success("¡Gracias por participar en la encuesta!")
