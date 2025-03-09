import re
import os
os.makedirs("clean_speeches", exist_ok=True)

def clean_speech(text):

    text = re.sub(r'<.*?>', '', text)

    text = re.sub(r'\(.*?\)', '', text) 
    
    text = re.sub(r'&nbsp;', ' ', text).strip()
    text = re.sub(r'&#8212;', ' ', text).strip()
    text = re.sub(r'#8217', ' ', text).strip()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

for i in range(1, 11):
  input_file = f"speeches/speech_{i}.txt"
  output_file = f"clean_speeches/clean_speech_{i}.txt"

  with open(f"speeches/speech_{i}.txt", "r", encoding="utf-8") as file:
    raw_text = file.read()
    cleaned_text = clean_speech(raw_text)

  with open(output_file, "w", encoding="utf-8") as file:
    file.write(cleaned_text)
        
  print(f"Cleaned speech saved as '{output_file}'.")