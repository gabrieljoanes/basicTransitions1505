import streamlit as st
from openai import OpenAI
from utils.io import load_examples
from utils.processing import get_transition_from_gpt
from utils.layout import rebuild_article_with_transitions
from utils.display import layout_title_and_input, show_output, show_version
from utils.version import compute_version_hash
from utils.title_blurb import generate_title_and_blurb  # ✅ NEW

def main():
    # ✅ Load OpenAI client from Streamlit secrets
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # ✅ Compute version hash for display/debug
    VERSION = compute_version_hash([
        "app.py",
        "transitions.json",
        "utils/io.py",
        "utils/processing.py",
        "utils/layout.py",
        "utils/display.py",
        "utils/version.py",
        "utils/title_blurb.py"
    ])

    # ✅ Show input UI
    text_input = layout_title_and_input()

    if st.button("✨ Générer les transitions"):
        if "TRANSITION" not in text_input:
            st.warning("Aucune balise `TRANSITION` trouvée.")
            return

        # ✅ Load few-shot examples
        examples = load_examples()

        # ✅ Split into paragraph parts and pairs
        parts = text_input.split("TRANSITION")
        pairs = list(zip(parts[:-1], parts[1:]))

        # ✅ Generate title and blurb from the first paragraph
        title_blurb = generate_title_and_blurb(parts[0], client)

        # ✅ Generate transitions
        generated_transitions = []
        for para_a, para_b in pairs:
            transition = get_transition_from_gpt(para_a, para_b, examples, client)
            generated_transitions.append(transition)

        # ✅ Rebuild the article with transitions
        rebuilt_text, error = rebuild_article_with_transitions(text_input, generated_transitions)
        if error:
            st.error(error)
        else:
            # ✅ Display title and blurb
            st.markdown("### 📰 Titre et chapeau")
            st.markdown(title_blurb)

            # ✅ Display full output with transitions
            show_output(rebuilt_text)

            # ✅ Display list of transitions
            st.markdown("### 🧩 Transitions générées :")
            for i, t in enumerate(generated_transitions, 1):
                st.markdown(f"{i}. _{t}_")

    # ✅ Always show version
    show_version(VERSION)

if __name__ == "__main__":
    main()
