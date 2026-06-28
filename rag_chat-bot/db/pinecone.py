from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

uri=os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key = uri)

# Create a dense index with integrated inference
# index_name = "llama-text-embed-v2"
index_name = "chatboot"

# pc.create_index_for_model(
#     name=index_name,
#     cloud="aws",
#     region="us-east-1",
#     embed={
#         "model": "llama-text-embed-v2",
#         "field_map": {
#             "text": "text"  # Map the record field to be embedded
#         }
#     }
# )

index = pc.Index(index_name)

async def upsert_data(text: str, id: str, type_item: str) -> None:
    """Pinecone util function to upsert data into the db."""
    try:
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