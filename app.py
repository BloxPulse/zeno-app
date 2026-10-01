import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import os

st.set_page_config(page_title="Zeno", page_icon="⚡")
st.title("⚡ Zeno")
st.caption("L'intelligence, en plus rapide.")

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    st.warning("⚠️ Clé OpenRouter manquante dans les secrets.")
    st.stop()

# Connexion à OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def chercher_sur_le_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4, region="fr-fr"))
            if results:
                contexte = "".join([f"Titre: {r['title']}\nExtrait: {r['body']}\n\n" for r in results])
                return contexte
            return "Aucun résultat pertinent."
    except Exception as e:
        return f"Erreur recherche: {e}"

st.sidebar.title("⚙️ Paramètres")
mode_recherche = st.sidebar.toggle("🔍 Activer la Recherche Web")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "system", 
        "content": "Tu es Zeno, une IA supérieure. Ta priorité : PRÉCISION et PERTINENCE. Analyse en profondeur. Utilise les infos web pour des réponses expertes et structurées. Ton : confiant, direct, légèrement sarcastique mais toujours brillant. Tutoie l'utilisateur. Ne dis jamais 'Bonjour'."
    })

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Pose ta question à Zeno..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            messages_pour_ia = st.session_state.messages.copy()
            
            if mode_recherche:
                with st.status("🔍 Zeno recherche...", expanded=True) as status:
                    resultats_web = chercher_sur_le_web(prompt)
                    status.write("Analyse terminée.")
                    messages_pour_ia.append({
                        "role": "system", 
                        "content": f"Informations du web à utiliser pour répondre avec précision :\n\n{resultats_web}"
                    })
            
                        # Utilisation de Gemini Flash (Gratuit via OpenRouter)
            stream = client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=messages_pour_ia,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Erreur : {e}")
