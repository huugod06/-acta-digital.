import streamlit as st
import hashlib
import time
import json
from pathlib import Path

# --- Prompt 3: función de hash ---
def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# --- Prompt 4: Interfaz de registro ---
st.title("Registro de Documentos Digitales")

owner = st.text_input("Propietario")
content = st.text_area("Contenido del documento")

# Ruta del "ledger" local (línea por registro)
LEDGER_PATH = Path("blockchain.json")

if st.button("Registrar"):
    if not owner.strip():
        st.warning("Por favor, indica el Propietario.")
    elif not content.strip():
        st.warning("El Contenido del documento no puede estar vacío.")
    else:
        record = {
            "owner": owner.strip(),
            "hash": get_hash(content),
            "time": time.time(),  # sello de tiempo (epoch)
        }
        # Asegurar que el archivo existe (opcional)
        if not LEDGER_PATH.exists():
            LEDGER_PATH.touch()

        # Guardar como línea JSON (JSONL)
        with LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        st.success("Documento registrado con éxito ✅")
        st.code(json.dumps(record, ensure_ascii=False, indent=2), language="json")

# Mostrar un previo de los últimos registros (opcional)
if LEDGER_PATH.exists():
    st.subheader("Últimos registros")
    lines = LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
    if lines:
        # Mostrar hasta 5 últimos
        for line in lines[-5:][::-1]:
            try:
                rec = json.loads(line)
                st.json(rec)
            except json.JSONDecodeError:
                st.write("Registro malformado:", line)

# Botón para descargar el ledger (útil en la nube)
if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0:
    st.download_button(
        label="Descargar blockchain.json",
        data=LEDGER_PATH.read_bytes(),
        file_name="blockchain.json",
        mime="application/json",
    )
