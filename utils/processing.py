import random

def get_transition_from_gpt(para_a, para_b, examples, client, is_last=False, model="gpt-4-turbo", max_examples=100):
    """
    Generate a context-aware French transition (max 5 words)
    using few-shot prompting from the examples list and OpenAI GPT.
    Returns: transition (str), prompt_tokens (int), completion_tokens (int)
    """

    selected_examples = random.sample(examples, min(max_examples, len(examples)))

    closing_transitions = [
        "Enfin", "Et pour finir", "Pour terminer", "Pour finir", "En guise de conclusion", "En conclusion",
        "En guise de mot de la fin", "Pour clore cette revue", "Pour conclure cette sélection",
        "Dernier point à noter", "Pour refermer ce tour d’horizon"
    ]

    def is_valid_closing_transition(text):
        return any(text.strip().lower().startswith(valid.lower()) for valid in closing_transitions)

    base_prompt = (
        "Tu es un assistant de presse francophone. "
        "Ta tâche est d'insérer une transition brève et naturelle (5 mots maximum) "
        "entre deux paragraphes d'actualité régionale. "
        "La transition doit être journalistique, fluide, neutre et ne pas répéter les débuts comme 'Par ailleurs', 'Parallèlement', ou 'Sujet'. "
        "Si tu veux utiliser 'Par ailleurs', préfère des variantes enrichies comme : 'Par ailleurs, on annonce que', ou 'Par ailleurs, sachez que'. "
        "Évite complètement l’usage de 'En parallèle'. "
    )

    if is_last:
        base_prompt += (
            "Cette transition est la toute dernière de l'article. "
            "Tu dois obligatoirement choisir une transition de fin dans cette liste : "
            f"[{', '.join(closing_transitions)}]. "
        )
    else:
        base_prompt += (
            "Cette transition n’est pas la dernière. "
            f"N’utilise aucune des transitions suivantes : [{', '.join(closing_transitions)}]. "
        )

    messages = [{"role": "system", "content": base_prompt}]
    for ex in selected_examples:
        messages.append({"role": "user", "content": ex["input"]})
        messages.append({"role": "assistant", "content": ex["output"]})
    messages.append({
        "role": "user",
        "content": f"{para_a.strip()}\nTRANSITION\n{para_b.strip()}"
    })

    max_attempts = 5
    for _ in range(max_attempts):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_tokens=20
        )

        transition = response.choices[0].message.content.strip()
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens

        if not is_last or is_valid_closing_transition(transition):
            return transition, prompt_tokens, completion_tokens

    return random.choice(closing_transitions) + ",", 0, 0
