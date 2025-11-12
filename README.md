# AI Content Management

A powerful CLI application for intelligent text analysis using OpenAI's GPT-5-Nano model. Perform summarization, translation, and sentiment analysis on `.txt` and `.pdf` files with automatic language detection and structured JSON output.

## Features

### Core Capabilities

- **📝 Text Summarization**: Generate concise summaries with 3-5 key points
- **🌍 Translation**: Translate text to any language while preserving tone and meaning
- **😊 Sentiment Analysis**: Detect sentiment (positive/neutral/negative) with confidence scores
- **📄 Multi-Format Support**: Process both `.txt` and `.pdf` files
- **🔍 Language Detection**: Automatic language identification for all input texts

### Technical Features

- **🔒 Security-First Design**:
  - Environment-based API key management (no hardcoded secrets)
  - Dual prompt injection protection (input isolation + JSON schema validation)
  - Strict JSON response validation
- **🔄 Robust Error Handling**:
  - Automatic retry logic for API calls (3 attempts with exponential backoff)
  - Clear error messages for all failure scenarios
  - Graceful degradation
- **💾 Structured Output**:
  - ISO8601 timestamps
  - Automatic word count and language detection
  - Timestamped JSON files: `filename_usecase_YYYY-MM-DD_HH-MM-SS.json`

## Project Structure

```
content-management-ai/
├── main.py                 # CLI entry point
├── src/
│   ├── __init__.py
│   ├── file_handler.py     # File reading and validation
│   ├── api_client.py       # OpenAI integration with security
│   ├── processors.py       # Use case orchestration
│   └── output_manager.py   # JSON output management
├── tests/
│   └── test_app.py         # Comprehensive test suite
├── sample_files/           # Example files for testing
│   ├── ai_overview.txt
│   ├── climate_change.txt
│   └── negative_review.txt
├── output/                 # Generated JSON results
├── requirements.txt
├── .env.example           # Environment template
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup Steps

1. **Clone or download the repository**

   ```bash
   cd content-management-ai
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-actual-key-here
   # OPENAI_MODEL=gpt-4-turbo-preview
   ```

## Usage

### Running the Application

```bash
python main.py
```

### Workflow

1. **Welcome Screen**: The application greets you with available options
2. **Choose Action**: Select from:
   - `1` - Summarize
   - `2` - Translate
   - `3` - Sentiment Analysis
   - `4` - Exit
3. **Provide File Path**: Enter absolute path to your `.txt` or `.pdf` file
4. **View Results**: Results are displayed in the terminal
5. **Automatic Save**: JSON file saved to `./output/` directory

### Example Session

```

```

============================================================
AI Content Management System
============================================================
Text Analysis powered by OpenAI GPT-5-Nano
============================================================

Available Actions:

1. Summarize - Generate summary and key points
2. Translate - Translate text to another language
3. Sentiment - Analyze sentiment and tone
4. Exit

```

Select option (1-4): 1

Enter file path:
> /home/user/documents/article.txt

⚙ Reading file...
⚙ Detecting language...
⚙ Generating summary...
✓ Processing complete

============================================================
RESULTS
============================================================

Summary:
[Your summary appears here]

Key Points:
  1. [Key point 1]
  2. [Key point 2]
  3. [Key point 3]

============================================================

⚙ Saving results...
✓ Results saved to: output/article_summarize_2025-11-12_15-43-22.json
```

## Output Format

All results are saved as JSON with the following schema:

```json
{
  "file": "document_name",
  "use_case": "summarize|translate|sentiment",
  "timestamp": "2025-11-12T15:43:22.123456",
  "result": {
    // Use case specific results
  },
  "word_count": 1234,
  "language_detected": "English"
}
```

### Summarization Output

```json
{
  "file": "ai_overview",
  "use_case": "summarize",
  "timestamp": "2025-11-12T15:43:22.123456",
  "result": {
    "summary": "Concise 2-3 sentence summary...",
    "key_points": ["First key point", "Second key point", "Third key point"]
  },
  "word_count": 234,
  "language_detected": "English"
}
```

### Translation Output

```json
{
  "file": "climate_change",
  "use_case": "translate",
  "timestamp": "2025-11-12T15:45:10.789012",
  "result": {
    "translated_text": "El planeta está enfrentando...",
    "target_language": "Spanish",
    "source_language": "English"
  },
  "word_count": 189,
  "language_detected": "English"
}
```

### Sentiment Analysis Output

```json
{
  "file": "negative_review",
  "use_case": "sentiment",
  "timestamp": "2025-11-12T15:47:33.456789",
  "result": {
    "sentiment": "negative",
    "confidence": 0.95,
    "explanation": "The text expresses strong dissatisfaction..."
  },
  "word_count": 267,
  "language_detected": "English"
}
```

## Security Features

### 1. API Key Protection

- API keys stored in `.env` file (excluded from version control)
- No hardcoded credentials
- Clear error messages if API key is missing

### 2. Prompt Injection Protection

**Protection Layer 1: Input Isolation**

```python
# User content wrapped in XML-like markers
<USER_CONTENT>
{user_provided_text}
</USER_CONTENT>
```

**Protection Layer 2: Strict JSON Schema Validation**

- All API responses validated against expected schema
- Required fields checked
- Type validation enforced
- Invalid responses rejected

### 3. Error Handling

- Retry logic with exponential backoff
- File validation before processing
- Graceful error messages
- Exit codes for automation

## Testing

The project includes a comprehensive test suite covering:

- File handling (txt/pdf reading, validation)
- Output management (JSON generation, schema validation)
- Integration tests for all three use cases

### Running Tests

```bash
# Make sure you have a .env file configured
python -m pytest tests/test_app.py -v
```

### Test Coverage

- ✅ File validation and reading
- ✅ Word counting
- ✅ Output filename generation
- ✅ JSON schema validation
- ✅ Complete summarization workflow
- ✅ Complete translation workflow
- ✅ Complete sentiment analysis workflow

## Requirements

```
openai>=1.3.0       # OpenAI API client
PyPDF2>=3.0.0       # PDF text extraction
python-dotenv>=1.0.0 # Environment variable management
pytest>=7.4.0       # Testing framework
```

## Troubleshooting

### "OPENAI_API_KEY not found"

- Ensure `.env` file exists in project root
- Verify `OPENAI_API_KEY=sk-...` is set correctly
- No quotes needed around the key

### "Unsupported file type"

- Only `.txt` and `.pdf` files are supported
- Check file extension is lowercase or uppercase

### "Could not extract text from PDF"

- PDF may be scanned/image-based (OCR not supported)
- Try converting to text-based PDF or use `.txt` file

### "API call failed after 3 attempts"

- Check your internet connection
- Verify API key is valid and has credits
- Check OpenAI service status

## Development

### Adding New Use Cases

1. Add method to `APIClient` in `src/api_client.py`
2. Add processing method to `TextProcessor` in `src/processors.py`
3. Add CLI handler in `main.py`
4. Update menu options
5. Add tests in `tests/test_app.py`

### Environment Variables

| Variable         | Required | Default               | Description         |
| ---------------- | -------- | --------------------- | ------------------- |
| `OPENAI_API_KEY` | Yes      | -                     | Your OpenAI API key |
| `OPENAI_MODEL`   | No       | `gpt-4-turbo-preview` | Model to use        |

## License

This project is for educational purposes. Please ensure you comply with OpenAI's usage policies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues or questions:

- Check the troubleshooting section
- Review test files for usage examples
- Consult OpenAI documentation for API-related issues

---

**Built with ❤️ using OpenAI GPT-5-Nano**
