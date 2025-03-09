import sqlite3
import requests
from collections import defaultdict

# Replace with your Congress.gov API key
API_KEY = "CpV2MssXeMqPrPeGItd2jbBQ0pYJaFOAnr8mYTRi"
BASE_URL = "https://api.congress.gov/v3"

# Database setup
def setup_database():
    conn = sqlite3.connect("congress_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id TEXT PRIMARY KEY,
            sponsored_bills TEXT,
            cosponsored_bills TEXT,
            total_bills_sponsored INTEGER,
            total_bills_cosponsored INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_members():
    members = []
    offset = 0
    limit = 250  # Adjust based on API limits
    
    while True:
        url = f"{BASE_URL}/member?api_key={API_KEY}&format=json&offset={offset}&limit={limit}"
        response = requests.get(url)
        data = response.json()
        
        page_members = []
        for member in data.get("members", []):
            bioguide_id = member.get("bioguideId", "")
            start_date = int(member.get("startYear", 0))
            end_date = member.get("endYear", "")
            
            if end_date == "2025":
                page_members.append((bioguide_id, start_date))
        
        if not page_members:
            break  # Stop when no more members are found
        
        members.extend(page_members)
        offset += limit  # Move to the next page
    
    members = sorted(members, key=lambda x: x[1], reverse=True)  # Sort by start year (most recent first)
    return [member[0] for member in members]

def get_bills(member_id, bill_type):
    bills = []
    offset = 0
    limit = 250  # Adjust based on API rate limits
    
    while True:
        url = f"{BASE_URL}/member/{member_id}/{bill_type}-legislation?api_key={API_KEY}&format=json&offset={offset}&limit={limit}"
        response = requests.get(url)
        data = response.json()
        
        page_bills = [bill.get("title", "Unknown Title") for bill in data.get("bills", [])]
        
        if not page_bills:
            break  # Stop if no more bills are found

        bills.extend(page_bills)
        offset += limit  # Move to next page
    
    return bills

def save_to_database(member_id, sponsored_bills, cosponsored_bills):
    conn = sqlite3.connect("congress_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (id, sponsored_bills, cosponsored_bills, total_bills_sponsored, total_bills_cosponsored)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            sponsored_bills = excluded.sponsored_bills,
            cosponsored_bills = excluded.cosponsored_bills,
            total_bills_sponsored = excluded.total_bills_sponsored,
            total_bills_cosponsored = excluded.total_bills_cosponsored
    ''', (member_id, ", ".join(sponsored_bills), ", ".join(cosponsored_bills), len(sponsored_bills), len(cosponsored_bills)))
    conn.commit()
    conn.close()

def generate_summary():
    members = get_members()
    for member_id in members[:1]:  # Limit to first 5 members for testing
        sponsored = get_bills(member_id, "sponsored")
        cosponsored = get_bills(member_id, "cosponsored")
        
        save_to_database(
            member_id,
            sponsored,
            cosponsored
        )

if __name__ == "__main__":
    setup_database()
    generate_summary()
    print("Data successfully stored in database.")
