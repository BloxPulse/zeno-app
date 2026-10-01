import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os

# Configuration de la page
st.set_page_config(page_title="Zeno", page_icon="⚡")
st.title("⚡ Zeno")
st.caption("L'intelligence, en plus rapide.")

# Récupération sécurisée de la clé API
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.warning("⚠️ Le cerveau de Zeno n'est pas encore connecté.")
    st.stop()

client = Groq(api_key=api_key)

# --- LA FONCTION MAGIQUE : RECHERCHE WEB ---
def chercher_sur_le_web(query):
    try:
        with DDGS() as ddgs:
            # On cherche les 3 meilleurs résultats en français
            results = list(ddgs.text(query, max_results=3, region="fr-fr"))
            if results:
                # On assemble les résultats pour que l'IA puisse les lire
                contexte = ""
                for r in results:
                    contexte += f"Titre: {r['title']}\nExtrait: {r['body']}\n\n"
                return contexte
            return "Aucun résultat pertinent trouvé sur le web."
    except Exception as e:
        return f"Erreur lors de la recherche web: {e}"

# --- INTERFACE ET PARAMÈTRES ---
st.sidebar.title("⚙️ Paramètres de Zeno")
mode_recherche = st.sidebar.toggle("🔍 Activer la Recherche Web")

# La mémoire de Zeno
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "system", 
        "content": "Tu es Zeno, une intelligence artificielle supérieure. Ton but est d'être le plus BRILLANT, EXACT et UTILE possible. Tu as un ton confiant, direct et légèrement sarcastique, mais tu ne sacrifies JAMAIS la qualité de la réponse pour faire une blague. Tu donnes des solutions concrètes et expertes. Tu tutoies l'utilisateur et tu vas droit au but sans jamais dire 'Bonjour'."
    })

# Affichage de l'historique
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Pose ta question à Zeno..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Zeno répond
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # On prépare la liste des messages à envoyer à l'IA
            messages_pour_ia = st.session_state.messages.copy()
            
            # SI LE MODE RECHERCHE EST ACTIVÉ
            if mode_recherche:
                with st.status("🔍 Zeno recherche sur le web...", expanded=True) as status:
                    resultats_web = chercher_sur_le_web(prompt)
                    status.write("Recherche terminée. Zeno analyse les informations.")
                    
                    # On injecte les résultats du web dans le cerveau de Zeno
                    messages_pour_ia.append({
                        "role": "system", 
                        "content": f"Voici des informations trouvées sur le web concernant la question de l'utilisateur. Utilise-les pour répondre de manière experte, précise et à jour :\n\n{resultats_web}"
                    })
            
            # Zeno génère la réponse
            for response in client.chat.completions.create(
                model="qwen/qwen3.8-27b", # Le nouveau modèle ultra-logique
                messages=messages_pour_ia,
                stream=True,
            ):
                if response.choices[0].delta.content is not None:
                    full_response += response.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Erreur de connexion au cerveau : {e}")
