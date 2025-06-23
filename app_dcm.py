import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

# Cargar claves desde archivo .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Estilo visual moderno
st.set_page_config(page_title="Test de Elección Discreta", layout="centered")

st.markdown("## Bienvenido al estudio de preferencias")
st.info("**Este estudio es anónimo y solo toma unos minutos. Los datos se usarán con fines académicos.**")

# Pantalla de consentimiento
if "consentimiento" not in st.session_state:
    st.session_state.consentimiento = False

if not st.session_state.consentimiento:
    if st.button("Acepto participar en el estudio"):
        st.session_state.consentimiento = True
    st.stop()

# Preguntas previas
st.markdown("### Preguntas iniciales")

edad = st.number_input("Edad", min_value=15, max_value=99, step=1)
sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro", "Prefiero no decirlo"])
nivel = st.selectbox("Nivel educativo", ["Secundario", "Terciario", "Universitario", "Posgrado"])

# Iniciar encuesta
if st.button("Comenzar encuesta"):
    st.session_state.user_id = str(uuid.uuid4())
    st.session_state.preguntas_previas = {
        "edad": edad,
        "sexo": sexo,
        "nivel": nivel
    }
    st.session_state.bloque = 1
    st.experimental_rerun()

# Mostrar bloques si se completaron preguntas previas
if "user_id" in st.session_state and "bloque" in st.session_state:

    total_bloques = 4

    st.markdown(f"## Bloque {st.session_state.bloque} de {total_bloques}")
    st.write("Elegí una alternativa:")

    # Atributos ficticios (podés modificar para cargar dinámicamente)
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

    eleccion = st.radio("¿Cuál preferís?", ["Alternativa A", "Alternativa B"])

    if st.button("Guardar y continuar"):
        # Guardar en Supabase
        supabase.table("respuestas").insert({
            "user_id": st.session_state.user_id,
            "bloque": st.session_state.bloque,
            "alternativa_elegida": eleccion,
            "consumo_alt1": alt1["consumo"],
            "diseño_alt1": alt1["diseño"],
            "consumo_alt2": alt2["consumo"],
            "diseño_alt2": alt2["diseño"],
            "timestamp": datetime.now().isoformat(),
            "edad": st.session_state.preguntas_previas["edad"],
            "sexo": st.session_state.preguntas_previas["sexo"],
            "nivel": st.session_state.preguntas_previas["nivel"]
        }).execute()

        if st.session_state.bloque < total_bloques:
            st.session_state.bloque += 1
            st.experimental_rerun()
        else:
            st.success("¡Gracias por participar!")
            st.stop()
