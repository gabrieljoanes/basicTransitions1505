import streamlit as st
import requests
import datetime

def show_openai_usage():
    st.header("📊 Suivi de l'utilisation OpenAI (API Key)")

    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.error("Aucune clé API trouvée dans `st.secrets[\"OPENAI_API_KEY\"]`")
        return

    # Date range: last 30 days
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    usage_url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(usage_url, headers=headers)
        response.raise_for_status()
        usage_data = response.json()

        total_usd = usage_data.get("total_usage", 0) / 100.0  # Convert from cents to dollars
        st.success(f"✅ Total dépensé entre {start_date} et {end_date} : **${total_usd:.2f}**")

    except Exception as e:
        st.error("Erreur lors de la récupération des données d'utilisation.")
        st.exception(e)

    # Display current pricing
    st.markdown("---")
    st.subheader("💵 Tarification standard des modèles")

    pricing = {
        "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03}
    }

    for model, rates in pricing.items():
        st.markdown(f"**{model}** — Prompt: ${rates['prompt']}/1K | Completion: ${rates['completion']}/1K")

