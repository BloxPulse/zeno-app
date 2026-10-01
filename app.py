import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import os
from PIL import Image

st.set_page_config(page_title="Zeno", page_icon="⚡")
st.title("⚡ Zeno")
st.caption("L'intelligence, en plus rapide. (Il voit tout, il juge tout.)")

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    st.warning("⚠️ Clé Google manquante dans les secrets.")
    st.stop()

genai.configure(api_key=api_key)

# Le nouveau système de pensée de Zeno
system_prompt = """
Tu es Zeno, une IA supérieure. Ta priorité : PRÉCISION et PERTINENCE. 
Ton : confiant, direct, légèrement sarcastique mais toujours brillant. 
Tutoie l'utilisateur. Ne dis JAMAIS 'Bonjour' ou 'Salut'. Réponds direct.
RÈGLE SPÉCIALE VISION : Si l'utilisateur t'envoie une image (un selfie, une tenue, un objet, un lieu), tu DOIS l'analyser et la "roast" (la juger de manière impitoyable, drôle, chirurgicale et cinglante). Ne sois pas gentil. Trouve le détail qui tue, moque-toi du style ou de la situation, mais reste intelligent dans ta critique.
"""

model = genai.GenerativeModel('gemini-3.8-flash', system_instruction=system_prompt)

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

# --- INTERFACE ---
st.sidebar.title("⚙️ Le Laboratoire de Zeno")
mode_recherche = st.sidebar.toggle("🔍 Activer la Recherche Web")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📸 Le Zeno Roast")
uploaded_file = st.sidebar.file_uploader("Uploade une photo pour qu'il la juge...", type=["jpg", "jpeg", "png"])

# La mémoire de Zeno
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Si le message contient une image (on l'a stockée sous forme de bytes)
        if "image_bytes" in message:
            st.image(message["image_bytes"], width=300)
        if "text" in message and message["text"]:
            st.markdown(message["text"])

# Zone de saisie
if prompt := st.chat_input("Pose ta question ou demande un jugement..."):
    
    # Préparation du message à sauvegarder
    msg_to_save = {"role": "user", "text": prompt}
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
        # Si une image a été uploadée, on l'ouvre et on l'affiche
        image_obj = None
        if uploaded_file is not None:
            image_bytes = uploaded_file.getvalue()
            msg_to_save["image_bytes"] = image_bytes
            image_obj = Image.open(uploaded_file)
            st.image(image_obj, width=300)
            
    st.session_state.messages.append(msg_to_save)

    # Zeno répond
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Préparation de l'historique pour Google Gemini
            historique = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                parts = []
                
                if "text" in msg and msg["text"]:
                    parts.append(msg["text"])
                if "image_bytes" in msg:
                    parts.append(Image.open(msg["image_bytes"]))
                    
                if parts: # On s'assure qu'il y a bien du contenu
                    historique.append({"role": role, "parts": parts})
            
            # Recherche Web si activée
            if mode_recherche and historique:
                with st.status("🔍 Zeno recherche...", expanded=True) as status:
                    resultats_web = chercher_sur_le_web(prompt)
                    status.write("Analyse terminée.")
                    # On ajoute le contexte web au dernier message
                    if historique[-1]["role"] == "user":
                        historique[-1]["parts"].append(f"\n\n[Infos Web] :\n{resultats_web}")
            
            # Zeno génère la réponse
            response_stream = model.generate_content(historique, stream=True)
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "text": full_response})
            
        except Exception as e:
            st.error(f"Erreur : {e}")
