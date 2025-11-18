# System Prompts

This folder contains all system prompts used by the AI Content Management application. These prompts are separated from the code for easier management and security.

## Files

- **summarize.md** - Prompt for text summarization with key points extraction
- **translate.md** - Prompt for translating text while preserving tone and meaning
- **sentiment.md** - Prompt for sentiment analysis with confidence scoring
- **detect_language.md** - Prompt for detecting the language of input text

## Security Note

⚠️ **This folder is included in `.gitignore`** to prevent system prompts from being committed to version control. This allows you to customize prompts without exposing your prompt engineering strategies.

## Format

Each prompt file:

- Is written in plain text/markdown format
- Contains the complete system prompt for that specific task
- May use `{variable}` placeholders for dynamic content (e.g., `{target_language}`)
- Includes XML-like `<USER_CONTENT>` markers for prompt injection protection

## Customization

You can modify these prompts to:

- Adjust the output format
- Change the tone or style
- Add additional constraints or requirements
- Improve prompt injection protection

**Note:** After modifying prompts, test thoroughly to ensure the application still works as expected.
