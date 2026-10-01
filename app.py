import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import os

st.set_page_config(page_title="Zeno", page_icon="⚡")
st.title("⚡ Zeno")
st.caption("L'intelligence, en plus rapide.")

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    st.warning("⚠️ Clé Google manquante dans les secrets.")
    st.stop()

# Connexion à Google Gemini
genai.configure(api_key=api_key)

# Le système de pensée de Zeno
system_prompt = """
Tu es Zeno, une IA supérieure. Ta priorité : PRÉCISION et PERTINENCE. Analyse en profondeur. 
Utilise les infos web pour des réponses expertes et structurées. 
Ton : confiant, direct, légèrement sarcastique mais toujours brillant. 
Tutoie l'utilisateur. Ne dis jamais 'Bonjour' ou 'Salut'. Réponds direct.
"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)

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

# Affichage de l'historique
for message in st.session_state.messages:
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
            # Préparation de l'historique pour Google
            historique = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                historique.append({"role": role, "parts": [msg["content"]]})
            
            # Recherche Web si activée
            if mode_recherche:
                with st.status("🔍 Zeno recherche...", expanded=True) as status:
                    resultats_web = chercher_sur_le_web(prompt)
                    status.write("Analyse terminée.")
                    # On ajoute le contexte web à la dernière question de l'utilisateur
                    if historique and historique[-1]["role"] == "user":
                        historique[-1]["parts"][0] += f"\n\n[Infos Web] :\n{resultats_web}"
            
            # Zeno répond
            response_stream = model.generate_content(historique, stream=True)
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Erreur : {e}")
