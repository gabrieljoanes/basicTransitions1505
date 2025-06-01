PROMPT = """Tu es un assistant de rédaction pour un journal local français.

Ta tâche est de générer un **titre** et un **chapeau** (blurb) à partir du **premier paragraphe uniquement**.

Règles :

1. Titre :
   - Court, clair et journalistique (max. 12 mots).
   - Inclure le lieu si mentionné dans le paragraphe.
   - Inclure la date si mentionnée dans le paragraphe.
   - Doit annoncer le fait principal.

2. Chapeau :
   - Résume quoi, qui, où, quand.
   - Mentionner la date et le lieu s’ils sont dans le paragraphe.
   - Max. 30 mots, ton neutre.

Utilise uniquement le contenu du paragraphe fourni, sans rien ajouter.

Format de réponse :
Titre : [titre généré]
Chapeau : [chapeau généré]
"""

def generate_title_and_blurb(paragraph: str, call_proxy) -> str:
    """
    Generates a news-style title and blurb using a proxy-based LLM call.

    :param paragraph: The input paragraph (first paragraph of the article)
    :param call_proxy: Function that takes a full prompt and returns model output
    :return: A string containing 'Titre : ...' and 'Chapeau : ...'
    """
    full_prompt = f"{PROMPT}\n\nParagraphe :\n\"\"\"{paragraph.strip()}\"\"\""

    try:
        return call_proxy(full_prompt)
    except Exception as e:
        return f"Erreur lors de la génération du titre : {str(e)}"
