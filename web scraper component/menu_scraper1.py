import asyncio
import re
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def detect_spice_level(name, description):
    spicy_keywords = [
        'spicy', 'hot', 'chillie', 'chilli', 'chili', 'mirch', 'pepper', 
        'jalapeño', 'jalapeno', 'habanero', 'ghost pepper', 'bhut jolokia',
        'spice', 'fiery', 'pungent', 'tikha', 'teekha', 'teekhi', 'tikhi', 
        'masaledar', 'masala', 'chilli powder', 'red pepper', 'cayenne',
        'tabasco', 'sriracha', 'wasabi', 'extra spicy', 'very spicy',
        'schezwan', 'szechuan', 'sichuan', 'tandoori'
    ]
    high_spice_keywords = [
        'extra hot', 'very hot', 'extra spicy', 'very spicy', 'fiery hot',
        'burning hot', 'tears', 'bahut tikha', 'bahut teekha', 'super spicy'
    ]
    combined_text = f"{name} {description}".lower()

    if any(keyword in combined_text for keyword in high_spice_keywords):
        return 3
    if any(keyword in combined_text for keyword in spicy_keywords):
        return 2
    return 1

def detect_veg_nonveg(name, description):
    non_veg_keywords = [
        'chicken', 'mutton', 'fish', 'egg', 'prawn', 'lamb', 'meat', 
        'bacon', 'keema', 'gosht', 'beef', 'pork', 'seafood', 'shrimp',
        'crab', 'lobster', 'squid', 'duck', 'turkey', 'ham', 'sausage',
        'salami', 'pepperoni'
    ]
    combined_text = f"{name} {description}".lower()
    return 'Non-Veg' if any(word in combined_text for word in non_veg_keywords) else 'Veg'

def extract_description(price_div):
    description = ""

    # Try finding nearby description tags
    candidates = [
        price_div.find_next('p'),
        price_div.find_next_sibling('div'),
        price_div.find_next('span')
    ]
    for candidate in candidates:
        if candidate and '₹' not in candidate.get_text():
            description = candidate.get_text(strip=True)
            if description:
                return description

    # Try inside parent container
    parent = price_div.parent
    if parent:
        for div in parent.find_all('div'):
            text = div.get_text(strip=True)
            if text and '₹' not in text and div != price_div and len(text) < 300:
                return text

    return description

def clean_menu_items(items):
    cleaned_items = []
    seen_names = set()

    for item in items:
        if item['attributes']['category'] == "Uncategorized":
            continue

        name = re.sub(r'[/:,]', '', item['name']).strip()
        simplified_name = re.sub(r'\W+', '', name.lower())

        if name and simplified_name not in seen_names:
            seen_names.add(simplified_name)
            item['name'] = name
            item['attributes'].pop('subcategory', None)
            cleaned_items.append(item)

    return cleaned_items

async def smart_scroll(page):
    print("Scrolling...")
    last_height = await page.evaluate("document.body.scrollHeight")
    scroll_count = 0
    max_scrolls = 10

    while scroll_count < max_scrolls:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)

        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            await page.wait_for_timeout(500)
            newer_height = await page.evaluate("document.body.scrollHeight")
            if newer_height == new_height:
                print(f"Reached bottom after {scroll_count+1} scrolls")
                break
        last_height = new_height
        scroll_count += 1

    await page.wait_for_timeout(1000)

async def scrape_menu(page):
    print("Extracting page content...")
    html = await page.content()

    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find_all('section')
    print(f"Found {len(sections)} sections")

    categories = []
    for section in sections:
        h4 = section.find('h4')
        if h4:
            category_name = h4.get_text(strip=True)
            if category_name and not any(c['name'] == category_name for c in categories):
                categories.append({'name': category_name, 'section_element': section})

    price_containers = soup.find_all(
        lambda tag: tag.name == 'div' and re.search(r'₹\s*\d+', tag.get_text(strip=True))
    )
    print(f"Found {len(price_containers)} price containers")

    menu_items = []
    seen_names = set()

    for price_div in price_containers:
        parent_section = price_div.find_parent('section')
        if not parent_section:
            continue

        item_category = next(
            (cat['name'] for cat in categories if cat['section_element'] == parent_section),
            "Uncategorized"
        )

        text = price_div.get_text(strip=True)
        name_match = re.search(r'^(.*?)(?:\s*₹)', text)
        price_match = re.search(r'₹\s*(\d+)', text)

        if not name_match or not price_match:
            continue

        name = name_match.group(1).strip()
        price = float(price_match.group(1))
        simplified_name = re.sub(r'\W+', '', name.lower())

        if simplified_name in seen_names:
            continue
        seen_names.add(simplified_name)

        description = extract_description(price_div)
        veg_status = detect_veg_nonveg(name, description)
        spice_level = detect_spice_level(name, description)

        menu_items.append({
            'name': name,
            'description': description,
            'price': price,
            'attributes': {
                'veg_nonveg': veg_status,
                'category': item_category,
                'spice_level': spice_level
            }
        })

    print(f"Extracted {len(menu_items)} menu items before cleaning")
    return clean_menu_items(menu_items)

async def scrape_zomato_menu(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Navigating to {url}...")
        await page.goto(url, timeout=60000)
        await page.wait_for_selector("text=₹", timeout=15000)

        await smart_scroll(page)
        menu_items = await scrape_menu(page)

        await browser.close()
        return menu_items

async def main():
    url = "https://example.com"  # Replace with your Zomato menu URL
    menu_items = await scrape_zomato_menu(url)

    with open('menu_items.json', 'w', encoding='utf-8') as f:
        json.dump(menu_items, f, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(menu_items)} menu items to menu_items.json")

if __name__ == "__main__":
    asyncio.run(main())
