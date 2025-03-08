import requests
import time

BASE_URL = "https://www.govtrack.us/api/v2/"

# Dictionary to store results
congress_data = {}

# Step 1: Fetch all members of Congress
members_url = f"{BASE_URL}person"
members_response = requests.get(members_url)
members = members_response.json()['objects']

# Step 2: Fetch voting records and sponsored bills
for member in members:
    member_name = f"{member['firstname']} {member['lastname']}"
    member_id = member['id']

    # Initialize member entry in dictionary
    congress_data[member_name] = {}

    # Step 3: Fetch their voting records
    votes_url = f"{BASE_URL}vote_voter?person={member_id}"
    votes_response = requests.get(votes_url)
    votes = votes_response.json()['objects']

    for vote in votes:
        bill = vote['vote'].get('bill')
        if bill:
            bill_id = bill['id']
            position = vote['option']['value']  # Yes/No
            congress_data[member_name][bill_id] = position
    
    # Step 4: Fetch bills they sponsored
    sponsored_bills_url = f"{BASE_URL}bill?sponsor={member_id}"
    sponsored_response = requests.get(sponsored_bills_url)
    sponsored_bills = sponsored_response.json()['objects']

    for bill in sponsored_bills:
        bill_id = bill['id']
        is_enacted = bill['current_status'] == "enacted"
        congress_data[member_name][bill_id] = "sponsored"
        if is_enacted:
            congress_data[member_name][bill_id] = "enacted"

    # Respect API rate limits
    time.sleep(1)

# Print the final dictionary
print(congress_data)
