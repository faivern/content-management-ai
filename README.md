# AI Content Management

AI Content Management helps teams turn unstructured text and PDF content into actionable business insights. It reduces the time spent reviewing documents by providing on-demand summaries, translations, and sentiment analysis.

For example, a customer-success team can analyze customer feedback files to quickly identify negative sentiment, understand recurring concerns, and prioritize follow-up actions.

## Linux installation

```bash
git clone https://github.com/faivern/content-management-ai.git
cd content-management-ai

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

cp env.example .env
${EDITOR:-nano} .env

python3 main.py
```

## Windows installation

Run in PowerShell:

```powershell
git clone https://github.com/faivern/content-management-ai.git
cd content-management-ai

py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt

Copy-Item env.example .env
notepad .env

py main.py
```
