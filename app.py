import streamlit as st
from openai import OpenAI
from utils.io import load_examples
from utils.processing import get_transition_from_gpt
from utils.layout import rebuild_article_with_transitions
from utils.display import layout_title_and_input, show_output, show_version
from utils.version import compute_version_hash
from utils.title_blurb import generate_title_and_blurb
from utils.logger import save_output_to_file

MODEL = "gpt-4-turbo"

def main():
    # ✅ Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

    # ✅ Display input UI
    text_input = layout_title_and_input()

    if st.button("✨ Générer les transitions"):
        if "TRANSITION" not in text_input:
            st.warning("Aucune balise `TRANSITION` trouvée.")
            return

        examples = load_examples()
        parts = text_input.split("TRANSITION")
        pairs = list(zip(parts[:-1], parts[1:]))

        # ✅ Token counters
        total_prompt_tokens = 0
        total_completion_tokens = 0

        # ✅ Title & blurb
        title_blurb, t_prompt, t_completion = generate_title_and_blurb(parts[0], client, model=MODEL)
        total_prompt_tokens += t_prompt
        total_completion_tokens += t_completion

        # ✅ Transitions
        generated_transitions = []
        for i, (para_a, para_b) in enumerate(pairs):
            is_last = (i == len(pairs) - 1)
            transition, p_tokens, c_tokens = get_transition_from_gpt(para_a, para_b, examples, client, is_last=is_last, model=MODEL)
            total_prompt_tokens += p_tokens
            total_completion_tokens += c_tokens
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

                st.markdown("### 📜 Titre")
                st.markdown(f"**{title_text}**")
                st.markdown("&nbsp;\n&nbsp;\n&nbsp;", unsafe_allow_html=True)

                st.markdown("### ✏️ Chapeau")
                st.markdown(chapo_text)
                st.markdown("&nbsp;\n" * 6, unsafe_allow_html=True)
            else:
                title_text = "Titre non défini"
                chapo_text = "Chapeau non défini"
                st.markdown("### 📜 Titre et chapeau")
                st.markdown(title_blurb)
                st.markdown("&nbsp;\n" * 6, unsafe_allow_html=True)

            st.markdown("### 💾 Article reconstruit")
            show_output(rebuilt_text)

            st.markdown("### 🧩 Transitions générées")
            for i, t in enumerate(generated_transitions, 1):
                st.markdown(f"{i}. _{t}_")

            filepath = save_output_to_file(title_text, chapo_text, rebuilt_text, generated_transitions)
            st.success(f"✅ L'article a été sauvegardé dans `{filepath}`")

            # ✅ Display estimated cost
            cost = (total_prompt_tokens * 0.01 + total_completion_tokens * 0.03) / 1000
            st.markdown("### 💰 Coût estimé")
            st.markdown(f"**{total_prompt_tokens}** tokens prompt + **{total_completion_tokens}** tokens complétion = **${cost:.4f}**")

    show_version(VERSION)

if __name__ == "__main__":
    main()
