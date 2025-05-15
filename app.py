# app.py
from openai import OpenAI

# Load your secret key from Streamlit (must be in the secrets panel!)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


import streamlit as st
from utils.io import load_examples
from utils.processing import get_transition_from_gpt
from utils.display import (
    layout_title_and_input,
    show_output,
    show_version
)
from utils.version import compute_version_hash

def main():
    VERSION = compute_version_hash([
        "app.py",
        "transitions.json",
        "utils/io.py",
        "utils/processing.py",
        "utils/display.py",
        "utils/version.py"
    ])

    text_input = layout_title_and_input()

    if st.button("✨ Générer les transitions"):
        if "TRANSITION" not in text_input:
            st.warning("Aucune balise `TRANSITION` trouvée.")
            return

        examples = load_examples()
        parts = text_input.split("TRANSITION")
        pairs = list(zip(parts[:-1], parts[1:]))

        generated_transitions = []
        for para_a, para_b in pairs:
            transition = get_transition_from_gpt(para_a, para_b, examples)
            generated_transitions.append(transition)

        # Rebuild final text
        final_text = parts[0]
        for t, next_part in zip(generated_transitions, parts[1:]):
            final_text += f"{t} {next_part}"

        # Output
        show_output(final_text)
        st.markdown("### 🧩 Transitions générées :")
        for i, t in enumerate(generated_transitions, 1):
            st.markdown(f"{i}. _{t}_")

    show_version(VERSION)

if __name__ == "__main__":
    main()
