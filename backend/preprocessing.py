import re

def clean_speech(text):

    text = re.sub(r'<.*?>', '', text)

    text = re.sub(r'\(.*?\)', '', text) 
    
    text = re.sub(r'&nbsp;', ' ', text).strip()
    text = re.sub(r'&#8212;', ' ', text).strip()
    text = re.sub(r'#8217', ' ', text).strip()
    return text

with open("speeches/speech_1.txt", "r", encoding="utf-8") as file:
    raw_text = file.read()

cleaned_text = clean_speech(raw_text)


with open("cleaned_speech.txt", "w", encoding="utf-8") as file:
    file.write(cleaned_text)

print("Speech cleaned and saved as 'cleaned_speech.txt'.")
