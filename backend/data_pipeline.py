import sqlite3
import requests
from collections import defaultdict
from textblob import TextBlob

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
            top_policies TEXT,
            sentiment_score REAL,
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
        url = f"{BASE_URL}/member?api_key={API_KEY}&format=json&offset={offset}&limit={limit}&currentMember=TRUE"
        response = requests.get(url)
        data = response.json()
        
        page_members = []
        for member in data.get("members", []):
            bioguide_id = member["bioguideId"]
            start_date = int(member["terms"]["item"][0]["startYear"])
            if "endYear" in member["terms"]["item"][0].keys(): end_date = int(member["terms"]["item"][0]["endYear"])
            else: end_date = -1
            page_members.append((bioguide_id, start_date))
        
        if not page_members:
            break  # Stop when no more members are found
        
        members.extend(page_members)
        offset += limit  # Move to the next page
    
    members = sorted(members, key=lambda x: x[1], reverse=True)  # Sort by start year (most recent first)
    print(members)
    return [member[0] for member in members]

def get_bills(member_id, bill_type):
    bills = []
    offset = 0
    limit = 250  # Adjust based on API rate limits
    
    while True:
        url = f"{BASE_URL}/member/{member_id}/{bill_type}-legislation?api_key={API_KEY}&format=json&offset={offset}&limit={limit}"
        response = requests.get(url)
        data = response.json()
        
        page_bills = []
        for bill in data.get("bills", []):
            title = bill.get("title", "Unknown Title")
            policy = bill.get("policyArea", {}).get("name", "Unknown Policy")
            
            page_bills.append((title, policy))
        
        if not page_bills:
            break  # Stop if no more bills are found

        bills.extend(page_bills)
        offset += limit  # Move to next page
    
    return bills

def analyze_sentiment(texts):
    sentiment_scores = [TextBlob(text).sentiment.polarity for text in texts]
    return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

def save_to_database(member_id, top_policies, sentiment_score, total_sponsored, total_cosponsored):
    conn = sqlite3.connect("congress_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (id, top_policies, sentiment_score, total_bills_sponsored, total_bills_cosponsored)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            top_policies = excluded.top_policies,
            sentiment_score = excluded.sentiment_score,
            total_bills_sponsored = excluded.total_bills_sponsored,
            total_bills_cosponsored = excluded.total_bills_cosponsored
    ''', (member_id, ", ".join(top_policies), sentiment_score, total_sponsored, total_cosponsored))
    conn.commit()
    conn.close()

def generate_summary():
    members = get_members()
    for member_id in members[:1]:  # Limit to first 5 members for testing
        sponsored = get_bills(member_id, "sponsored")
        cosponsored = get_bills(member_id, "cosponsored")
        
        policy_count = defaultdict(int)
        for _, policy in sponsored + cosponsored:
            policy_count[policy] += 1

        top_policies = sorted(policy_count.items(), key=lambda x: x[1], reverse=True)[:3]
        sentiment_score = analyze_sentiment([title for title, _ in sponsored + cosponsored])
        
        save_to_database(
            member_id,
            [policy.strip() for policy, _ in top_policies],
            sentiment_score,
            len(sponsored),
            len(cosponsored)
        )

if __name__ == "__main__":
    setup_database()
    generate_summary()
    print("Data successfully stored in database.")
