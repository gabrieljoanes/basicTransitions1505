# utils/processing.py

def generate_unique_transitions(transitions, needed):
    """
    Selects up to `needed` transitions from the list,
    ensuring no word is repeated across the selected phrases.
    """
    used_words = set()
    results = []

    for t in transitions:
        words = set(t.lower().split())
        if used_words.isdisjoint(words):
            results.append(t)
            used_words.update(words)
        if len(results) == needed:
            break

    return results
