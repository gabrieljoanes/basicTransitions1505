import random

def get_transition_from_gpt(para_a, para_b, examples, client, model="gpt-4"):
    """
    Generate a context-aware French transition (max 5 words)
    using few-shot prompting from the examples list and OpenAI GPT.

    Parameters:
    - para_a: str, first paragraph
    - para_b: str, second paragraph
    - examples: list of dicts with 'input' and 'output'
    - client: OpenAI client
    - model: str, OpenAI model name (default 'gpt-4')

    Returns:
    - str: generated transition
    """

    # Select up to 3 random examples
    selected_examples = random.sample(examples, min(3, len(examples)))

    system_prompt = (
        "Tu es un assistant de presse francophone. "
        "Ta tâche est d'insérer une transition brève et naturelle (5 mots maximum) "
        "entre deux paragraphes d'actualité régionale. "
        "La transition doit être journalistique, fluide, neutre et ne pas répéter les débuts comme 'Par ailleurs' ou 'Parallèlement' ou 'Sujet'. "
        "La dernière transition dans l’article doit absolument être une transition de clôture. Utilise exclusivement l'une des expressions suivantes : "
        "Enfin, Et pour finir, Pour terminer, Pour finir, En guise de conclusion, En conclusion, En guise de mot de la fin, Pour clore cette revue, "
        "Pour conclure cette sélection, Dernier point à noter, Pour refermer ce tour d’horizon. Ces transitions de fin ne doivent apparaître qu’une seule fois, "
        "et uniquement à la toute fin de l’article. "
        "Si tu veux utiliser 'Par ailleurs', préfère des variantes enrichies comme : 'Par ailleurs, on annonce que', ou 'Par ailleurs, sachez que'. "
        "Évite complètement l’usage de 'En parallèle'."
    )

    # Build the chat messages
    messages = [{"role": "system", "content": system_prompt}]
    for ex in selected_examples:
        messages.append({"role": "user", "content": ex["input"]})
        messages.append({"role": "assistant", "content": ex["output"]})

    # Add actual paragraph pair
    messages.append({
        "role": "user",
        "content": f"{para_a.strip()}\nTRANSITION\n{para_b.strip()}"
    })

    # Query OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=20
    )

    return response.choices[0].message.content.strip()
