import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

def scrape_exercise(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to reach {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # 1. Name
    name_elem = soup.find('h1', class_='pt-6 text-2xl text-white font-semibold mb-4')
    name = name_elem.text.strip() if name_elem else "Unknown"

    # 2. Description
    desc_elem = soup.find('p', class_='text-gray-300 leading-relaxed whitespace-pre-line')
    description = desc_elem.text.strip() if desc_elem else "No description"

    # 3. FIXED: How-to instructions between headings
    instructions = []
    # Find the starting heading (adjust the string to match exactly what is on the page)
    start_node = soup.find(string=lambda text: text and "How to perform" in text)
    
    if start_node:
        # Move to the container holding the text
        current = start_node.find_parent()
        # Iterate through siblings until we hit "What muscles work"
        for sibling in current.find_next_siblings():
            if "What muscles work" in sibling.get_text():
                break
            # Collect list items or text paragraphs
            if sibling.name in ['ul', 'ol']:
                instructions.extend([li.text.strip() for li in sibling.find_all('li')])
            elif sibling.name == 'p':
                instructions.append(sibling.text.strip())

    # 4. FIXED: Image URL (Targeting the animation container)
    # Change 'div.aspect-video img' to the specific class of your animation tag if needed
    img_elem = soup.select_one('div.aspect-video img')
    if img_elem and img_elem.has_attr('src'):
        image = urljoin(url, img_elem['src'])
    else:
        image = "No image"

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
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_data)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Execution
url = "https://smartworkout.app/en/exercise-library/forearms/dumbbell-lying-pronation"
new_exercise = scrape_exercise(url)

if new_exercise:
    append_to_json(new_exercise)
    print(f"Appended {new_exercise['name']} to database.json")
