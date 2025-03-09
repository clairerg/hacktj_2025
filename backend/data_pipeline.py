import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
from textblob import TextBlob

# Replace with your Congress.gov API key
API_KEY = "CpV2MssXeMqPrPeGItd2jbBQ0pYJaFOAnr8mYTRi"
BASE_URL = "https://api.congress.gov/v3"

def get_members():
    members = []
    offset = 0
    limit = 250  # Adjust based on API limits
    
    while True:
        url = f"{BASE_URL}/member?api_key={API_KEY}&format=xml&offset={offset}&limit={limit}"
        response = requests.get(url)
        root = ET.fromstring(response.content)

        page_members = [member.find("bioguideId").text for member in root.findall(".//member")]
        if not page_members:
            break  # Stop when no more members are found
        
        members.extend(page_members)
        offset += limit  # Move to the next page
    members = [member.strip() for member in members]
    print(members)
    return members

# Fetch bills sponsored/cosponsored by a member
def get_bills(member_id, bill_type):
    bills = []
    offset = 0
    limit = 250  # Adjust based on API rate limits
    
    while True:
        url = f"{BASE_URL}/member/{member_id}/{bill_type}-legislation?api_key={API_KEY}&format=xml&offset={offset}&limit={limit}"
        response = requests.get(url)
        root = ET.fromstring(response.content)

        page_bills = []
        for bill in root.findall(".//item"):
            title_element = bill.find("title")
            policy_element = bill.find(".//policyArea/name")

            title = title_element.text if title_element is not None else "Unknown Title"
            policy = policy_element.text if policy_element is not None else "Unknown Policy"

            page_bills.append((title, policy))

        if not page_bills:
            break  # Stop if no more bills are found

        bills.extend(page_bills)
        offset += limit  # Move to next page
    
    return bills

# Perform sentiment analysis on bills and votes
def analyze_sentiment(texts):
    sentiment_scores = [TextBlob(text).sentiment.polarity for text in texts]
    return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

# Generate a summary for each member
def generate_summary():
    members = get_members()
    summaries = {}
    for member_id in members[:1]:  # Limit to first 5 members for testing
        sponsored = get_bills(member_id, "sponsored")
        cosponsored = get_bills(member_id, "cosponsored")
        
        policy_count = defaultdict(int)
        for _, policy in sponsored + cosponsored:
            policy_count[policy] += 1

        top_policies = sorted(policy_count.items(), key=lambda x: x[1], reverse=True)[:3]
        sentiment_score = analyze_sentiment([title for title, _ in sponsored + cosponsored])
        
        summaries[member_id] = {
            "Top Policy Areas": [policy.strip() for policy, _ in top_policies],
            "Sentiment Score": sentiment_score,
            "Total Bills Sponsored": len(sponsored),
            "Total Bills Cosponsored": len(cosponsored)
        }
    
    return summaries

# Run the script and print summaries
summaries = generate_summary()
for member, summary in summaries.items():
    print(f"Member ID: {member}")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("-" * 50)
