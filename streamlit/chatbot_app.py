import os
import streamlit as st #all streamlit commands will be available through the "st" alias
import chatbot_lib as glib #reference to local lib script
from langchain.callbacks import StreamlitCallbackHandler

# https://github.com/pop-srw/streamlit-cognito-auth
from streamlit_cognito_auth import CognitoAuthenticator


st.set_page_config(page_title="Amazon Bedrock") #HTML title


pool_id = os.environ.get("POOL_ID")
app_client_id = os.environ.get("APP_CLIENT_ID")
app_client_secret = os.environ.get("APP_CLIENT_SECRET")

authenticator = CognitoAuthenticator(
    pool_id=pool_id,
    app_client_secret=app_client_secret,
    app_client_id=app_client_id,
)

is_logged_in = authenticator.login()
if not is_logged_in:
    st.stop()


def logout():
    authenticator.logout()

st.markdown("## Chatea con el Borrador de Constitucion") #page title

with st.sidebar:
    st.button("Logout", "logout_btn", on_click=logout)



st.sidebar.markdown("""# Hola
Este es un chatbot que utiliza técnicas de Inteligencia Artificial para consultar el [borrador constitucional](https://www.procesoconstitucional.cl/wp-content/uploads/2023/10/Texto-aprobado-Consejo-Constitucional_06.10.23.pdf)
y responder las preguntas realizadas por ti. 

Intenta hacer preguntas de tu interés. Revisa el página, artículo y letra mencionado en profundidad. Recuerda que este chabot no tiene una postura (a favor o encontra) respecto al texto, 
lo que busca que puedas formar tu propia opinión.

""")


if 'memory' not in st.session_state: #see if the memory hasn't been created yet
    st.session_state.memory = glib.get_memory() #initialize the memory
    #st.session_state.memory.human_prefix = "H"
    #st.session_state.memory.ai_prefix = "A"


if 'chat_history' not in st.session_state: #see if the chat history hasn't been created yet
    st.session_state.chat_history = [] #initialize the chat history


#Re-render the chat history (Streamlit re-runs this script, so need this to preserve previous chat messages)
for message in st.session_state.chat_history: #loop through the chat history
    with st.chat_message(message["role"]): #renders a chat line for the given role, containing everything in the with block
        st.markdown(message["text"]) #display the chat content


input_text = st.chat_input("Chat with your bot here") #display a chat input box

if input_text: #run the code in this if block after the user submits a chat message
    
    with st.chat_message("user"): #display a user chat message
        st.markdown(input_text) #renders the user's latest message
    
    st.session_state.chat_history.append({"role":"user", "text":input_text}) #append the user's latest message to the chat history
    

    placeholder =  st.empty()


    chat_message = placeholder.chat_message("assistant")
    st_callback = StreamlitCallbackHandler(chat_message )



    with chat_message: #display a bot chat message
        chat_response = glib.get_chat_response(
            prompt=input_text,
            memory=st.session_state.memory,
            streaming_callback=st_callback
            )
        
    placeholder.empty()
        
    st.chat_message("assistant").write(chat_response,) #display bot's latest response


    st.session_state.chat_history.append({"role":"assistant", "text":chat_response}) #append the bot's latest message to the chat history
    