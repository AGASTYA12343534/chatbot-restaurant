# Restaurant-Gen-AI-Chat Bot
#### A smart solution for all your cravings: easily explore and satisfy your inquiries through a smooth, user-friendly interface.

# Demo Vedio
Demo vedio]((https://www.youtube.com/watch?v=1NKOmnRl_bA))


## 1. Web Scraper Component and Knowledge Base Creation 

It consists of three Python scripts:
- `menu_scraper.py` — Scrapes menu items, descriptions, prices, and special attributes.
- `info_scraper.py` — Scrapes general restaurant information like name, address, hours, phone, and images.
- `format.py` — Cleans, formats, and combines scraped data into a unified structured JSON.


### 1. Web Scraping
Instead of manually collecting restaurant data, we automate it by scraping multiple restaurant websites.  
We capture:
- Restaurant name , address, timings and contact details.
- Menu items with:
  - Description
  - Price
  - Dietary options (e.g., vege tarian/non-vegetarian)
  - Spice level (if available)

Both `menu_scraper.py` and `info_scraper.py` takes care of following : 

- Implementing error handling to avoid crashes if some fields are missing.
- Respect the site's `robots.txt` to avoid scraping restricted areas.
- Organize extracted data into clean intermediate JSON files.

---

### 2. Knowledge Base Creation

Once raw data is scraped:
- `format.py` processes both the **restaurant info** and the **menu items**.
- It **normalizes** the text (removing extra spaces, cleaning HTML artifacts).
- It **indexes** data efficiently, associating each restaurant with its menu.
- It finally generates a structured `knowledgebase.json`, ready for future chatbot integration.

### Below is the `knowledgebase.json` structure
Restaurant data (per restaurant):

```
{
    "name": "...",
    "menu_items": [...],
    "dietary_options": "...",
    "price_range": "...", 
    "address": "...",
    "opening_hours": "...",
    "image_url": "...",
    "phone_number": "..."
}
```
Menu Item Data (per dish):

```
{
    "name": "...",
    "description": "...",
    "price": "amount in rupees",
    "attributes": {
        "veg_nonveg": "...",
        "category": "...",
        "spice_level": 0/1/2 based on spices
    }
}
```
## 3. RAG Chatbot 
### Overview of component

A chatbot that uses Retrieval-Augmented Generation (RAG) architecture to answer restaurant and menu-related queries, backed by a Pinecone database and Hugging Face LLMs.
Built with Streamlit for a simple and clean UI.

### Features

1. Menu item availability and details
2. Restaurant feature comparisons
3. Price range inquiries
4. Dietary restriction information
5. Handles ambiguous and out-of-scope queries
6. Maintains basic conversation history

### Project Structure
```
db/
  └── pinecone.py
structures/
  ├── menu.py
  └── resturant.py
utils/
  ├── generatePrompt.py
  └── llm.py
.env
knowledgebase.json
main.py
requirements.txt
```
### Functionality of each component
1. Database (`pinecone.py`)
- Manages embeddings storage and retrieval using Pinecone.

2. Structures (`menu.py` and `restaurant.py`)
- **`menu.py`**: Handles menu items, prices, and dietary tags.
- **`restaurant.py`**: Handles restaurant features for comparison.

3. Utilities (`llm.py` and `generatePrompt.py`)
- **`llm.py`**: Interfaces with a Hugging Face LLM to generate responses.
- **`generatePrompt.py`**: Builds structured prompts for the LLM.

4. Main Application (`main.py`)
- Hosts the Streamlit app UI for chatbot interaction.

5. Knowledge Base (`knowledgebase.json`)
- JSON file containing restaurant and menu information for embedding.

6. Environment Configuration (`.env`)
- Stores API keys and private configurations securely.

### System workflow
```
flowchart TD
    A[User Query] --> B[Retrieve relevant data from Pinecone]
    B --> C[Generate prompt using retrieved data]
    C --> D[Send prompt to Hugging Face LLM]
    D --> E[LLM generates a natural language response]
    E --> F[Display response in Streamlit UI]
```

# Project Workflow
![ChatGPT Image Apr 27, 2025, 12_37_37 PM](https://github.com/user-attachments/assets/521f7633-93c4-4d17-abaf-82e8a28f763d)

# Installation and setup guide

### Clone the repository
```
https://github.com/apoorv1110/Zomato-Gen-AI-Internship-Assignment.git
```
### Install dependencies
```
pip install -r requirements.txt
```

## Move into the directory

### Web Scraping Component

```
cd web scraper component
```
Run web scraping python Files

```
python3 run main.py
```
It will create a restaurant.json with unfiltered data

Format and generate the knowledge base:
```
python3 format.py
```
It will create a Knowledgebase.json with cleaned data

### RAG Chatbot

```
cd RAG_CHAT-BOT
```

Set up environment variable
```
PINECONE_API_KEY=your_pinecone_key
MONGODB_URI=your_mongodb_cluster_uri
GEMINI_API_KEY = your_free_gemini_api_key
```
Running the streamlit application
```
streamlit run main.py
```
Streamlit application will start running on local hoat and a UI like below will get opened up
- For the first time to start chatbot , click on Upload data under admin actions button
- This will enable the LLM to use data for information retrieval
- Once the data is uploaded successfully you can use chatbot for your queries

<img width="1280" alt="Screenshot 2025-04-27 at 12 16 03 PM" src="https://github.com/user-attachments/assets/03643da7-fbb8-47c2-9c23-a7a36754974b" />
<img width="1280" alt="Screenshot 2025-04-27 at 12 29 28 PM" src="https://github.com/user-attachments/assets/4f17bef7-ee03-4079-861b-6fd5de0870e0" />
<img width="1280" alt="Screenshot 2025-04-27 at 12 31 33 PM" src="https://github.com/user-attachments/assets/88fab175-0fbd-43e0-95f5-11df4b0a7ac0" />

# 🛠️ Technology Stack Used

## Languages
- **Python 3.10+** — Core development language for backend logic and scripting.

## Frameworks & Libraries
- **BeautifulSoup** — Web scraping library for parsing HTML and XML documents.
- **Requests** — Python HTTP library for making API calls and web scraping.
- **Streamlit** — Frontend framework to quickly build interactive UIs for the chatbot.
- **Pinecone** — Vector database used to store and retrieve embeddings efficiently.
- **Hugging Face Transformers** — Access to state-of-the-art LLMs for response generation.
- **dotenv** — For securely managing environment variables like API keys.
- **json** — To process and manage structured data formats (knowledge base).

## Databases
- **Pinecone** — Used for scalable similarity search and retrieval of vectorized knowledge base data.

## APIs
- **Hugging Face Inference API** — For generating human-like natural language responses.
- **Gemini API** — Additional large language model support.

## Tools
- **Streamlit CLI** — Used to run and deploy the chatbot locally.
- **Git & GitHub** — For version control and project collaboration.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

