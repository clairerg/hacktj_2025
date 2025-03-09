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
            name TEXT,
            top_policies TEXT,
            total_bills_sponsored INTEGER,
            total_bills_cosponsored INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            member_id TEXT,
            bill_type TEXT,
            title TEXT,
            policy_area TEXT,
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    ''')
    conn.commit()
    conn.close()

# Get members
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
            name = member["name"]
            page_members.append((bioguide_id, name, start_date))
        
        if not page_members:
            break  # Stop when no more members are found
        
        members.extend(page_members)
        offset += limit  # Move to the next page
    
    members = sorted(members, key=lambda x: x[2], reverse=True)  # Sort by start year (most recent first)
    return [(member[0], member[1]) for member in members]

# Get bills
def get_bills(member_id, bill_type):
    bills = []
    offset = 0
    limit = 250  # Adjust based on API rate limits
    
    while True:
        url = f"{BASE_URL}/member/{member_id}/{bill_type}-legislation?api_key={API_KEY}&format=json&offset={offset}&limit={limit}"
        response = requests.get(url)
        data = response.json()
        if len(data.keys()) == 3: data = data[bill_type + "Legislation"]
        else: return []
        page_bills = []
        for bill in data:
            title = bill.get("title", "Unknown Title")
            policy = bill.get("policyArea", {}).get("name", "Unknown Policy")
            if policy != None: page_bills.append((title, policy))
        
        if not page_bills:
            break  # Stop if no more bills are found

        bills.extend(page_bills)
        offset += limit  # Move to next page
    
    return bills

# Save data to database
def save_to_database(member_id, name, top_policies, total_sponsored, total_cosponsored, sponsored, cosponsored):
    conn = sqlite3.connect("congress_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (id, name, top_policies, total_bills_sponsored, total_bills_cosponsored)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            top_policies = excluded.top_policies,
            total_bills_sponsored = excluded.total_bills_sponsored,
            total_bills_cosponsored = excluded.total_bills_cosponsored
    ''', (member_id, name, ", ".join(top_policies), total_sponsored, total_cosponsored))
    
    for title, policy in sponsored:
        cursor.execute('''
            INSERT INTO bills (member_id, bill_type, title, policy_area)
            VALUES (?, ?, ?, ?)
        ''', (member_id, "sponsored", title, policy))
    
    for title, policy in cosponsored:
        cursor.execute('''
            INSERT INTO bills (member_id, bill_type, title, policy_area)
            VALUES (?, ?, ?, ?)
        ''', (member_id, "cosponsored", title, policy))
    
    conn.commit()
    conn.close()

# Generate summary
def generate_summary():
    members = get_members()
    for member_id, name in members[:5] + members[-3:]: 
        sponsored = get_bills(member_id, "sponsored")
        cosponsored = get_bills(member_id, "cosponsored")
        policy_count = defaultdict(int)
        for _, policy in sponsored + cosponsored:
            policy_count[policy] += 1
        top_policies = sorted(policy_count.items(), key=lambda x: x[1], reverse=True)[:3]
        print(top_policies)
        
        save_to_database(
            member_id,
            name,
            [policy.strip() for policy, _ in top_policies],
            len(sponsored),
            len(cosponsored),
            sponsored,
            cosponsored
        )

if __name__ == "__main__":
    setup_database()
    generate_summary()
    print("Data successfully stored in database.")
