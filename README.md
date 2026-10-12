# RCA Automation Engine (LangGraph & Gemini AI)

An automated Root Cause Analysis (RCA) email processor built with **LangGraph**, **Gemini 2.5/3.8 Flash**, and **MS SQL Server**. This tool monitors incoming internal support emails, extracts targeted contact identifiers, queries core operational databases, and drafts automated context-aware responses.

## 🌟 Key Features
- **State Graph Workflow:** Structured linear node pipeline using `LangGraph` (`fetch_email` -> `extract_phone` -> `sql_lookup` -> `draft_reply`).
- **Hybrid Extraction:** Primary extraction using Regex & BeautifulSoup with fallback to Gemini LLM for unstructured text parsing.
- **SQL Database Integration:** Queries ODBC SQL databases to link secondary/alternate contacts to primary account IDs.
- **Automated Gmail Integration:** Checks targeted IMAP labels and queues response drafts to Gmail via IMAP append commands.

## 📁 Repository Structure
├── App.py                     # Standalone CLI/Script execution module
├── Rca_Langraph.ipynb         # Jupyter Notebook with LangGraph development steps
├── .gitignore                 # Excluded environments and sensitive data
└── requirements.txt           # Python dependencies


# 🛠️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/abhishekmukherjee60/RCA_Email_Automation.git](https://github.com/abhishekmukherjee60/RCA_Email_Automation.git)


   
