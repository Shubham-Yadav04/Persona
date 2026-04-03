
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
from matplotlib.style import context

load_dotenv()

# file_path = "./Shubham_Yadav.pdf"
# loader = PyPDFLoader(file_path)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

api_key=os.getenv("CHROMA_CLOUD_API")
tenant=os.getenv("CHROMA_TENANT")
database=os.getenv("CHROMA_DATABASE")
collection_name=os.getenv("CHROMA_COLLECTION","Persona")
print(api_key, tenant, database, collection_name , " let see the logs")
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
retriever = vector_store.as_retriever(search_kwargs={"k": 2}) # creating a retriever to retreive the data from the vector store
runner = Runner(
    agent=persona_agent,
    app_name=app_name,
    session_service=session_service
)
async def response_generator(session_id: str, query: str):
    print("someone called call runner", query)

    user_id = "123"

    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    if session is None:
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

    context = retriever.invoke(query)
  
    full_prompt = f"""
    Use the following context to answer:
    {context}
    User question: {query}
    """

    content = types.Content(
        role='user',
        parts=[types.Part(text=full_prompt)]
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.content and event.content.parts:
            yield event.content.parts[0].text

        if event.actions and event.actions.escalate:
            yield f"[ERROR]: {event.error_message}"

        if event.is_final_response():
            break