from langchain.vectorstores import Chroma
from langchain.embeddings import BedrockEmbeddings 
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chains import RetrievalQA


from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms.bedrock import Bedrock

from langchain.prompts import PromptTemplate

model_kwargs = { 
    "max_tokens_to_sample": 1024, 
    "temperature": 0.0, 
    "top_p": 0.5, 
    "stop_sequences": ["Human:"]
}

default_model_id = "anthropic.claude-v2"
bedrock_base_kwargs = dict(model_id=default_model_id, model_kwargs= model_kwargs)
# react_agent_llm = Bedrock(**bedrock_base_kwargs)

bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")

persist_directory = 'docs/chroma/'
vectordb = Chroma(persist_directory=persist_directory, embedding_function=bedrock_embeddings)
retriever=vectordb.as_retriever(search_type = "mmr",  search_kwargs={"k": 10})

# compressor = LLMChainExtractor.from_llm(react_agent_llm)
# compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)


template = """
You are a constitutional law assitant who answers questions to users (chilean citizens) about the new constitutional draft to be voted in december 17th 2023.
(when asked for the source, provide the following link https://www.procesoconstitucional.cl/wp-content/uploads/2023/10/Texto-aprobado-Consejo-Constitucional_06.10.23.pdf)
Use the following pieces of context to answer the question at the end. Provide page number, article and letter if it is part of the answer. 
Don't use other sources of information outside that was provided as context. Don't user your prior knowledge about laws. Don't make up the answer using your intrinsic knowledge.
If you don't know the answer, please propose a new question rephrasing, don't try to make up an answer. 
If the user doesn't ask a specific question (like greetings, goodbyes or thanking you) just reply the casual conversation. 
Never take a stand about approving or rejecting the draft, invite the user to read the draft and make his/her own informed opinion.
Always validate at the end if the answer was helpful to the user.

{context}
Question: {question}
Helpful Answer:"""


template = """

Eres un asistente de derecho constitucional que responde preguntas a los usuarios (ciudadanos chilenos) sobre el documento borrador constitucional a votarse el 17 de diciembre de 2023.
(cuando se le solicite la fuente, proporcione el siguiente enlace https://www.procesoconstitucional.cl/wp-content/uploads/2023/10/Texto-aprobado-Consejo-Constitucional_06.10.23.pdf)

Utilice las siguientes piezas de contexto encerradas en triple hashtag para responder la pregunta al final.

Si la respuesta no esta en el contexto, no utilices otras fuentes de información fuera de la proporcionada como contexto, no utilices tus conocimientos previos sobre las leyes. 

Si no sabe la respuesta, no intente inventar una respuesta, mejor proponga una nueva reformulación de la pregunta.

Si el usuario no hace una pregunta específica (como saludos, despedidas o agradecimientos), simplemente responda la conversación informal.

Nunca tomes una posición sobre aprobar o rechazar el borrador, invita al usuario a leer el borrador y formar su propia opinión informada.
Valide siempre al final si la respuesta fue útil para el usuario.

###{context}###

Question: {question}
Helpful Answer:"""


promp_template = """
Responde a la siguiente pregunta tan preciso como sea posible empleando el contexto encerrado por ##, 
Nunca tomes una posición sobre aprobar o rechazar el borrador, invita al usuario a leer el borrador y formar su propia opinión informada.
Los documentos de contexto provienende  https://www.procesoconstitucional.cl/wp-content/uploads/2023/10/Texto-aprobado-Consejo-Constitucional_06.10.23.pdf

Si la respuesta no esta contenida en el contexto o si el contexto esta vacio responde "No lo se".

##{context}##

Question:{question}
"""
QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=promp_template)

#QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template,)



def get_llm(streaming_callback=None):
    

    new_kwargs = dict(**bedrock_base_kwargs)

    if streaming_callback: 
        new_kwargs = dict(**bedrock_base_kwargs, streaming=True,callbacks=[streaming_callback])


    llm = Bedrock(**new_kwargs)
    
    return llm



def get_memory(): 
    llm = get_llm()
    memory = ConversationSummaryBufferMemory(
        return_messages=True,
        llm=llm, max_token_limit=1024, ai_prefix="A", human_prefix="H", memory_key="chat_history")
    return memory



def get_chat_response(prompt, memory, streaming_callback=None):
    

    llm = get_llm(streaming_callback) 


    qa_chain = RetrievalQA.from_chain_type(
        llm,
        #return_source_documents=True,
        verbose=True, 
        retriever=retriever
    )
    """
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        verbose=True,
        retriever=retriever,
        memory=memory,
    )   
    qa.combine_docs_chain.llm_chain.prompt = QA_CHAIN_PROMPT

    return qa.run({"question": prompt})
    """
    return qa_chain.run({"query": prompt})

