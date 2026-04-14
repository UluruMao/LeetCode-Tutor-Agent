import sqlite3

DB_NAME = "leetcode_history.db"

def search_by_tag(target_tag):
    """Searches the database for any problem matching the tag."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # We use % to allow partial matches, so searching "sliding window" 
    # will match "Array, Sliding Window, Two Pointers"
    query = "SELECT timestamp, problem_title, error_type FROM failures WHERE tags LIKE ? COLLATE NOCASE"
    cursor.execute(query, ('%' + target_tag + '%',))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print(f"No failures found for tag: '{target_tag}'")
        return
        
    print(f"\n--- Found {len(results)} failures involving '{target_tag}' ---")
    for row in results:
        timestamp, title, error = row
        print(f"[{timestamp}] {title} - Failed with: {error}")

if __name__ == "__main__":
    import sys
    
    # Allow the user to pass the tag via the terminal
    if len(sys.argv) > 1:
        search_term = " ".join(sys.argv[1:])
        search_by_tag(search_term)
    else:
        print("Usage: python query_stats.py <tag_name>")
        print("Example: python query_stats.py sliding window")
