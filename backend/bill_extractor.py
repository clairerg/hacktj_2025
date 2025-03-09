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

kw_extractor = yake.KeywordExtractor()

def extract_keywords_from_bills(biocode_id):
    bills_list = get_bills(biocode_id) 

    if not bills_list:
        print(f"No bills found for {biocode_id}.")
        return
    
    all_titles = " ".join([bill[0] for bill in bills_list])
    
    keywords = kw_extractor.extract_keywords(all_titles)
    formatted_keywords = "\n".join([f"{kw[0]} ({kw[1]:.4f})" for kw in keywords])
    print(formatted_keywords)
    output_file3 = f"summaries/keywords_{biocode_id}.txt"

    with open(output_file3, "w", encoding="utf-8") as file:
        file.write(formatted_keywords)

    print(f"Keywords saved as '{output_file3}'.")

# Example usage
biocode_id = "M001242"
extract_keywords_from_bills(biocode_id)