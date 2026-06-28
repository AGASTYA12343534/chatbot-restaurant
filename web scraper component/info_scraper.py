import json
import requests
from bs4 import BeautifulSoup
from menu_scraper1 import scrape_zomato_menu
import asyncio 

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

def get_info(url):
    """ Get Information about the restaurant from URL """
    
    global headers
    webpage = requests.get(url, headers=headers, timeout=3)
    html_text = BeautifulSoup(webpage.text, 'lxml')
    info = html_text.find_all('script', type='application/ld+json')[1]
    info = json.loads(info.string)
    
    restaurant_info = {
        'type': info['@type'],
        'name': info['name'],
        'url': info['url'],
        'opening_hours': info['openingHours'],
        'address': {
            'street': info['address']['streetAddress'],
            'locality': info['address']['addressLocality'],
            'region': info['address']['addressRegion'],
            'postal_code': info['address']['postalCode'],
            'country': info['address']['addressCountry']
        },
        'geo': {
            'latitude': info['geo']['latitude'],
            'longitude': info['geo']['longitude']
        },
        'telephone': info['telephone'],
        'price_range': info['priceRange'],
        'payment_methods': info['paymentAccepted'],
        'image_url': info['image'],
        'cuisine': info['servesCuisine'],
        'rating': info['aggregateRating']['ratingValue'],
        'rating_count': info['aggregateRating']['ratingCount'],
        'menu': []  # Placeholder for menu items
    }
    
    return restaurant_info


def save_json(file_name, data):
    """ Save the data as a JSON file """
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def get_restaurant_info(url_list, save=True, file_name="Restaurants.json"):
    """ Get Restaurant Information from all urls passed and include menu """

    # Collecting the data
    restaurant_data = []
    for url in url_list:
        restaurant_info = get_info(url)
        
        # Fetch menu
        menu = asyncio.run(scrape_zomato_menu(url + "/order"))
        
        # Adding menu to restaurant data
        restaurant_info['menu'] = menu
        
        restaurant_data.append(restaurant_info)
        
    # Save the data to JSON file
    if save:
        save_json(file_name, restaurant_data)
        
    return restaurant_data
