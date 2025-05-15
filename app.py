import streamlit as st
from openai import OpenAI
from utils.io import load_examples
from utils.processing import get_transition_from_gpt
from utils.display import layout_title_and_input, show_output, show_version
from utils.version import compute_version_hash
from utils.layout import rebuild_article_with_transitions  # ✅ New import

def main():
    # ✅ Load OpenAI client from Streamlit secrets
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # ✅ Version hash
    VERSION = compute_version_hash([
        "app.py",
        "transitions.json",
        "utils/io.py",
        "utils/processing.py",
        "utils/display.py",
        "utils/version.py",
        "utils/layout.py"  # ✅ Include new file in hash
    ])

    # ✅ UI input
    text_input = layout_title_and_input()

    if st.button("✨ Générer les transitions"):
        if "TRANSITION" not in text_input:
            st.warning("Aucune balise `TRANSITION` trouvée.")
            return

        # ✅ Load few-shot examples
        examples = load_examples()

        # ✅ Break input into paragraph pairs
        parts = text_input.split("TRANSITION")
        pairs = list(zip(parts[:-1], parts[1:]))

        # ✅ Generate transition for each pair
        generated_transitions = []
        for para_a, para_b in pairs:
            transition = get_transition_from_gpt(para_a, para_b, examples, client)
            generated_transitions.append(transition)

        # ✅ Rebuild article using helper
        rebuilt_text, error = rebuild_article_with_transitions(text_input, generated_transitions)
        if error:
            st.error(error)
        else:
            # ✅ Show final output and transitions
            show_output(rebuilt_text)
            st.markdown("### 🧩 Transitions générées :")
            for i, t in enumerate(generated_transitions, 1):
                st.markdown(f"{i}. _{t}_")

    show_version(VERSION)

if __name__ == "__main__":
    main()
