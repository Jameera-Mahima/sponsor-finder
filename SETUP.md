# Sponsor Finder Setup Guide

Quick start guide for setting up the Sponsor Finder system with OpenAI.

## Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Jameera-Mahima/sponsor-finder.git
cd sponsor-finder
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `requests`, `beautifulsoup4` - Web scraping tools
- `pandas` - Data handling
- `colorama` - Enhanced logging

### 3. Configure OpenAI API Key

**Create `.env` file:**

```bash
cp .env.example .env
```

**Edit `.env` and add your API key:**

```env
OPENAI_API_KEY=your-actual-api-key-here
OPENAI_MODEL_FAST=gpt-4o-mini
OPENAI_MODEL_QUALITY=gpt-4o
USE_OPENAI=true
```

**Important:** Never commit the `.env` file! It's already in `.gitignore` for your protection.

### 4. Verify Configuration

Run the example script to test your setup:

```bash
python openai_agent_example.py
```

You should see output showing keyword extraction and model configuration.

## Project Structure

```
sponsor-finder/
├── .env                    # Your API keys (DO NOT COMMIT)
├── .env.example           # Template for .env file
├── config.py              # Configuration loader
├── openai_agent_example.py # Usage examples
├── requirements.txt       # Python dependencies
├── CLAUDE.md             # Project documentation
├── .claude/              # Agent and skill definitions
│   ├── agents/          # 8 agent definitions
│   ├── commands/        # Platform integration commands
│   └── skills/          # Custom workflows
├── docs/                # Generated reports and documentation
├── logs/                # Execution logs and dashboard
└── specs/               # System specifications
```

## Usage

### Running the Workflow

The system is designed to work with Claude Code. To run a sponsor search:

1. Open Claude Code in this directory
2. Use the workflow command or agents directly
3. Example: "Find sponsors for arts education in NYC"

### Using Individual Agents

Each agent can be invoked through Claude Code's Task tool:

```
Phase 1: Keyword Extraction
  Agent: keyword-extractor
  Model: gpt-4o-mini

Phase 2: Web Research
  Agent: web-researcher
  Model: gpt-4o-mini

Phase 3: Categorization
  Agent: categorizer
  Model: gpt-4o-mini

Phase 4: Validation
  Agent: validator
  Model: gpt-4o (higher quality)
```

### Custom Commands

- `/sync` - Stage, commit, and push changes
- `/checkpoint` - Create local WIP commits
- `/quick-commit` - Smart commit with user approval
- `/save-report` - Commit sponsor reports

## Model Selection

The system automatically uses the right model for each task:

- **Fast tasks** (gpt-4o-mini): Keyword extraction, categorization, data formatting
- **Quality tasks** (gpt-4o): Validation, analytics, strategic coordination

You can customize model selection in `config.py`.

## Troubleshooting

### "OPENAI_API_KEY not found" error

Make sure:
1. `.env` file exists in project root
2. File contains `OPENAI_API_KEY=your-key`
3. No extra spaces around the `=` sign

### "openai package not installed" error

```bash
pip install openai
```

### API rate limits

If you hit rate limits:
1. Add delays between requests
2. Use gpt-4o-mini for more requests
3. Upgrade your OpenAI plan

## Security Best Practices

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Rotate API keys regularly** - Update in `.env` only
3. **Use environment-specific keys** - Different keys for dev/prod
4. **Monitor API usage** - Check OpenAI dashboard regularly

## Getting Help

- Check `CLAUDE.md` for detailed project documentation
- See `openai_agent_example.py` for code examples
- Review agent definitions in `.claude/agents/`
- Check logs in `logs/` directory for debugging

## Next Steps

1. Run the test workflow: See logs/test_run_*.log for example
2. Review campaign scenarios: `docs/operations/Campaign_Scenarios.md`
3. Explore agent definitions: `.claude/agents/`
4. Check the system architecture: `docs/diagrams/`

## Contributing

When contributing:
1. Never commit `.env` files
2. Use `/quick-commit` for meaningful commit messages
3. Test with `/sync` before creating PRs
4. Update documentation when adding features
