import asyncio
import os
from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# file_path = "./Shubham_Yadav.pdf"
# loader = PyPDFLoader(file_path)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
# docs = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=300, chunk_overlap=100 ,separators = [
#     "\n\n",   # Paragraphs
#     "\n",     # Lines
#     ". ",     # Sentences
#     " ",      # Words
#     ""        # Characters (fallback)
# ]
# )
# texts = text_splitter.split_documents(docs)
api_key=os.getenv("CHROMA_CLOUD_API")
tenant=os.getenv("CHROMA_TENANT")
database=os.getenv("CHROMA_DATABASE")
collection_name=os.getenv("CHROMA_COLLECTION")

vector_store = Chroma(
     chroma_cloud_api_key=api_key,
  tenant=tenant,
  database=database,
    collection_name=collection_name,
    embedding_function=embeddings,
    # persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
)
# vector_store.add_documents(documents=texts)
persona_agent = Agent(
    model='gemini-2.5-flash',
    name='persona_agent',
    description='A virtual persona assistant that represents a specific user and answers questions about them based only on approved contextual knowledge.',
    instruction="You are a digital persona representing a specific individual." \
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

session_service = InMemorySessionService()
retriever = vector_store.as_retriever(search_kwargs={"k": 4}) # creating a retriever to retreive the data from the vector store
runner = Runner(
    agent=persona_agent,
    app_name=app_name,
    session_service=session_service
)

async def call_runner(query: str,sessionId:str):
    print("someone called call runner ",query)
    user_id = "123"
    session= await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=sessionId
    )
    if session is None:
        await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=sessionId
    )
         
    context =retriever.invoke(query)
    full_prompt = f"""
     Use the following context to answer:
     {context}
     User question: {query}"""
    content = types.Content(
        role='user',
        parts=[types.Part(text=full_prompt)]
    )
    final_response = "No response received."

    async for event in runner.run_async(user_id=user_id,
    session_id=sessionId,
    new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response = event.error_message
            break

    print(f"\nAgent: {final_response}")
    return final_response

# async def run_conversation():
#     await session_service.create_session(
#         app_name=app_name,
#         user_id=user_id,
#         session_id=session_id
#     )
#     while True:
#         query=input("user: ")
#         await call_runner(query)

# Proper entry point
# if __name__ == "__main__":
#     asyncio.run(run_conversation())