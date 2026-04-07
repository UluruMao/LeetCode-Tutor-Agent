import os
import requests
import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# --- Setup & Authentication ---
load_dotenv()
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF")
USERNAME = os.getenv("LEETCODE_USERNAME")
GRAPHQL_URL = "https://leetcode.com/graphql"

headers = {
    "Content-Type": "application/json",
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
    "x-csrftoken": CSRF_TOKEN,
    "Referer": f"https://leetcode.com/{USERNAME}/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# --- 1. The Eyes: Fetching Functions ---
def get_latest_submission():
    payload = {
        "operationName": "recentAcSubmissions",
        "variables": {"username": USERNAME, "limit": 1},
        "query": """
        query recentAcSubmissions($username: String!, $limit: Int!) {
          recentSubmissionList(username: $username, limit: $limit) {
            id title statusDisplay lang
          }
        }
        """
    }
    response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
    submissions = response.json().get("data", {}).get("recentSubmissionList", [])
    return submissions[0] if submissions else None

def get_submission_details(submission_id):
    payload = {
        "operationName": "submissionDetails",
        "variables": {"submissionId": submission_id},
        "query": """
        query submissionDetails($submissionId: Int!) {
          submissionDetails(submissionId: $submissionId) {
            code statusCode runtimeError compileError lastTestcase
            question { titleSlug }
          }
        }
        """
    }
    response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
    return response.json().get("data", {}).get("submissionDetails")

# --- 2. The Brain: LangChain Tutor ---
def analyze_with_ai(problem_title, user_code, failed_test_case, error_msg):
    print("\n Invoking Gemini AI Tutor...\n")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    prompt = PromptTemplate(
        input_variables=["problem", "code", "test_case", "error"],
        template="""
        You are an expert, Socratic algorithm tutor helping a student with LeetCode.
        
        Problem: {problem}
        Error/Status: {error}
        Failed Test Case: {test_case}
        
        Student's Code:
        {code}
        
        YOUR GOAL:
        1. Identify the logical flaw or edge case the student missed.
        2. DO NOT GIVE THE ANSWER OR REWRITE THE CODE.
        3. Explain *why* the logic fails on this specific test case.
        4. Ask one guiding question to help them realize the fix themselves.
        
        Keep your response concise, encouraging, and formatted clearly in the terminal.
        """
    )
    
    chain = prompt | llm
    result = chain.invoke({
        "problem": problem_title,
        "code": user_code,
        "test_case": failed_test_case or "N/A",
        "error": error_msg or "Wrong Answer"
    })
    
    print("================ AI TUTOR ================")
    print(result.content)
    print("==========================================")
    save_to_markdown(problem_title, error_msg, result.content)

# --- 3. The Markdown Logger ---
def save_to_markdown(problem_title, error_msg, ai_advice):
    filename = "study_guide.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Format the log entry in beautiful Markdown
    entry = f"##  {problem_title}\n"
    entry += f"**Date:** {timestamp}\n"
    entry += f"**Status/Error:** `{error_msg}`\n\n"
    entry += "### The Flaw & Hint\n"
    entry += f"{ai_advice}\n\n"
    entry += "---\n\n"
    
    # Append to the file (creates the file if it doesn't exist)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)
        
    print(f" Logged to {filename}")

# --- 4. The Main Loop ---
if __name__ == "__main__":
    print(f" Checking LeetCode for {USERNAME}...")
    latest = get_latest_submission()
    
    if not latest:
        print(" No submissions found.")
    else:
        print(f" Found latest submission: {latest['title']} ({latest['statusDisplay']})")
        
        if latest['statusDisplay'] == "Accepted":
            print(" Solution Accepted! No tutoring needed right now.")
        else:
            print(f" Oh no! Failed with: {latest['statusDisplay']}. Pulling code for analysis...")
            
            # Fetch the actual code and test case
            details = get_submission_details(latest['id'])
            
            if details:
                error_info = details.get('runtimeError') or details.get('compileError') or latest['statusDisplay']
                analyze_with_ai(
                    problem_title=latest['title'],
                    user_code=details.get('code'),
                    failed_test_case=details.get('lastTestcase'),
                    error_msg=error_info
                )