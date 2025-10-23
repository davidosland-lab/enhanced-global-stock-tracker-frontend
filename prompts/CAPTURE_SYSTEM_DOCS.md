# Prompt Capture System Documentation

## Overview
An automatic system for capturing, organizing, and archiving user prompts to GitHub. Every prompt is saved with metadata, categorized by topic, and committed to version control.

## Features

### 🎯 Core Features
- **Automatic Capture**: Save prompts with single function call
- **Topic Classification**: Automatically categorize prompts by content
- **Git Integration**: Auto-commit to GitHub for version tracking
- **Metadata Tracking**: Timestamp, word count, context, and more
- **Web Interface**: User-friendly HTML interface for manual capture
- **REST API**: Webhook endpoint for programmatic capture
- **Statistics**: Track usage patterns and analytics

### 📁 Organization Structure
```
prompts/
├── daily/                  # Prompts organized by date
│   └── 2025-10-01/        # Daily folders
│       └── [prompt_id].md # Individual prompt files
├── by_topic/              # Prompts organized by topic
│   ├── github/            # GitHub-related prompts
│   ├── backend/           # Backend prompts
│   ├── frontend/          # Frontend prompts
│   └── ...               # Other topics
├── metadata/              # JSON metadata files
│   └── [prompt_id].json  # Metadata for each prompt
├── INDEX.md               # Master index of all prompts
└── README.md              # Basic documentation
```

## Installation & Setup

### 1. Basic Setup
The system is already installed in `/home/user/webapp/prompts/`

### 2. Start the Capture Service
```bash
cd /home/user/webapp/prompts
./start_capture_service.sh
```

This starts the webhook API on port 8003.

### 3. Access the Web Interface
Open in your browser: `http://localhost:8003/capture_interface.html`

## Usage Methods

### Method 1: Python Script
```python
from prompt_capture_system import PromptCaptureSystem

system = PromptCaptureSystem()
prompt_id = system.capture_and_save(
    prompt="Your prompt text here",
    context={"user": "username", "session": "session_id"}
)
```

### Method 2: REST API
```bash
curl -X POST http://localhost:8003/capture \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Your prompt text here",
    "user": "username",
    "tags": ["tag1", "tag2"],
    "auto_commit": true
  }'
```

### Method 3: Web Interface
1. Navigate to `http://localhost:8003/capture_interface.html`
2. Enter prompt text
3. Add optional tags and user info
4. Click "Capture Prompt"

### Method 4: Direct Function Call
```python
from prompts.prompt_capture_system import capture_current_prompt

prompt_id = capture_current_prompt("Your prompt text here")
```

## API Endpoints

### POST /capture
Capture a new prompt

**Request Body:**
```json
{
  "prompt": "string",
  "user": "string (optional)",
  "tags": ["array", "of", "tags"],
  "auto_commit": true,
  "context": {}
}
```

**Response:**
```json
{
  "success": true,
  "prompt_id": "20251001_213638_a6f37c37",
  "topic": "github",
  "word_count": 20,
  "timestamp": "2025-10-01T21:36:38",
  "message": "Prompt captured successfully"
}
```

### GET /stats
Get capture statistics

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_prompts": 42,
    "topics": {"github": 10, "backend": 15, ...},
    "daily_counts": {"2025-10-01": 5, ...},
    "total_words": 2500,
    "average_words": 60
  }
}
```

### GET /prompts
List recent prompts

**Query Parameters:**
- `limit`: Number of prompts to return (default: 10)

### GET /health
Health check endpoint

## File Format

### Prompt File (.md)
```markdown
# Prompt: [prompt_id]

**Date**: 2025-10-01
**Time**: 21:36:38
**Topic**: github
**Words**: 20

## Prompt Content

```
Your actual prompt text here
```

## Context

```json
{
  "user": "username",
  "session": "session_id",
  "timestamp": "2025-10-01T21:36:38"
}
```
```

### Metadata File (.json)
```json
{
  "id": "20251001_213638_a6f37c37",
  "timestamp": "2025-10-01T21:36:38",
  "date": "2025-10-01",
  "time": "21:36:38",
  "topic": "github",
  "prompt_length": 95,
  "word_count": 20,
  "context": {
    "user": "username",
    "session": "session_id"
  }
}
```

## Topic Classification

The system automatically classifies prompts into topics based on keywords:

- **github**: Git, push, pull, commit
- **backend**: Backend, API, server
- **frontend**: Frontend, UI, HTML, CSS
- **documentation**: Docs, README, documentation
- **testing**: Test, debug, QA
- **deployment**: Deploy, production, release
- **feature**: Feature, enhancement, add
- **bugfix**: Fix, bug, error, issue
- **refactoring**: Refactor, clean, organize
- **automation**: Automatic, routine, webhook
- **general**: Default for unclassified prompts

## Integration Examples

### Integration with Claude/ChatGPT
```python
# Capture every interaction
def on_user_message(message):
    capture_current_prompt(message)
    # Process message normally
    return ai_response
```

### Integration with Web Application
```javascript
// Capture form submissions
async function captureUserInput(input) {
    await fetch('http://localhost:8003/capture', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            prompt: input,
            user: getCurrentUser(),
            tags: extractTags(input)
        })
    });
}
```

### Integration with CLI Tools
```bash
#!/bin/bash
# Capture command-line prompts
function capture_prompt() {
    curl -X POST http://localhost:8003/capture \
      -H "Content-Type: application/json" \
      -d "{\"prompt\": \"$1\", \"user\": \"$USER\"}"
}

# Usage
capture_prompt "Your CLI prompt here"
```

## Git Workflow

The system automatically commits captured prompts:

1. Each prompt capture triggers a Git add
2. Commits with descriptive message: `feat(prompts): Capture prompt [id] [topic]`
3. Maintains clean commit history
4. Can be pushed to GitHub manually or via automation

### Manual Push
```bash
cd /home/user/webapp
git push origin main
```

### Automatic Push (add to crontab)
```bash
# Add to crontab for hourly push
0 * * * * cd /home/user/webapp && git push origin main
```

## Statistics & Analytics

Access statistics through:
1. Web interface statistics panel
2. API endpoint: `GET /stats`
3. Python script: `system.get_statistics()`

Tracked metrics:
- Total prompts captured
- Prompts per day
- Average word count
- Topic distribution
- User activity (if tracked)

## Troubleshooting

### Service Won't Start
```bash
# Check if port 8003 is in use
lsof -i :8003

# Kill existing process if needed
kill -9 [PID]
```

### Git Commit Fails
```bash
# Check Git status
cd /home/user/webapp
git status

# Fix any issues
git add prompts/
git commit -m "Manual prompt capture commit"
```

### No Data Showing
```bash
# Check file permissions
ls -la prompts/

# Check service logs
python3 prompts/auto_capture_webhook.py
```

## Security Considerations

1. **Local Only**: Default setup only accepts localhost connections
2. **No Authentication**: Add auth layer for production use
3. **Input Validation**: Prompts are sanitized before saving
4. **Git Credentials**: Ensure secure credential storage

## Future Enhancements

Potential improvements:
- [ ] Machine learning for better topic classification
- [ ] Prompt similarity detection
- [ ] Analytics dashboard
- [ ] Export functionality (PDF, CSV)
- [ ] Search capabilities
- [ ] Prompt templates
- [ ] Team collaboration features
- [ ] Encryption for sensitive prompts

## License

Part of the ASX Market Dashboard project. See main project license.