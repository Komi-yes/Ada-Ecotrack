import streamlit as st

from ecotrack.parser import estimate_co2

st.set_page_config(page_title="EcoTrack", page_icon="🌱", layout="centered")

st.title("🌱 EcoTrack")
st.caption("Registrá tu día en lenguaje natural y estimamos tu huella de carbono.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("entry_form", clear_on_submit=True):
    text = st.text_area(
        "¿Qué hiciste hoy?",
        placeholder="Ej: Hoy comí carne y viajé 20km en bus",
        height=100,
    )
    submitted = st.form_submit_button("Calcular huella de CO2")

if submitted and text.strip():
    result = estimate_co2(text)
    st.session_state.history.append((text, result))

if not st.session_state.history:
    st.info("Escribí una frase describiendo tu comida y tu transporte del día para empezar.")
else:
    latest_text, latest_result = st.session_state.history[-1]

    st.subheader("Resultado")
    st.metric("CO2 estimado", f"{latest_result.total_co2_kg:.2f} kg")

    if latest_result.items:
        for item in latest_result.items:
            icon = "🍽️" if item.category == "comida" else "🚗"
            st.write(f"{icon} **{item.label}** ({item.detail}) → {item.co2_kg:.2f} kg CO2")
    else:
        st.warning("No se detectaron alimentos ni medios de transporte en el texto.")

    with st.expander("Historial de esta sesión"):
        for past_text, past_result in reversed(st.session_state.history):
            st.write(f"- \"{past_text}\" → **{past_result.total_co2_kg:.2f} kg CO2**")

st.divider()
st.caption(
    "Estimaciones basadas en factores de emisión promedio (comida por porción, "
    "transporte por km). Prototipo educativo, no reemplaza un cálculo certificado."
)
