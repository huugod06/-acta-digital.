import streamlit as st
import hashlib
import time
import json

# --- Prompt 3: función de hash ---
def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

st.title("Acta Digital — Hash tester")

st.write("Escribe un texto y calcula su hash SHA-256.")

texto = st.text_input("Texto a hashear", placeholder="Escribe aquí...")

# Calcula automáticamente si hay texto
if texto:
    h = get_hash(texto)
    st.write("**Hash (SHA-256):**")
    st.code(h)

# Opcional: botón de cálculo
if st.button("Calcular hash"):
    if not texto:
        st.warning("Primero escribe algún texto.")
    else:
        h = get_hash(texto)
        st.success("Hash calculado:")
        st.code(h)


