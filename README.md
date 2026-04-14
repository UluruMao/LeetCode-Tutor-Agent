## LeetCode AI Tutor Agent

An autonomous, locally-hosted background daemon that monitors your LeetCode profile, detects failed submissions in real-time, and provides **Socratic, spoiler-free tutoring** using **Google Gemini** (via LangChain).

Built to transform the LeetCode grind into a guided learning loop, this agent acts like a strict but helpful tutor: it sits silently in the background, pings you with a native OS desktop notification when you fail a test case, and generates a detailed study guide highlighting logical gaps—**without writing the full solution for you**.

---

## Key Features

- **Automated data fetching**: Uses LeetCode’s GraphQL endpoint to pull recent submission status, code, and failed test cases.
- **Socratic AI analysis**: Uses Gemini via LangChain with “teacher-mode” prompts to focus on reasoning, not answer-dumping.
- **Study guide generation**: Logs failed attempts, error output, and tailored guidance into a local, timestamped `study_guide.md`.
- **Secure-by-default workflow**: Uses `.venv` and `python-dotenv` so cookies and API keys stay local and out of version control.
- **Continuous Background Monitoring**: Added polling every 60 seconds.
- **Native OS Notifications**: Added instant Windows alerts via plyer.
- **Dual-Layer Logging**: Added the SQLite database (leetcode_history.db) alongside the Markdown file.

---

## Tech Stack

- **Language**: Python 3
- **AI orchestration**: LangChain (`langchain-google-genai`)
- **LLM**: Google Gemini (configured in code; default: `gemini-3-flash-preview`)
- **Network / API**: `requests`, GraphQL
- **System Integration**: `plyer` (notifications), `python-dotenv`, `PyInstaller`
- **Database**:SQLite3, plyer, and PyInstaller
---

## Project Output

- `study_guide.md`: A growing, timestamped log of failures + guidance (generated locally).
- `.env`: Local secrets file (not committed).

---

## Quick Start

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell)**:

```powershell
.\.venv\Scripts\Activate.ps1
```

- **macOS/Linux (bash/zsh)**:

```bash
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install python-dotenv requests langchain langchain-google-genai
```

### 3) Configure authentication (`.env`)

Create a file named **exactly** `.env` in the project root.

You need:
- A **Google AI Studio API key**
- Your active **LeetCode session cookies**
- Your **LeetCode username**

#### Getting LeetCode cookies

1. Log into LeetCode in your browser
2. Open Developer Tools (F12)
3. Go to **Application / Storage → Cookies**
4. Copy values for:
   - `LEETCODE_SESSION`
   - `csrftoken`

#### Example `.env`

```env
GOOGLE_API_KEY="your_gemini_key_here"
LEETCODE_SESSION="your_leetcode_session_cookie_here"
LEETCODE_CSRF="your_csrf_token_here"
LEETCODE_USERNAME="your_leetcode_username"
```

**Important**: No spaces around `=`.

### 4) Run the tutor

1. Submit a problem on LeetCode.
2. Run:

```bash
python main.py
```
### 5) Analyzing Your Weaknesses

You can query your local SQLite database to see how often you fail certain types of problems. Run the query script with a search term, for example:

```bash
python query_stats.py "sliding window"
```
---

## How It Works (High Level)

1. **Monitor:** The daemon runs continuously in the background, polling LeetCode via GraphQL every 60 seconds.
2. **Alert:** Triggers native Windows desktop notifications the moment a new submission is detected.
3. **Fetch Context:** If a failure is detected, it pulls the exact failure context (your code, runtime errors, and failing test cases).
4. **Socratic Analysis:** Sends a constrained “tutor prompt” to Gemini via LangChain, extracting the core hint from the model's response blocks.
5. **Dual-Layer Logging:** Appends the full AI explanation to `study_guide.md` and logs the structured failure data (problem title, tags, error type) into the `leetcode_history.db` SQLite database for long-term tracking.

---

## Security Notes

- Treat `.env` as sensitive (it contains cookies + API key).
- Keep `.env` out of git (ensure `.gitignore` includes it).
- Rotate cookies and API keys if you suspect exposure.

---

## Troubleshooting

- **401/403 from LeetCode**: Cookies expired or missing. Re-copy `LEETCODE_SESSION` and `LEETCODE_CSRF` into your `.env` file.
- **No submissions detected**: Confirm `LEETCODE_USERNAME` is correct and you have recent submissions.
- **Gemini errors / invalid key**: Verify `GOOGLE_API_KEY` is valid and enabled in Google AI Studio.
- **503 Service Unavailable**: The Gemini API is experiencing high traffic. The daemon is designed to handle this gracefully; it will automatically wait 60 seconds and retry, so no action is needed!
- **RequestsDependencyWarning**: If your terminal shows a warning about `chardet` or `charset_normalizer`, it is completely harmless.
- **"No usable implementation found!" crash**: If your compiled `.exe` crashes with this error, PyInstaller failed to bundle the Windows notification libraries. Re-build the executable and ensure you include the `--hidden-import "plyer.platforms.win.notification"` flag.
- **Windows activation blocked**: You may need to allow script execution (PowerShell). See Microsoft guidance for `Set-ExecutionPolicy` (use the least permissive option that works for you).

---

## Roadmap / Future Improvements

- **Targeted practice generation**: Generate an “easy” drill problem tailored to the specific mistake detected.

---

## Disclaimer

This project is not affiliated with LeetCode. It relies on web/API behavior that may change.

