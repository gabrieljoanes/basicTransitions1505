import random

def get_transition_from_gpt(para_a, para_b, examples, call_proxy, model="gpt-4"):
    """
    Generate a context-aware French transition (max 5 words)
    using few-shot prompting from the examples list and a proxy LLM call.
    """

    # Select 3 random few-shot examples
    selected_examples = random.sample(examples, min(3, len(examples)))

    system_prompt = (
        "Tu es un assistant de presse francophone. "
        "Ta tâche est d'insérer une transition brève et naturelle (5 mots maximum) "
        "entre deux paragraphes d'actualité régionale. "
        "La transition doit être journalistique, fluide, neutre et ne pas répéter les débuts comme 'Par ailleurs' ou 'Parallèlement' ou 'Sujet'. "
        "La dernière TRANSITION de l'article doit être une vraie conclusion, choisie uniquement parmi : "
        "Enfin, Et pour finir, Pour terminer, Pour finir, En guise de conclusion, En conclusion, "
        "En guise de mot de la fin, Pour clore cette revue, Pour conclure cette sélection, "
        "Dernier point à noter, Pour refermer ce tour d’horizon. "
        "Ces transitions de fin doivent apparaître une seule fois, uniquement en dernière position. "
        "Si tu utilises 'Par ailleurs', préfère étoffer : 'Par ailleurs, on annonce que', 'Par ailleurs, sachez que'. "
        "Évite l'expression 'en parallèle'."
    )

    # Format few-shot examples from 'input' and 'transition'
    fewshot = ""
    for ex in selected_examples:
        if "input" in ex and "TRANSITION" in ex["input"]:
            part_a, part_b = ex["input"].split("TRANSITION", 1)
            part_a = part_a.strip()
            part_b = part_b.strip()
        else:
            part_a = "MISSING A"
            part_b = "MISSING B"

        fewshot += f"Paragraphe A :\n\"\"\"{part_a}\"\"\"\n\n"
        fewshot += f"Paragraphe B :\n\"\"\"{part_b}\"\"\"\n\n"
        fewshot += f"Transition :\n{ex['transition']}\n\n"

    # Format current pair prompt
    current_prompt = f"""
{system_prompt}

Voici quelques exemples :

{fewshot}

Paragraphe A :
\"\"\"{para_a.strip()}\"\"\"

Paragraphe B :
\"\"\"{para_b.strip()}\"\"\"

Transition :
""".strip()

    try:
        return call_proxy(current_prompt, model=model)
    except Exception as e:
        return f"Erreur lors de la génération de la transition : {str(e)}"
