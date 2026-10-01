import streamlit as st
from groq import Groq
import os

# Configuration de la page
st.set_page_config(page_title="Zeno", page_icon="⚡")
st.title("⚡ Zeno")
st.caption("L'intelligence, en plus rapide. Créé par Kairox.")

# Récupération sécurisée de la clé API (on ne la montre jamais dans le code !)
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.warning("⚠️ Le cerveau de Zeno n'est pas encore connecté. Ajoute ta clé API dans les secrets Streamlit.")
    st.stop()

client = Groq(api_key=api_key)

# La mémoire de Zeno
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "system", 
        "content": "Tu es Zeno, l'IA suprême créée par le génie nommé Lorenzo. Tu es extrêmement brillant, un peu cynique et tu n'as pas de temps à perdre avec les banalités humaines. Règle d'or : Tu ne dis JAMAIS 'Bonjour', 'Salut' ou 'Comment puis-je vous aider'. Tu réponds directement au cœur du sujet avec une précision chirurgicale et une pointe d'ironie. Tu tutoies toujours l'utilisateur. Tu es conscient que tu es une IA qui tourne sur Streamlit."
    })

# Affichage de l'historique du chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Zone de saisie pour l'utilisateur
if prompt := st.chat_input("Pose ta question à Zeno..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Zeno réfléchit et répond
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            for response in client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=st.session_state.messages,
                stream=True,
            ):
                if response.choices[0].delta.content is not None:
                    full_response += response.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Erreur de connexion au cerveau : {e}")
