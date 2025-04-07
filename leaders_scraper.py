import requests
import json
from bs4 import BeautifulSoup
import re

def get_leaders():
    # 1. get the URLs
    root_url = 'https://country-leaders.onrender.com'
    status_url = root_url + '/status'
    countries_url = root_url + '/countries'
    cookie_url = root_url + '/cookie'
    leaders_url = root_url + '/leaders'

    # 2. get the cookie
    cookies = requests.get(cookie_url).cookies

    # 3. get the countries
    countries = requests.get(countries_url, cookies=cookies).json()

    # 4. get the leaders for each country
    leaders_per_country = {}
    session_render = requests.Session()
    session_wikipedia = requests.Session()

    for country in countries:
        print(country)
        
        # Get leaders data for the current country
        leaders_response = requests.get(leaders_url, cookies=cookies, params={'country': country})
        
        if leaders_response.status_code == 200:
            leaders_per_country[country] = leaders_response.json()
        else:
            # If the request fails, get a new cookie and retry
            print('new cookie')
            cookies = requests.get(cookie_url).cookies
            leaders_per_country[country] = session_render.get(leaders_url, cookies=cookies, params={'country': country}).json()

        # Retrieve the first paragraph from Wikipedia for each leader
        for leader in leaders_per_country[country]:
            wikipedia_url = leader['wikipedia_url']
            leader['first_paragraph'] = get_first_paragraph(wikipedia_url, session_wikipedia)

    # 5. return the leaders data
    return leaders_per_country


def get_first_paragraph(wikipedia_url, session):
    print(wikipedia_url)  # keep this for debugging purposes
    response = session.get(wikipedia_url)
    soup = BeautifulSoup(response.text, "html.parser")
    first_paragraph = ''

    # Extract the first non-empty paragraph
    for paragraph in soup.find_all('p'):
        text = paragraph.get_text(strip=True)
        if text:  
            first_paragraph = text
            break

    # Clean the text by removing unwanted elements

    # 1. Remove references like [1], [2], etc.
    cleaned_text = re.sub(r'\[[0-9]*\]', '', first_paragraph)

    # 2. Remove any remaining HTML tags
    cleaned_text = re.sub(r'<.*?>', '', cleaned_text)

    # 3. Remove phonetic transcriptions (e.g., [ˈɡi vɛʁɔfstat])
    cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text)

    # 4. Remove hyperlinks like [text](url)
    cleaned_text = re.sub(r'\[.*?\]\(.*?\)', '', cleaned_text)

    # 5. Remove dates or irrelevant events (e.g., "year 1999")
    cleaned_text = re.sub(r'(année|le)\s*(\d{4})', '', cleaned_text)

    # 6. Remove usernames or other personal information
    cleaned_text = re.sub(r'@[\w]+', '', cleaned_text)

    # 7. Remove sections like "See also" or "References"
    cleaned_text = re.sub(r'(Voir aussi|Références|Sources)', '', cleaned_text)

    # 8. Replace multiple spaces and newline characters with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text) 
    cleaned_text = cleaned_text.strip()  # Remove leading and trailing spaces
    
    return cleaned_text

def save(leaders_per_country):
    # Save the leaders data to a JSON file
    with open('leaders.json', 'w') as f:
        json.dump(leaders_per_country, f)

# Main execution
if __name__ == "__main__":
    leaders_data = get_leaders()
    save(leaders_data)