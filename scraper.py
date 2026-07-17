import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_exercise(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Data extraction
    name_elem = soup.find('h1', class_='pt-6 text-2xl text-white font-semibold mb-4')
    name = name_elem.text.strip() if name_elem else "Unknown"

    desc_elem = soup.find('p', class_='text-gray-300 leading-relaxed whitespace-pre-line')
    description = desc_elem.text.strip() if desc_elem else "No description"

    # Refined instructions: look for the specific container class if possible
    instructions = [li.text.strip() for li in soup.select('li')]

    img_elem = soup.find('img')
    image = img_elem['src'] if img_elem and img_elem.has_attr('src') else "No image"

    url_parts = url.rstrip('/').split('/')
    muscle = url_parts[-2].replace('-', ' ')
    equipment = "dumbbell" 

    return {
        "name": name,
        "description": description,
        "how_to": instructions,
        "muscle": muscle,
        "equipment": equipment,
        "image": image
    }

def append_to_json(new_data, filename='database.json'):
    # Load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = [] # Handle empty or corrupt file
    else:
        data = []

    # Append new item
    data.append(new_data)

    # Save back to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Execution
url = "https://smartworkout.app/en/exercise-library/forearms/dumbbell-lying-pronation"
new_exercise = scrape_exercise(url)

if new_exercise:
    append_to_json(new_exercise)
    print(f"Appended {new_exercise['name']} to database.json")
