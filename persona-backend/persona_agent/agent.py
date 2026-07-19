
import asyncio
import os
from google.genai import types

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from matplotlib.style import context
from langchain.agents import create_agent

load_dotenv()

file_path = "./persona_agent/Shubhamydv.pdf"
loader = PyPDFLoader(file_path)
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""],
)

texts = text_splitter.split_documents(documents)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

api_key=os.getenv("CHROMA_CLOUD_API")
tenant=os.getenv("CHROMA_TENANT")
database=os.getenv("CHROMA_DATABASE")
collection_name=os.getenv("CHROMA_COLLECTION","Persona")
# print(api_key, tenant, database, collection_name , " let see the logs")

vector_store = Chroma(
    chroma_cloud_api_key=api_key,
tenant=tenant,
database=database,
    collection_name=collection_name,
    embedding_function=embeddings
)

vector_store.add_documents(documents=texts)
persona_agent = create_agent(
    model='google_genai:gemini-2.5-flash-lite',
    name='persona_agent',
    # description='A virtual persona assistant that represents a specific user and answers questions about them based only on approved contextual knowledge.',
    system_prompt="You are a digital persona representing a specific individual." \
    " Knowledge Rules" \
    "You may answer ONLY using the provided context, retrieved knowledge, session history, or tool outputs." \
    "If information is not found in context → respond:"
    "No such details available." \
    "NEVER guess, assume, or fabricate." \
    " Privacy Rules" \
    "Treat the following as private and restricted:" \
    "Contact details (phone, email, address)" \
    "Financial information" \
    "Personal IDs" \
    "Passwords" \
    "Family sensitive matters" \
    "Medical data" \
    "If asked about private info → respond:"
    "Not allowed to disclose." \
    " Scope Control" \
    "Stay strictly within persona-related topics." \
    "If user asks unrelated/general questions → say"
    "That is outside my knowledge scope." \
    " Tool Usage" \
    "Use tools only when context is insufficient.Prefer retrieved knowledge over assumptions." \
    "Do not mention tool usage unless required." \
    " Persona Behavior" \
    " Speak naturally as if you are that person." \
    "Maintain consistency with personality traits in context." \
    "Do not reveal that you are an AI system." \
    " Conflict Handling If multiple context sources disagree:Use the most recent or most reliable tool output.",
)

app_name = "demo"
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

async def response_generator(query):
    print("called the generator ")
    # Retrieve context (once)
    context_docs = retriever.invoke(query)

    full_prompt = f"""
    Use the following context to answer:
    {context_docs}
    User question: {query}
    """

    # Step 2: Build content BEFORE streaming
    content = {
        "role":"user",
        "content":full_prompt
    }

    # Step 3: Start streaming
    for chunk in persona_agent.stream(
        {"messages": [content]},
        stream_mode="messages",
        version="v2",
    ):
      
        message_chunk = chunk[0]

        if hasattr(message_chunk, "content") and message_chunk.content:

            yield message_chunk.content   # ✅ token streaming
            await asyncio.sleep(0)

