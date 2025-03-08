import requests
from bs4 import BeautifulSoup
import re
import os 

URL = "https://www.whitehouse.gov/briefing-room/speeches-remarks/"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")
speech_links = [a["href"] for a in soup.find_all("a", href=True) if "whitehouse.gov/remarks" in a["href"] and "-" in a["href"]]

if not os.path.exists("speeches"):
    os.makedirs("speeches")
    
all_speeches = []

for i, link in enumerate(speech_links):
    speech_text = requests.get(link).text
    
    # Define filename
    filename = f"speeches/speech_{i+1}.txt"
    
    # Save speech to file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(speech_text)
    
    print(f"Saved: {filename}")

print("All speeches saved in the 'speeches' folder.")