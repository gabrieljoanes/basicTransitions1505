import streamlit as st
import requests
from utils.io import load_examples
from utils.processing import get_transition_from_gpt
from utils.layout import rebuild_article_with_transitions
from utils.display import layout_title_and_input, show_output, show_version
from utils.version import compute_version_hash
from utils.title_blurb import generate_title_and_blurb
from utils.logger import save_output_to_file

# TEMP: Debug secrets
st.write("Secrets loaded:", list(st.secrets.keys()))

# --- Proxy Call ---
API_URL = st.secrets["API_URL"]
API_TOKEN = st.secrets["API_TOKEN"]

def call_proxy(prompt_text, model="gpt-4"):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    openai_payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}]
    }

    payload = {
        "prompt": repr(openai_payload)
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        debug_json = response.json()
        st.write("\U0001F6E0 DEBUG: proxy response", debug_json)
    except Exception as e:
        st.error(f"\u274C Erreur lors de l'analyse de la réponse proxy : {str(e)}")
        raise

    response.raise_for_status()
    return debug_json.get("reply", "").strip()

# --- App Version Hash ---
VERSION = compute_version_hash([
    "app.py",
    "transitions.json",
    "utils/io.py",
    "utils/processing.py",
    "utils/layout.py",
    "utils/display.py",
    "utils/version.py",
    "utils/title_blurb.py",
    "utils/logger.py"
])

# --- Tabs UI ---
tabs = st.tabs([
    "✨ Générer les transitions",
    "📝 Résultat",
    "✅ Validation",
    "💾 Sauvegarde",
    "📤 Upload par lot depuis Google Drive"
])

# Shared state
if "generated_transitions" not in st.session_state:
    st.session_state.generated_transitions = []
    st.session_state.rebuilt_text = ""
    st.session_state.title_text = ""
    st.session_state.chapo_text = ""
    st.session_state.title_blurb = ""

# --- Génération ---
with tabs[0]:
    text_input = layout_title_and_input()

    if st.button("✨ Générer"):
        if "TRANSITION" not in text_input:
            st.warning("Aucune balise `TRANSITION` trouvée.")
        else:
            examples = load_examples()
            parts = text_input.split("TRANSITION")
            pairs = list(zip(parts[:-1], parts[1:]))

            title_blurb = generate_title_and_blurb(parts[0], call_proxy)
            st.session_state.title_blurb = title_blurb

            transitions = []
            for para_a, para_b in pairs:
                transition = get_transition_from_gpt(para_a, para_b, examples, call_proxy)
                transitions.append(transition)

            rebuilt_text, error = rebuild_article_with_transitions(text_input, transitions)
            if error:
                st.error(error)
            else:
                st.session_state.generated_transitions = transitions
                st.session_state.rebuilt_text = rebuilt_text
                if "Titre :" in title_blurb and "Chapeau :" in title_blurb:
                    lines = title_blurb.split("\n")
                    title_line = next((l for l in lines if l.startswith("Titre :")), "")
                    chapo_line = next((l for l in lines if l.startswith("Chapeau :")), "")
                    st.session_state.title_text = title_line.replace("Titre :", "").strip()
                    st.session_state.chapo_text = chapo_line.replace("Chapeau :", "").strip()
                else:
                    st.session_state.title_text = "Titre non défini"
                    st.session_state.chapo_text = "Chapeau non défini"

# --- Résultat ---
with tabs[1]:
    st.markdown("### 📰 Titre")
    st.markdown(f"**{st.session_state.title_text}**")
    st.markdown("&nbsp;\n" * 2, unsafe_allow_html=True)
    st.markdown("### ✏️ Chapeau")
    st.markdown(st.session_state.chapo_text)
    st.markdown("&nbsp;\n" * 4, unsafe_allow_html=True)
    st.markdown("### 🧾 Article reconstruit")
    show_output(st.session_state.rebuilt_text)

# --- Validation ---
with tabs[2]:
    st.markdown("### 🧩 Transitions générées")
    for i, t in enumerate(st.session_state.generated_transitions, 1):
        st.markdown(f"{i}. _{t}_")

# --- Sauvegarde ---
with tabs[3]:
    if st.session_state.rebuilt_text:
        filepath = save_output_to_file(
            st.session_state.title_text,
            st.session_state.chapo_text,
            st.session_state.rebuilt_text,
            st.session_state.generated_transitions
        )
        st.success(f"✅ L'article a été sauvegardé dans `{filepath}`")

# --- Upload (placeholder) ---
with tabs[4]:
    st.info("Fonction d'import depuis Google Drive à venir.")

show_version(VERSION)
