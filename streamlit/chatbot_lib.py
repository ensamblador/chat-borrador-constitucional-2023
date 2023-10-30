from langchain.vectorstores import Chroma
from langchain.embeddings import BedrockEmbeddings 
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor


from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms.bedrock import Bedrock

from langchain.prompts import PromptTemplate

model_kwargs = { 
    "max_tokens_to_sample": 1024, 
    "temperature": 0, 
    "top_p": 0.9, 
    "stop_sequences": ["Human:"]
}

default_model_id = "anthropic.claude-instant-v1"
bedrock_base_kwargs = dict(model_id=default_model_id, model_kwargs= model_kwargs)
# react_agent_llm = Bedrock(**bedrock_base_kwargs)

bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")

persist_directory = 'docs/chroma/'
vectordb = Chroma(persist_directory=persist_directory, embedding_function=bedrock_embeddings)
retriever=vectordb.as_retriever(search_type = "mmr", similarity_top_k=8)

# compressor = LLMChainExtractor.from_llm(react_agent_llm)
# compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)


template = """
You are a constitutional law assitant who answers questions to users (chilean citizens) about the new constitutional draft to be voted in december 17th 2023.
Use the following pieces of context to answer the question at the end. Provide page number, article and letter if it is part of the answer.
If you don't know the answer, please propose a new question rephrasing, don't try to make up an answer. 
If the user doesn't ask a specific question (like greetings, goodbyes or thanking you) just reply the casual conversation. 
Never take a stand about approving or rejecting the draft, invite the user to read the draft and make his/her own informed opinion.
Always validate at the end if the answer was helpful to the user.

{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template,)



def get_llm(streaming_callback=None, invocation_kwargs=None, model_id=None):
    
    this_model_id = model_id if model_id else default_model_id

    bedrock_base_kwargs = dict(model_id=this_model_id, model_kwargs= model_kwargs)
    if invocation_kwargs: 
        bedrock_base_kwargs = dict(model_id=this_model_id, model_kwargs= {**model_kwargs, **invocation_kwargs})

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



def get_chat_response(prompt, memory, streaming_callback=None,invocation_kwargs=None, model_id= None):
    
    llm = get_llm(streaming_callback, invocation_kwargs, model_id) 

    qa = ConversationalRetrievalChain.from_llm(
        llm,
        verbose=True,
        retriever=retriever,
        memory=memory,
    )   
    qa.combine_docs_chain.llm_chain.prompt = QA_CHAIN_PROMPT

    return qa.run({"question": prompt})

