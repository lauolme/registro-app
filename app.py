import streamlit as st
import yaml
import hashlib
from pathlib import Path

# Rutas
RULES_PATH = Path("data/rules.yml")
TEMPLATE_PATH = Path("data/templates/dictamen.md")

# Cargar reglas desde YAML
def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Cargar plantilla de dictamen
def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

# Evaluar hechos contra reglas
def evaluate_rules(facts, rules):
    triggered = []
    for rule in rules:
        cond = rule.get("condition", {})
        match = all(str(facts.get(k, "")).lower() == str(v).lower() for k, v in cond.items())
        if match:
            triggered.append(rule)
    return triggered

# Generar dictamen
def generate_dictamen(template, facts, triggered):
    analisis = "\n".join([f"- {r['name']}: {r['analysis']}" for r in triggered]) or "No se activaron reglas."
    conclusion = "\n".join([r["conclusion"] for r in triggered]) or "No se aprecia efecto jurídico relevante."
    riesgos = "\n".join([r.get("risk", "") for r in triggered if r.get("risk")]) or "Ninguno identificado."
    pasos = "\n".join([r.get("next_steps", "") for r in triggered if r.get("next_steps")]) or "Ninguno."

    md = template.format(
        hechos="\n".join([f"- {k}: {v}" for k, v in facts.items()]),
        cuestiones=", ".join([r["name"] for r in triggered]) or "Ninguna",
        analisis=analisis,
        conclusion=conclusion,
        riesgos=riesgos,
        pasos=pasos,
    )
    return md

# Calcular hash SHA-256
def sha256_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

# UI
st.set_page_config(page_title="LegalTech Registro", page_icon="⚖️", layout="wide")
st.title("⚖️ LegalTech Registro")
st.write("Analizador de casos sobre prioridad, publicidad, oponibilidad y tracto en España/UE.")

# Cargar reglas
rules = load_rules()
template = load_template()

# Demo casos
demo_cases = {
    "Caso demo: Doble venta": {"doble_venta": "Sí", "admin_no_inscrito": "No"},
    "Caso demo: Admin no inscrito": {"doble_venta": "No", "admin_no_inscrito": "Sí"},
}

# Selector de demo
selected_demo = st.selectbox("⚡ Cargar un caso de demostración", ["Ninguno"] + list(demo_cases.keys()))

facts = {"doble_venta": "", "admin_no_inscrito": ""}

if selected_demo != "Ninguno":
    facts.update(demo_cases[selected_demo])

# Formulario de entrada
st.subheader("👉 Introducir hechos del caso")
facts["doble_venta"] = st.radio("¿Hay doble venta de inmueble?", ["", "Sí", "No"], index=["", "Sí", "No"].index(facts["doble_venta"]))
facts["admin_no_inscrito"] = st.radio("¿Administrador no inscrito?", ["", "Sí", "No"], index=["", "Sí", "No"].index(facts["admin_no_inscrito"]))

# Evaluar reglas
if st.button("Evaluar"):
    triggered = evaluate_rules(facts, rules)
    st.subheader("📌 Traza del análisis")
    st.write("**Hechos capturados:**", facts)
    st.write("**Reglas activadas:**", [r["name"] for r in triggered] or "Ninguna")

    dictamen = generate_dictamen(template, facts, triggered)
    hash_value = sha256_hash(dictamen)

    st.subheader("📄 Dictamen generado")
    st.markdown(dictamen)

    st.subheader("🔒 Evidencia de integridad")
    st.code(hash_value)

    st.download_button("⬇️ Descargar dictamen en Markdown", dictamen, file_name="dictamen.md", mime="text/markdown")
