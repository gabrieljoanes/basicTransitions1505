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

def call_proxy(prompt, model="gpt-3.5-turbo"):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

def main():
    # ✅ Compute version hash
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

    # ✅ Layout input
    text_input = layout_title_and_input()

    if st.button("✨ Générer les transitions"):
        if "TRANSITION" not in text_input:
            st.warning("Aucune balise `TRANSITION` trouvée.")
            return

        examples = load_examples()
        parts = text_input.split("TRANSITION")
        pairs = list(zip(parts[:-1], parts[1:]))

        # Replace original OpenAI call with proxy
        title_blurb = generate_title_and_blurb(parts[0], call_proxy)

        generated_transitions = []
        for para_a, para_b in pairs:
            transition = get_transition_from_gpt(para_a, para_b, examples, call_proxy)
            generated_transitions.append(transition)

        rebuilt_text, error = rebuild_article_with_transitions(text_input, generated_transitions)
        if error:
            st.error(error)
        else:
            if "Titre :" in title_blurb and "Chapeau :" in title_blurb:
                lines = title_blurb.split("\n")
                title_line = next((l for l in lines if l.startswith("Titre :")), "")
                chapo_line = next((l for l in lines if l.startswith("Chapeau :")), "")
                title_text = title_line.replace("Titre :", "").strip()
                chapo_text = chapo_line.replace("Chapeau :", "").strip()

                st.markdown("### 📰 Titre")
                st.markdown(f"**{title_text}**")
                st.markdown("&nbsp;\n&nbsp;\n&nbsp;", unsafe_allow_html=True)
                st.markdown("### ✏️ Chapeau")
                st.markdown(chapo_text)
                st.markdown("&nbsp;\n" * 6, unsafe_allow_html=True)
            else:
                title_text = "Titre non défini"
                chapo_text = "Chapeau non défini"
                st.markdown("### 📰 Titre et chapeau")
                st.markdown(title_blurb)
                st.markdown("&nbsp;\n" * 6, unsafe_allow_html=True)

            st.markdown("### 🧾 Article reconstruit")
            show_output(rebuilt_text)

            st.markdown("### 🧩 Transitions générées")
            for i, t in enumerate(generated_transitions, 1):
                st.markdown(f"{i}. _{t}_")

            filepath = save_output_to_file(title_text, chapo_text, rebuilt_text, generated_transitions)
            st.success(f"✅ L'article a été sauvegardé dans `{filepath}`")

    show_version(VERSION)

if __name__ == "__main__":
    main()
