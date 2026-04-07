## LeetCode AI Tutor Agent

An autonomous, locally-hosted AI engineering tool that monitors your LeetCode profile, detects failed submissions, and provides **Socratic, spoiler-free tutoring** using **Google Gemini** (via LangChain).

Built to transform the LeetCode grind into a guided learning loop, this agent acts like a strict but helpful tutor: it highlights logical gaps, surfaces edge cases, and asks guiding questions—**without writing the full solution for you**.

---

## Key Features

- **Automated data fetching**: Uses LeetCode’s GraphQL endpoint to pull recent submission status, code, and failed test cases.
- **Socratic AI analysis**: Uses Gemini via LangChain with “teacher-mode” prompts to focus on reasoning, not answer-dumping.
- **Study guide generation**: Logs failed attempts, error output, and tailored guidance into a local, timestamped `study_guide.md`.
- **Secure-by-default workflow**: Uses `.venv` and `python-dotenv` so cookies and API keys stay local and out of version control.

---

## Tech Stack

- **Language**: Python 3
- **AI orchestration**: LangChain (`langchain-google-genai`)
- **LLM**: Google Gemini (configured in code; default: `gemini-2.5-flash`)
- **Network / API**: `requests`, GraphQL
- **Environment**: `python-dotenv`

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

1. Submit a problem on LeetCode (failing one is a good test).
2. Run:

```bash
python main.py
```

---

## How It Works (High Level)

1. Fetch recent submission metadata from LeetCode (GraphQL)
2. Detect failed submissions
3. Pull relevant failure context (code + failing cases/output when available)
4. Send a constrained “tutor prompt” to Gemini via LangChain
5. Append results to `study_guide.md` for later review

---

## Security Notes

- Treat `.env` as sensitive (it contains cookies + API key).
- Keep `.env` out of git (ensure `.gitignore` includes it).
- Rotate cookies and API keys if you suspect exposure.

---

## Troubleshooting

- **401/403 from LeetCode**: Cookies expired or missing. Re-copy `LEETCODE_SESSION` and `LEETCODE_CSRF`.
- **No submissions detected**: Confirm `LEETCODE_USERNAME` is correct and you have recent submissions.
- **Gemini errors / invalid key**: Verify `GOOGLE_API_KEY` is valid and enabled in Google AI Studio.
- **Windows activation blocked**: You may need to allow script execution (PowerShell). See Microsoft guidance for `Set-ExecutionPolicy` (use the least permissive option that works for you).

---

## Roadmap / Future Improvements

- **Continuous polling**: Run as a background daemon to trigger instantly after a failed submission.
- **Targeted practice generation**: Generate an “easy” drill problem tailored to the specific mistake detected.
- **SQLite logging**: Replace Markdown-only history with a queryable local database (failure types over time, topic trends, etc.).

---

## Disclaimer

This project is not affiliated with LeetCode. It relies on web/API behavior that may change.

