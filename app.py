import streamlit as st
import hashlib
import time
import json
import secrets  # <-- Prompt 6
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
    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("hash") == h:
                return True
    return False

# ===========================
#        INTERFAZ UI
# ===========================
st.title("Registro de Documentos Digitales")

# -------- Registrar documento (Prompt 4) --------
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

# -------- Verificar integridad (Prompt 5) --------
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

# -------- Identidad y firma (Prompt 6) --------
st.subheader("Identidad y firma (demo)")

# Guardamos claves en la sesión del usuario de Streamlit (no en disco)
if "private_key" not in st.session_state:
    st.session_state.private_key = None
    st.session_state.public_key = None

col1, col2 = st.columns(2)
with col1:
    if st.button("Generar claves"):
        # Clave privada aleatoria (16 bytes -> 32 hex)
        st.session_state.private_key = secrets.token_hex(16)
        # Clave pública como hash de la privada (demo pedagógica, NO criptografía real)
        st.session_state.public_key = get_hash(st.session_state.private_key)

with col2:
    if st.session_state.private_key:
        # Descargar la clave privada para guardarla de forma segura
        st.download_button(
            "Descargar clave privada (txt)",
            data=st.session_state.private_key.encode(),
            file_name="private_key.txt",
            mime="text/plain",
        )

if st.session_state.public_key:
    st.write("**Tu clave pública:**")
    st.code(st.session_state.public_key)

    with st.expander("Ver mi clave privada (¡no la compartas!)"):
        st.code(st.session_state.private_key)

    # Demo de "firma" del contenido actual (solo ilustrativa)
    if content.strip():
        demo_sig = get_hash(get_hash(content) + st.session_state.private_key)
        st.caption("Ejemplo de 'firma' del contenido actual (demo pedagógica):")
        st.code(demo_sig)

st.info(
    "Explicación: **la clave pública identifica**, mientras que **la clave privada te da poder para firmar**. "
    "Esta demo usa `public_key = hash(private_key)` solo con fines educativos; **no es un esquema de firma real**. "
    "Para producción, usa criptografía asimétrica (p. ej., Ed25519/ECDSA) con verificación mediante clave pública."
)

# -------- Vista rápida y descarga del ledger --------
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
        )# --- Prompt 7: Votación de validez (DAO simple) ---
from pathlib import Path  # (ignora si ya lo importaste arriba)
VOTES_PATH = Path("votes.json")

def hash_exists(h: str) -> bool:
    """Comprueba si un hash existe en el registro (blockchain.json)."""
    try:
        if not LEDGER_PATH.exists():
            return False
        with LEDGER_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("hash") == h:
                    return True
    except Exception:
        return False
    return False

st.header("Votación de validez")

# Autorrelleno del hash con el documento actual (si lo tienes en el área de texto)
prefill_hash = get_hash(content) if content and content.strip() else ""

doc_hash = st.text_input(
    "Hash del documento a votar",
    value=prefill_hash,
    placeholder="Pega un hash SHA-256 (64 caracteres hex)",
    key="vote_hash",
)

vote = st.radio("¿Es válido?", ["Sí", "No"], horizontal=True)

def _valid_sha256(h: str) -> bool:
    h = h.strip().lower()
    return len(h) == 64 and all(c in "0123456789abcdef" for c in h)

if st.button("Votar"):
    if not doc_hash.strip():
        st.warning("Introduce un hash para votar.")
    elif not _valid_sha256(doc_hash):
        st.error("El hash no parece un SHA-256 válido (64 caracteres hex).")
    elif not hash_exists(doc_hash.strip().lower()):
        st.warning("No se encontró ese hash en el registro. Registra el documento o verifica el hash.")
    else:
        vote_rec = {
            "hash": doc_hash.strip().lower(),
            "vote": vote,
            "time": time.time(),
        }
        # Si el usuario generó claves en el Prompt 6, registra su clave pública como "votante"
        if st.session_state.get("public_key"):
            vote_rec["voter"] = st.session_state["public_key"]

        if not VOTES_PATH.exists():
            VOTES_PATH.touch()

        with VOTES_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(vote_rec, ensure_ascii=False) + "\n")

        st.success("Voto registrado 🗳️")

# (Opcional) Conteo en vivo para el hash introducido
if VOTES_PATH.exists() and doc_hash.strip():
    yes = no = 0
    with VOTES_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("hash") == doc_hash.strip().lower():
                if r.get("vote") == "Sí":
                    yes += 1
                elif r.get("vote") == "No":
                    no += 1
    total = yes + no
    if total > 0:
        st.subheader("Resultados actuales para este hash")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sí", yes)
        c2.metric("No", no)
        c3.metric("Total", total)

# (Opcional) Descargar el fichero de votos
if VOTES_PATH.exists() and VOTES_PATH.stat().st_size > 0:
    st.download_button(
        label="Descargar votes.json",
        data=VOTES_PATH.read_bytes(),
        file_name="votes.json",
        mime="application/json",
    )
# --- Prompt 8: Resultado de la votación (global) ---
def count_votes():
    yes, no = 0, 0
    # Usa el mismo fichero de votos del Prompt 7
    try:
        if not VOTES_PATH.exists():
            return yes, no
        with VOTES_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    v = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if v.get("vote") == "Sí":
                    yes += 1
                else:
                    no += 1
    except Exception:
        pass
    return yes, no

st.subheader("Resultado de la votación (global)")
if st.button("Ver resultado"):
    y, n = count_votes()
    st.write(f"Sí: {y} | No: {n}")
    total = y + n
    if total > 0:
        st.progress(y / total)
    st.caption(
        "Este código suma votos y muestra el resultado. "
        "Ejecuta la decisión, pero **no analiza si es justa** ni quién debería asumir responsabilidad."
    )

