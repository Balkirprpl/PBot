# Policing Bot

## Overview
PBot's idea come from the extensive use of fake users in social media, and AI has made them even harder to distinguish from real accounts.
Running this program should allow the user to distinguish between real people, bots, and malicious bots. The scans can be performed in two modes: Single Search and Submission Search

### SINGLE SEARCH:
- Analyzes a single user for bot behavior and maliciousness.
### SUBMISSION SEARCH:
- Finds users in Subreddits by New, Hot, or Top submissions.
- Analyzes each users account history and gives a veredict.
- Allows the user to set the depth of search.
- Stores findings in database-friendly format.

## How to Use
1. Clone this repo:
   ```bash
   git clone https://github.com/Balkirprpl/PBot.git
   cd PBot
2. Install Dependencies:
  ```
pip install -r requirements.txt
```
4. Create and configure a 'keys.py' file API keys:
``` 
File: PBot/keys.py
───────┼────────────────────────────────────────────────────────────────────────
   1   │ key = "<secret key>"
   2   │ client = "<client key>"
   3   │ user_agent ="<user agent>"
