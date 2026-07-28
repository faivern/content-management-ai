# AI Content Management

A command-line tool that solves common text-processing needs by using OpenAI to summarize, translate, and analyze the sentiment of text and PDF files.

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
