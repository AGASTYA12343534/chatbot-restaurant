import os
import json
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Restaurant AI Assistant",
    page_icon="🍽️",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117;
    color: #e8e8e8;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: #161b27;
    border-right: 1px solid #2a2f3e;
}

.brand-header {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f97316, #fb923c, #fdba74);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
    line-height: 1.2;
}

.brand-sub {
    font-size: 0.85rem;
    color: #6b7280;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

.user-bubble {
    background: linear-gradient(135deg, #1e3a5f, #1d4ed8);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
    color: #e8f4fd;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(29, 78, 216, 0.3);
}

.bot-bubble {
    background: #1a1f2e;
    border: 1px solid #2a3347;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 0;
    max-width: 85%;
    color: #d1d5db;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.restaurant-card {
    background: #1a1f2e;
    border: 1px solid #2a3347;
    border-left: 3px solid #f97316;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 8px 0;
    font-size: 0.88rem;
}

.restaurant-card h4 {
    color: #fb923c;
    margin: 0 0 6px 0;
    font-size: 1rem;
    font-weight: 600;
}

.tag {
    display: inline-block;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    color: #94a3b8;
    margin: 2px;
}

.tag-orange { border-color: #f9731650; color: #fb923c; background: #f9731610; }
.tag-green  { border-color: #22c55e50; color: #4ade80; background: #22c55e10; }

.chat-input-area { margin-top: 1rem; }

.stChatInputContainer { background: #1a1f2e !important; border: 1px solid #2a3347 !important; border-radius: 12px !important; }

div[data-testid="stChatMessage"] { background: transparent !important; }

.sidebar-section {
    background: #1e2537;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 14px;
    border: 1px solid #2a3347;
    font-size: 0.85rem;
}

.sidebar-section h5 {
    color: #fb923c;
    margin: 0 0 8px 0;
    font-size: 0.9rem;
    font-weight: 600;
}

.sidebar-section p, .sidebar-section li {
    color: #9ca3af;
    margin: 3px 0;
    line-height: 1.5;
}

.welcome-card {
    background: linear-gradient(135deg, #1a1f2e, #1e2537);
    border: 1px solid #2a3347;
    border-top: 3px solid #f97316;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 1rem;
}

.welcome-card h3 { color: #fb923c; margin: 0 0 8px 0; }
.welcome-card p  { color: #9ca3af; font-size: 0.9rem; line-height: 1.6; margin: 0; }

.suggestion-btn {
    background: #1e2537;
    border: 1px solid #2a3347;
    border-radius: 8px;
    padding: 8px 12px;
    color: #9ca3af;
    font-size: 0.82rem;
    cursor: pointer;
    margin: 4px 0;
    width: 100%;
    text-align: left;
    transition: border-color 0.2s;
}
</style>
""", unsafe_allow_html=True)

# ── Load knowledge base ───────────────────────────────────────────────────────
@st.cache_data
def load_kb():
    kb_path = os.path.join(os.path.dirname(__file__), "knowledgebase.json")
    with open(kb_path, "r", encoding="utf-8") as f:
        return json.load(f)

restaurants = load_kb()

# ── Search ────────────────────────────────────────────────────────────────────
def search(query: str, top_k: int = 3) -> list:
    q = query.lower()
    scored = []

    for r in restaurants:
        score = 0
        name  = r.get("name", "").lower()
        cuisine = str(r.get("cuisine", "")).lower()
        address = r.get("address", "").lower()
        diet    = " ".join(r.get("dietary_options", [])).lower()
        price   = r.get("price_range", "").lower()
        hours   = r.get("opening_hours", "").lower()

        # restaurant-level signals
        for word in q.split():
            if word in name:    score += 5
            if word in cuisine: score += 4
            if word in address: score += 2
            if word in diet:    score += 3
            if word in price:   score += 2
            if word in hours:   score += 1

        # dietary shortcuts
        if any(k in q for k in ["veg", "vegetarian", "plant"]) and "veg" in diet:
            score += 6
        if any(k in q for k in ["non veg", "nonveg", "chicken", "mutton", "meat", "fish", "egg"]):
            if "non-veg" in diet: score += 6

        # menu-level signals
        menu_hits = []
        for item in r.get("menu_items", []):
            iname = item.get("name", "").lower()
            idesc = item.get("description", "").lower()
            icat  = item.get("attributes", {}).get("category", "").lower()
            for word in q.split():
                if len(word) > 2 and (word in iname or word in idesc or word in icat):
                    score += 3
                    menu_hits.append(item)
                    break

        scored.append((score, r, menu_hits[:5]))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [(r, hits) for s, r, hits in scored[:top_k] if s > 0]

# ── Prompt builder ────────────────────────────────────────────────────────────
def build_context(query: str) -> str:
    results = search(query)
    if not results:
        return ""

    lines = ["RETRIEVED RESTAURANT DATA:\n"]
    for r, hits in results:
        lines.append(f"Restaurant: {r.get('name')}")
        lines.append(f"  Cuisine: {r.get('cuisine')}")
        lines.append(f"  Address: {r.get('address')}")
        lines.append(f"  Hours: {r.get('opening_hours')}")
        lines.append(f"  Price Range: {r.get('price_range')}")
        lines.append(f"  Rating: {r.get('rating')} ({r.get('rating_count')} reviews)")
        lines.append(f"  Dietary Options: {', '.join(r.get('dietary_options', []))}")
        lines.append(f"  Phone: {r.get('phone_number')}")

        if hits:
            lines.append("  Matching Menu Items:")
            for item in hits:
                attr = item.get("attributes", {})
                lines.append(f"    - {item['name']} | ₹{item['price']} | {attr.get('veg_nonveg','?')} | Spice: {attr.get('spice_level','?')}/3")
                if item.get("description"):
                    lines.append(f"      {item['description']}")
        else:
            lines.append("  Sample Menu Items:")
            for item in r.get("menu_items", [])[:5]:
                attr = item.get("attributes", {})
                lines.append(f"    - {item['name']} | ₹{item['price']} | {attr.get('veg_nonveg','?')}")
        lines.append("")

    return "\n".join(lines)

SYSTEM_PROMPT = """You are a friendly and knowledgeable restaurant assistant for a food discovery platform focused on restaurants in Lucknow, India.

Your job is to help users discover restaurants, explore menus, check prices, find dietary options, and make dining decisions.

When context data is provided, use it to give specific, accurate answers. Be conversational, warm, and helpful.
Always mention specific dish names, prices in ₹, and restaurant details when relevant.
For greetings, introduce yourself briefly and ask what the user is looking for.
If asked something outside restaurant/food topics, politely redirect.
Keep responses concise but informative. Use emojis sparingly (1-2 max per response)."""

# ── Anthropic client ──────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        st.error("⚠️ ANTHROPIC_API_KEY not found. Add it in Streamlit secrets or .env file.")
        st.stop()
    return Anthropic(api_key=key)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-header">🍽️ FoodBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Lucknow Restaurant Guide</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
      <h5>📍 Restaurants Available</h5>
    """, unsafe_allow_html=True)
    for r in restaurants:
        st.markdown(f"<p>• <b style='color:#d1d5db'>{r['name']}</b><br><span style='color:#6b7280;font-size:0.78rem'>{r.get('cuisine','')[:40]}</span></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
      <h5>💡 Try asking</h5>
      <p>• Best veg restaurants?</p>
      <p>• Show me cheap options under ₹200</p>
      <p>• Which places serve South Indian?</p>
      <p>• What's good at Tanatan?</p>
      <p>• Compare Fo'sho and Curry Leaf</p>
      <p>• Any spicy non-veg dishes?</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown('<div class="brand-header">Restaurant AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Powered by Claude · Lucknow Food Discovery</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome card
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
      <h3>👋 Welcome! I'm your food guide for Lucknow</h3>
      <p>I know 7 restaurants inside out — their menus, prices, dietary options, timings, and more.
      Ask me anything: <b style="color:#fb923c">find dishes, compare restaurants, check what's veg/non-veg</b>, or just browse what's available.</p>
    </div>
    """, unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble">{msg["display"]}</div>', unsafe_allow_html=True)

# Input
if user_input := st.chat_input("Ask about restaurants, dishes, prices, dietary options..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)

    # Build context
    context = build_context(user_input)

    # Build messages for Claude (last 8 turns)
    history = st.session_state.messages[-8:]
    api_messages = []
    for m in history:
        if m["role"] == "user":
            api_messages.append({"role": "user", "content": m["content"]})
        else:
            api_messages.append({"role": "assistant", "content": m.get("raw", m.get("display", ""))})

    # Inject context into last user message
    if context:
        api_messages[-1]["content"] = f"{context}\n\nUser question: {user_input}"

    # Call Claude
    client = get_client()
    with st.chat_message("assistant"):
        with st.spinner(""):
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=api_messages,
            )
            reply = response.content[0].text

        st.markdown(f'<div class="bot-bubble">{reply}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "display": reply,
        "raw": reply,
    })
