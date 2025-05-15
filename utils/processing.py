# utils/processing.py

import random

def get_transition_from_gpt(para_a, para_b, examples, client, model="gpt-4"):
    """
    Generate a context-aware French transition (max 5 words)
    using few-shot prompting from the examples list and OpenAI GPT.
    """
    # Select 3 random examples for few-shot context
    selected_examples = random.sample(examples, min(3, len(examples)))

    system_prompt = (
        "Tu es un assistant de presse francophone. "
        "Ta tâche est d'insérer une transition brève et naturelle (5 mots maximum) "
        "entre deux paragraphes d'actualité régionale. "
        "La transition doit être journalistique, fluide, neutre et ne pas répéter les débuts comme 'Par ailleurs'."
    )

    # Prepare messages for OpenAI chat completion
    messages = [{"role": "system", "content": system_prompt}]
    for ex in selected_examples:
        messages.append({"role": "user", "content": ex["input"]})
        messages.append({"role": "assistant", "content": ex["transition"]})

    # Add the real paragraph pair
    messages.append({
        "role": "user",
        "content": f"{para_a.strip()}\nTRANSITION\n{para_b.strip()}"
    })

    # Generate with OpenAI client
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=20
    )

    return response.choices[0].message.content.strip()
