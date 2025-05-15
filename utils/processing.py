# utils/processing.py

from openai import OpenAI
import random

client = OpenAI()  # This will automatically use the API key from environment or Streamlit secrets

def get_transition_from_gpt(para_a, para_b, examples, model="gpt-4"):
    """
    Generate a short, 5-word French transition between para_a and para_b
    using GPT and few-shot examples from your dataset.
    """

    selected_examples = random.sample(examples, min(3, len(examples)))

    system_prompt = (
        "Tu es un assistant de presse francophone. "
        "Ta tâche est d'insérer une transition brève et naturelle (5 mots maximum) "
        "entre deux paragraphes d'actualité régionale. "
        "La transition doit être journalistique, fluide, neutre et ne doit pas répéter les débuts comme 'Par ailleurs'."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for shot in selected_examples:
        messages.append({"role": "user", "content": shot["input"]})
        messages.append({"role": "assistant", "content": shot["transition"]})

    messages.append({
        "role": "user",
        "content": f"{para_a.strip()}\nTRANSITION\n{para_b.strip()}"
    })

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=20
    )

    return response.choices[0].message.content.strip()
