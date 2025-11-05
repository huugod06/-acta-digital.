import streamlit as st
import hashlib
import time
import json
from pathlib import Path

# --- Prompt 3: función de hash ---
def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# --- Prompt 5: verificación de integridad ---
LEDGER_PATH = Path("blockchain.json")

def verify(content: str) -> bool:
    """Devuelve True si el hash del contenido ya existe en blockchain.json"""
    h = get_hash(content)
    if not LEDGER_PATH.exists():
        return False
    # Leemos línea a línea (formato JSON Lines)
    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                # Si hay una línea corrupta, la ignoramos y seguimos
                continue
            if r.get("hash") == h:
                return True
    return False

# --- Interfaz ---
st.title("Registro de Documentos Digitales")

# Sección: Registrar documento (Prompt 4)
st.subheader("Registrar documento")
owner = st.text_input("Propietario")
content = st.text_area("Contenido del documento", placeholder="Pega aquí el contenido a registrar")

if st.button("Registrar"):
    if not owner.strip():
        st.warning("Por favor, indica el Propietario.")
    elif not content.strip():
        st.warning("El contenido no puede estar vacío.")
    else:
        record = {
            "owner": owner.strip(),
            "hash": get_hash(content),
            "time": time.time(),  # sello de tiempo (epoch)
        }
        if not LEDGER_PATH.exists():
            LEDGER_PATH.touch()
        with LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        st.success("Documento registrado con éxito ✅")
        st.code(json.dumps(record, ensure_ascii=False, indent=2), language="json")

# Sección: Verificar integridad (Prompt 5)
st.subheader("Verificar integridad")
to_verify = st.text_area("Texto a verificar", key="verify_text", placeholder="Pega el contenido para comprobar si ya fue registrado")

if st.button("Verificar"):
    if not to_verify.strip():
        st.warning("Introduce un texto para verificar.")
    else:
        exists = verify(to_verify)
        if exists:
            st.success("✅ El contenido ya estaba registrado (hash coincide).")
            st.code(get_hash(to_verify))
        else:
            st.error("❌ No se encontró un registro con este contenido.")
            st.caption("Sugerencia: si crees que sí estaba, confirma que el texto sea exactamente igual (espacios, saltos de línea, mayúsculas).")

# (Opcional) Mostrar últimos registros y descarga del "ledger"
if LEDGER_PATH.exists():
    st.subheader("Últimos registros")
    lines = LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
    if lines:
        for line in lines[-5:][::-1]:
            try:
                rec = json.loads(line)
                st.json(rec)
            except json.JSONDecodeError:
                st.write("Registro malformado:", line)

    if LEDGER_PATH.stat().st_size > 0:
        st.download_button(
            label="Descargar blockchain.json",
            data=LEDGER_PATH.read_bytes(),
            file_name="blockchain.json",
            mime="application/json",
        )
