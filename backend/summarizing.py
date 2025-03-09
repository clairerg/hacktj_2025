import os
from transformers import pipeline

os.makedirs("summaries", exist_ok=True)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def split_text(text, max_tokens=900):
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_tokens):
        chunks.append(" ".join(words[i:i + max_tokens]))
    
    return chunks

# for i in range(1, 11):
input_file = f"clean_speeches/clean_speech_{1}.txt"
output_file = f"summaries/summary_{1}.txt"

try:
    with open(input_file, "r", encoding="utf-8") as file:
        cleaned_text = file.read()

    text_chunks = split_text(cleaned_text)

    chunk_summaries = [
        summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
        for chunk in text_chunks
    ]

    final_summary = " ".join(chunk_summaries)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(final_summary)

    print(f"Summary saved as '{output_file}'.")

except FileNotFoundError:
    print(f"Warning: {input_file} not found, skipping.")

print("All speeches summarized and saved.")