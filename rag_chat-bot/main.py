import os
import streamlit as st
import json
from bson import ObjectId
import asyncio
from dotenv import load_dotenv
from structures.resturant import Restaurant
from structures.menu import MenuItem
from db.pinecone import upsert_data, fetch_data
from motor.motor_asyncio import AsyncIOMotorClient

from utils.generatePrompt import generatePrompt
from utils.llm import generate_content

# Load environment variables
load_dotenv()

uri = os.getenv("MONGODB_URI")

# MongoDB setup
client = AsyncIOMotorClient(uri)
db = client["zomato_rag"]
collection = db["zomato_collection"]

# Asyncio event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Upload function
async def upload_data():
    with open("../rag_chat-bot/knowledgebase.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for restaurant_data in data:
        menu_items_data = restaurant_data.pop("menu_items", [])
        
        if not isinstance(restaurant_data.get('cuisine'), str):
            restaurant_data['cuisine'] = ', '.join(restaurant_data['cuisine'])

        restaurant_obj = Restaurant(**restaurant_data, menu_items=[])
        restaurant_inserted = await collection.insert_one(restaurant_obj.dict())
        restaurant_id = restaurant_inserted.inserted_id

        restaurant_string = " ".join(f"{key}: {value}" for key, value in restaurant_data.items())
        await upsert_data(restaurant_string, str(restaurant_id), "resturant")

        for menu_item in menu_items_data:
            menu_item_obj = MenuItem(**menu_item, restaurant_id=str(restaurant_id))
            menu_item_inserted = await collection.insert_one(menu_item_obj.dict())
            menu_item_id = menu_item_inserted.inserted_id

            menu_item_string = " ".join(f"{key}: {value}" for key, value in menu_item.items())
            await upsert_data(menu_item_string, str(menu_item_id), "menu")

            collection.update_one(
                {"_id": restaurant_id},
                {"$push": {"menu_items": str(menu_item_id)}}
            )

# Helper to fetch and enrich documents
async def get_doc(entry):
    raw = entry.get('_id', '')
    parts = raw.split()
    raw_id, vector_type = parts[0], parts[-1].lower()

    try:
        oid = ObjectId(raw_id)
    except Exception as e:
        print(f"Error converting ID to ObjectId: {e}")
        return None

    doc = await collection.find_one({'_id': oid})
    if not doc:
        return None

    doc['_id'] = str(oid)
    doc['_score'] = entry.get('_score')
    doc['vector_type'] = vector_type

    if vector_type == 'resturant':
        menus = []
        for mid in doc.get('menu_items', []):
            try:
                m_oid = ObjectId(mid)
            except Exception as e:
                print(f"Error converting menu item ID: {e}")
                continue
            mdoc = await collection.find_one({'_id': m_oid})
            if mdoc:
                mdoc['_id'] = str(m_oid)
                menus.append(mdoc)
        doc['menus'] = menus
    elif vector_type == 'menu':
        parent = await collection.find_one({'menu_items': raw_id})
        if parent:
            parent['_id'] = str(parent['_id'])
            parent.pop('menu_items', None)
            doc['restaurant'] = parent

    return doc

# Chat function
async def chat_bot(message):
    try:
        data = await fetch_data(message)
    except Exception as e:
        return f"Error fetching from vector store: {e}"

    if not data:
        return "No matches found."

    docs = []
    first_type = data[0].get('_id', '').split()[-1].lower()
    if first_type == 'resturant':
        doc = await get_doc(data[0])
        if doc:
            docs.append(doc)
    elif first_type == 'menu':
        for entry in data:
            doc = await get_doc(entry)
            if doc:
                docs.append(doc)
    else:
        for entry in data[:2]:
            doc = await get_doc(entry)
            if doc:
                docs.append(doc)

    if not docs:
        return "No valid documents found."
    
    prompt = generatePrompt(message, docs)

    try:
        response = generate_content(prompt)
    except Exception as e:
        return f"Error generating content: {e}"

    if not response:
        return "No response generated."

    return response

# ---------------- STREAMLIT APP UI ----------------

st.set_page_config(page_title="Zomato RAG Chatbot", layout="wide")

# Header layout
col1, col2 = st.columns([2, 1])

with col1:
    st.title("Zomato RAG Chatbot")

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/1046/1046784.png", width=120)

# Sidebar - Admin Actions
with st.sidebar.expander("🛠️ Admin Actions"):
    if st.button("Upload Data"):
        with st.spinner("Uploading data..."):
            loop.run_until_complete(upload_data())
        st.success("✅ Data uploaded successfully!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("👋 Hi there! Ask me anything about restaurants, cuisines, or menu items!")

# Function to style user and assistant messages
def styled_message(message, role):
    if role == "user":
        st.markdown(f"<div style='color:blue; font-weight:bold;'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:green; font-weight:bold;'>{message}</div>", unsafe_allow_html=True)

# Chat history rendering
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        styled_message(msg["content"], msg["role"])

# User input
if user_input := st.chat_input("Ask me anything about restaurants..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        styled_message(user_input, "user")

    # Generate bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            bot_response = loop.run_until_complete(chat_bot(user_input))
            styled_message(bot_response, "assistant")

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
