import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.whitehouse.gov/briefing-room/speeches-remarks/"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")
speech_links = [a["href"] for a in soup.find_all("a", href=True) if "whitehouse.gov/remarks" in a["href"] and "-" in a["href"]]

all_speeches = []

for i, link in enumerate(speech_links):
    speech_text = requests.get(link).text
    all_speeches.append(f"=== SPEECH {i+1} ===\n{speech_text}")

# Join speeches with a separator and save to file
with open("all_speeches.txt", "w", encoding="utf-8") as file:
    file.write("\n\n---\n\n".join(all_speeches))

print("All speeches saved to all_speeches.txt")