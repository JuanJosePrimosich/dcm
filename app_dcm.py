import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

# Polyfill para st.experimental_rerun si no existe (versiones antiguas)
if not hasattr(st, "experimental_rerun"):
    def experimental_rerun():
        st.session_state["_rerun"] = True
        st.stop()
    st.experimental_rerun = experimental_rerun

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Test de Elección Discreta", layout="centered")

# Manejo simple para rerun
if "_rerun" in st.session_state:
    del st.session_state["_rerun"]
    # Si querés, podés poner algo para refrescar (no estrictamente necesario)

st.markdown("## Bienvenido al estudio de preferencias")
st.info("**Este estudio es anónimo y solo toma unos minutos. Los datos se usarán con fines académicos.**")

# Consentimiento informado
if "consentimiento" not in st.session_state:
    st.session_state.consentimiento = False

if not st.session_state.consentimiento:
    if st.button("Acepto participar en el estudio"):
        st.session_state.consentimiento = True
        st.experimental_rerun()
    st.stop()

st.markdown("### Preguntas iniciales")
edad = st.number_input("Edad", min_value=15, max_value=99, step=1)
sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro", "Prefiero no decirlo"])
nivel = st.selectbox("Nivel educativo", ["Secundario", "Terciario", "Universitario", "Posgrado"])

if st.button("Comenzar encuesta"):
    st.session_state.user_id = str(uuid.uuid4())
    st.session_state.preguntas_previas = {
        "edad": edad,
        "sexo": sexo,
        "nivel": nivel
    }
    st.session_state.bloque = 1
    st.experimental_rerun()

if "user_id" in st.session_state and "bloque" in st.session_state:

    total_bloques = 4

    st.markdown(f"## Bloque {st.session_state.bloque} de {total_bloques}")
    st.write("Elegí una alternativa:")

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
