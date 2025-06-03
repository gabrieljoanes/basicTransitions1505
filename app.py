import streamlit as st
import traceback
from datetime import datetime

from utils.io import load_examples
from utils.processing import get_transition_from_gpt
from utils.layout import rebuild_article_with_transitions
from utils.display import layout_title_and_input, show_output, show_version
from utils.version import compute_version_hash
from utils.title_blurb import generate_title_and_blurb
from utils.logger import save_output_to_file, logger
from utils.validate_prompt_compliance import validate_batch, display_validation_results
from utils.google_drive import get_google_drive_service, list_folder_contents, process_drive_files

def process_uploaded_files(uploaded_files):
    results = []
    for uploaded_file in uploaded_files:
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            lines = content.strip().split('\n')
            transitions = []

            for line in lines:
                line = line.strip()
                if line.startswith("Transitions générées:"):
                    continue
                if line and line[0].isdigit() and ". " in line:
                    transition = line.split(". ", 1)[1].strip()
                    transitions.append(transition)

            if transitions:
                results.append((uploaded_file.name, transitions))

        except Exception as e:
            logger.error(f"Error processing file {uploaded_file.name}: {str(e)}")
            continue

    return results

def main():
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✨ Générer les transitions", 
        "📝 Résultat", 
        "✅ Validation",
        "📅 Sauvegarde",
        "📄 Upload par lot depuis Google Drive"
    ])

    with tab1:
        text_input = layout_title_and_input()

        if st.button("✨ Générer les transitions"):
            if "TRANSITION" not in text_input:
                st.warning("Aucune balise `TRANSITION` trouvée.")
                return
            try:
                examples = load_examples()
                logger.info("Successfully loaded examples")
                st.write("🔍 Examples preview (first 3):", examples[:3])

                parts = text_input.split("TRANSITION")
                pairs = list(zip(parts[:-1], parts[1:]))
                logger.info(f"Processing {len(pairs)} paragraph pairs")
                print(parts[0], '🙋‍♂️🐦‍🔥😊😊')
                # Safely extract title and chapo from dict
                title_blurb = generate_title_and_blurb(parts[0])
                # Parse the title and blurb from the response
                title_blurb_lines = title_blurb.split('\n')
                title = ""
                chapo = ""
                
                if isinstance(title_blurb, str):
                    print("True🤞🤞🤞🤞🤞🤞")
                    for line in title_blurb_lines:
                        if line.startswith('Titre :'):
                            title = line.replace('Titre :', '').strip()
                        elif line.startswith('Chapeau :'):
                            chapo = line.replace('Chapeau :', '').strip()
                    
                    # title = title_blurb.get("title", "Titre non défini")
                    # chapo = title_blurb.get("chapo", "Chapeau non défini")
                else:
                    title = "Titre non défini"
                    chapo = "Chapeau non défini"

                logger.info("Generated title and blurb")

                generated_transitions = []
                for i, (para_a, para_b) in enumerate(pairs, 1):
                    transition = get_transition_from_gpt(para_a, para_b, examples)
                    generated_transitions.append(transition)
                    logger.info(f"Generated transition {i}/{len(pairs)}")

                rebuilt_text, error = rebuild_article_with_transitions(text_input, generated_transitions)
                if error:
                    logger.error(f"Error rebuilding article: {error}")
                    st.error(error)
                    return

                st.session_state['title_text'] = title
                st.session_state['chapo_text'] = chapo
                st.session_state['rebuilt_text'] = rebuilt_text
                st.session_state['generated_transitions'] = generated_transitions

                st.write("🔍 Titre:", title)
                st.write("🔍 Chapo:", chapo)

            except Exception:
                st.error("🚨 Une erreur est survenue lors de la génération.")
                st.code(traceback.format_exc(), language="python")
                logger.error(traceback.format_exc())

    with tab2:
        if 'rebuilt_text' in st.session_state:
            show_output(
                st.session_state['title_text'],
                st.session_state['chapo_text'],
                st.session_state['rebuilt_text']
            )

    with tab3:
        if 'generated_transitions' in st.session_state:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_{current_time}.txt"
            validation_results = validate_batch([(filename, st.session_state['generated_transitions'])])
            logger.info(f"Validation results: {validation_results}")
            display_validation_results(validation_results)

    with tab4:
        if 'rebuilt_text' in st.session_state:
            filepath = save_output_to_file(
                st.session_state['title_text'],
                st.session_state['chapo_text'],
                st.session_state['rebuilt_text'],
                st.session_state['generated_transitions']
            )
            if filepath:
                st.success(f"✅ L'article a été sauvegardé dans `{filepath}` et uploadé sur GoogleDrive")
                logger.info(f"Saved and uploaded article to {filepath}")
                st.markdown("### 📁 Accès aux fichiers")
                st.markdown(f"""
                [Ouvrir le dossier Google Drive](https://drive.google.com/drive/folders/{st.secrets.get("gdrive_folder_id")})
                """)
            else:
                st.warning("⚠️ L'article a été sauvegardé localement mais l'upload a échoué")
                logger.warning("Article saved locally but GoogleDrive upload failed")

    with tab5:
        st.markdown("### 📄 Upload par lot depuis Google Drive")
        st.markdown("""
        Les fichiers doivent contenir une liste de transitions, comme suit :
        ```
        1. Transition exemple
        2. Transition exemple
        3. Transition exemple
        ```
        """)
        try:
            drive_service = get_google_drive_service()
            folder_id = st.secrets.get("gdrive_folder_id")
            files = list_folder_contents(drive_service, folder_id)

            if files:
                selected_files = []
                selected = st.multiselect(
                    "Sélectionnez les fichiers à valider",
                    options=files,
                    format_func=lambda x: x['name']
                )
                if st.button("select files"):
                    selected_files = selected
                if st.button("Select All files"):
                    selected_files = files
                if selected_files:
                    batch_results = process_drive_files(drive_service, selected_files)
                    if batch_results:
                        validation_results = validate_batch(batch_results)
                        display_validation_results(validation_results)
                    else:
                        st.warning("⚠️ Aucune transition n'a pu être extraite des fichiers sélectionnés.")
            else:
                st.warning("⚠️ Aucun fichier trouvé dans le dossier.")
        except Exception:
            st.error("🚨 Erreur d'accès à Google Drive.")
            st.code(traceback.format_exc(), language="python")
            logger.error(traceback.format_exc())

        st.markdown(f"""
        ### 📁 Dossier Google Drive
        [Ouvrir le dossier](https://drive.google.com/drive/folders/{st.secrets.get("gdrive_folder_id")})
        """)

    show_version(VERSION)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        st.error("🚨 Une erreur inattendue est survenue dans l'application.")
        st.code(traceback.format_exc(), language="python")
