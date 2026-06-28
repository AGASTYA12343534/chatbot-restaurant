from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

index_name = "chatboot"

def get_index():
    uri = os.getenv("PINECONE_API_KEY")
    if not uri or uri == "your_pinecone_api_key_here":
        raise ValueError("Pinecone API key is missing or not configured. Please set PINECONE_API_KEY in your .env file.")
    try:
        pc = Pinecone(api_key=uri)
        return pc.Index(index_name)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Pinecone Index: {e}")

async def upsert_data(text: str, id: str, type_item: str) -> None:
    """Pinecone util function to upsert data into the db."""
    try:
        index = get_index()
        if type_item == "menu":
            id = id + " menu"
        else:
            id = id + " resturant"
            
        index.upsert_records(
            namespace="Example",
            records=[
                {
                    "id": id,  # Same as that of mongoDB's Resturant or Menu item ID
                    "text": text,
                }
            ]
        )
        print("Data upserted successfully.")
        
    except Exception as e:
        raise e
    
async def fetch_data(
    query: str,
    top_k: int = 10
) -> list:
    """Pinecone util function to perform similarity search in the db."""
    try:
        index = get_index()
        query_payload = {
            "inputs": {
                "text": query
            },
            "top_k": top_k,
        }
        result = index.search(
            namespace="Example",
            query=query_payload
        )

        return result['result']['hits']
    
    except Exception as e:
        raise e