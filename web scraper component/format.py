
import json
from collections import defaultdict

# Load raw data
with open("Restaurants.json", "r", encoding="utf-8") as infile:
    raw_data = json.load(infile)

cleaned_data = []

for entry in raw_data:
    address_data = entry.get("address", {})
    full_address = ", ".join(filter(None, [
        address_data.get("street", ""),
        address_data.get("locality", ""),
        address_data.get("region", ""),
        address_data.get("postal_code", ""),
        address_data.get("country", "")
    ]))

    menu = entry.get("menu", [])
    category_wise_menu = defaultdict(list)

    for item in menu:
        if isinstance(item, dict):
            category = item.get("attributes", {}).get("category", "Uncategorized")
            category_wise_menu[category].append(item)
        elif isinstance(item, list) and len(item) == 2:
            name, price = item
            clean_price = price.replace("\\u20b9", "").replace("\u20b9", "").replace("₹", "").strip()

            try:
                price_value = float(clean_price)
            except ValueError:
                price_value = 0.0

            category_wise_menu["Uncategorized"].append({
                "name": name,
                "description": "",
                "price": price_value,
                "attributes": {}
            })

    # ⚡️ Only keep up to 4 dishes per category
    formatted_menu = []
    for dishes in category_wise_menu.values():
        formatted_menu.extend(dishes[:3])

    # Determine dietary options from the selected menu
    dietary_options = []
    for menu_item in formatted_menu:
        veg_nonveg = menu_item.get("attributes", {}).get("veg_nonveg")
        if veg_nonveg and veg_nonveg not in dietary_options:
            dietary_options.append(veg_nonveg)

    cleaned_entry = {
        "name": entry.get("name", ""),
        "menu_items": formatted_menu,
        "dietary_options": dietary_options,
        "price_range": entry.get("price_range", "").replace("\u20b9", "₹").replace("\\u20b9", "₹"),
        "address": full_address,
        "opening_hours": entry.get("opening_hours", ""),
        "image_url": entry.get("image_url", ""),
        "phone_number": entry.get("telephone", ""),
        "rating": entry.get("rating", ""),
        "rating_count": entry.get("rating_count", ""),
        "features": entry.get("payment_methods", ""),
        "cuisine": entry.get("cuisine", ""),
    }
    cleaned_data.append(cleaned_entry)

# Save cleaned data
with open("knowledgebase.json", "w", encoding="utf-8") as outfile:
    json.dump(cleaned_data, outfile, indent=2, ensure_ascii=False)
