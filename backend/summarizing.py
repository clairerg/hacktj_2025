import os
from transformers import pipeline
import yake
import sqlite3

def get_bills(biocode_id, db_path="congress_data.db"):
    bills = []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        SELECT title, policy_area
        FROM bills
        WHERE member_id = ?;
        """
        
        cursor.execute(query, (biocode_id,))
        bills = cursor.fetchall()

        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    
    return bills

biocode_id = "M001242"
bills_list = get_bills(biocode_id)
print(bills_list)


os.makedirs("summaries", exist_ok=True)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def split_text(text, max_tokens=900):
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_tokens):
        chunks.append(" ".join(words[i:i + max_tokens]))
    
    return chunks

# for i in range(1, 11):
input_file = f"clean_speeches/clean_speech_{6}.txt"
output_file = f"summaries/summary_{6}.txt"
output_file2 = f"summaries/keywords_{6}.txt"
try:
    with open(input_file, "r", encoding="utf-8") as file:
        cleaned_text = file.read()
    text_chunks = split_text(cleaned_text)

    chunk_summaries = [
        summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
        for chunk in text_chunks
    ]

    final_summary = " ".join(chunk_summaries)

    exceptions = {"Mr.", "U.S.", "D.C."} 
    words = final_summary.split(" ") 
    formatted_summary = []

    for i in range(len(words)):
      formatted_summary.append(words[i])
      if words[i].endswith(".") and words[i] not in exceptions:
          formatted_summary.append("\n")

    formatted_summary = " ".join(formatted_summary)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(formatted_summary)

    print(f"Summary saved as '{output_file}'.")

    # kw_extractor = yake.KeywordExtractor()
    # keywords = kw_extractor.extract_keywords(cleaned_text)

    # # Format keywords into a readable format
    # formatted_keywords = "\n".join([f"{kw[0]} ({kw[1]:.4f})" for kw in keywords])

    # with open(output_file2, "w", encoding="utf-8") as file:
    #         file.write(formatted_keywords)

    # print(f"Keywords saved as '{output_file}'.")
    

except FileNotFoundError:
    print(f"Warning: {input_file} not found, skipping.")

print("All speeches summarized and saved.")

# with open(input_file, "r", encoding="utf-8") as file:
#   cleaned_text = file.read()

# kw_extractor = yake.KeywordExtractor()
# keywords = kw_extractor.extract_keywords(cleaned_text)

# formatted_keywords = "\n".join([f"{kw[0]} ({kw[1]:.4f})" for kw in keywords])

# with open(output_file2, "w", encoding="utf-8") as file:
#   file.write(formatted_keywords)

# print(f"Keywords saved as '{output_file}'.")
 