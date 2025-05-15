import streamlit as st
from utils.io import load_transitions
from utils.processing import generate_unique_transitions
from utils.display import (
    layout_title_and_input,
    show_output,
    show_warning_or_error,
    show_version
)
from utils.version import compute_version_hash

# Compute version hash based on key files
VERSION = compute_version_hash([
    "app.py",
    "transitions.json",
    "utils/io.py",
    "utils/processing.py",
    "utils/display.py",
    "utils/version.py"
])

# UI input
text_input = layout_title_and_input()

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

# Show version hash at the bottom
show_version(VERSION)
