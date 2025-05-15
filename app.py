# ...
if st.button("✨ Générer les transitions"):
    if "TRANSITION" not in text_input:
        show_warning_or_error(missing=True)
    else:
        transitions = load_transitions()
        needed = text_input.count("TRANSITION")
        replacements = generate_unique_transitions(transitions, needed)

        if len(replacements) < needed:
            show_warning_or_error(not_enough=True)
        else:
            result = text_input
            for phrase in replacements:
                result = result.replace("TRANSITION", phrase, 1)
            show_output(result)

            # 🔽 List selected transitions
            st.markdown("### 🧩 Transitions utilisées :")
            for i, t in enumerate(replacements, 1):
                st.markdown(f"{i}. _{t}_")
