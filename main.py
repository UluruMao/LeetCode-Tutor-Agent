import os
import requests
import datetime
import time
from plyer import notification
from dotenv import load_dotenv
from database import init_db, log_failure_to_db
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate


# --- Setup & Authentication ---
load_dotenv()
init_db()
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

# --- Fetching Functions ---
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

def get_problem_tags(title_slug: str) -> str:
    payload = {
        "operationName": "questionTags",
        "variables": {"titleSlug": title_slug},
        "query": """
        query questionTags($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            topicTags { name }
          }
        }
        """
    }
    response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
    tags = (
        response.json()
        .get("data", {})
        .get("question", {})
        .get("topicTags", [])
    )
    return ", ".join(t.get("name") for t in tags if t.get("name")) or "N/A"

# --- Notification Helper ---
def notify_user(title, message):
    """Triggers a native Windows desktop notification."""
    notification.notify(
        title=title,
        message=message,
        app_name="LeetCode Tutor",
        # You can add a .ico file path here if you want a custom icon
        timeout=10 
    )

# --- LangChain Tutor ---
def analyze_with_ai(problem_title, problem_tags, user_code, failed_test_case, error_msg):
    print("\n Invoking Gemini AI Tutor...\n")
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.2)
    
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
    
    # NEW FIX: Extract text if the preview model returns a list
    ai_advice = result.content
    if isinstance(ai_advice, list):
        # Extract the 'text' value from the dictionary inside the list
        ai_advice = "".join([block.get("text", "") for block in ai_advice if block.get("type") == "text"])
    
    print("================ AI TUTOR ================")
    print(ai_advice)
    print("==========================================")
    
    # Pass the cleaned string to the logger, not the raw result.content
    save_to_markdown(problem_title, problem_tags, error_msg, ai_advice)

# --- The Markdown Logger ---
def save_to_markdown(problem_title, problem_tags, error_msg, ai_advice):
    filename = "study_guide.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Format the log entry in beautiful Markdown
    entry = f"##  {problem_title}\n"
    entry += f"**Tags:** {problem_tags}\n"
    entry += f"**Date:** {timestamp}\n"
    entry += f"**Status/Error:** `{error_msg}`\n\n"
    entry += "### The Flaw & Hint\n"
    entry += f"{ai_advice}\n\n"
    entry += "---\n\n"
    
    # Append to the file (creates the file if it doesn't exist)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)
        log_failure_to_db(problem_title, problem_tags, error_msg, ai_advice)
        
    print(f" Logged to {filename}")

# --- The Background Loop ---
def run_tutor_loop():
    last_processed_id = None
    
    # Initialize the DB once at startup
    init_db()
    
    print(f"Background Daemon Started. Monitoring {USERNAME}...")
    notify_user("LeetCode Tutor Active", "Monitoring your submissions in the background.")

    while True:
        try:
            latest = get_latest_submission()
            
            if latest:
                current_id = latest['id']
                status = latest['statusDisplay']
                
                # Only proceed if this is a NEW submission we haven't seen yet
                if current_id != last_processed_id:
                    if status == "Accepted":
                        print(f"New submission: '{latest['title']}' accepted. Skipping.")
                        # NEW: Immediate success notification
                        notify_user("LeetCode: Accepted! ", f"Great job passing {latest['title']}!")
                    else:
                        print(f"New failure detected: {latest['title']}. Analyzing...")
                        # NEW: Immediate failure notification
                        notify_user("LeetCode: Failed ", f"Failed {latest['title']}. AI Tutor is analyzing your code...")
                        
                        # Process the failure
                        details = get_submission_details(current_id)
                        if details:
                            error_info = (details.get('runtimeError') or 
                                          details.get('compileError') or 
                                          status)
                            title_slug = (details.get("question") or {}).get("titleSlug")
                            problem_tags = get_problem_tags(title_slug) if title_slug else "N/A"
                            
                            # Analyze and save
                            analyze_with_ai(
                                problem_title=latest['title'],
                                problem_tags=problem_tags,
                                user_code=details.get('code'),
                                failed_test_case=details.get('lastTestcase'),
                                error_msg=error_info
                            )
                            
                            # Trigger Desktop Notification WHEN FINISHED
                            notify_user(
                                f"Tutor Analysis Ready",
                                f"Socratic hint for {latest['title']} is in your study_guide.md!"
                            )
                    
                    # Update the state so we don't re-process this ID
                    last_processed_id = current_id
            
        except Exception as e:
            print(f"Polling error: {e}")

        # Wait for 60 seconds before checking again
        time.sleep(60)

# --- Execution ---
if __name__ == "__main__":
    run_tutor_loop()    
