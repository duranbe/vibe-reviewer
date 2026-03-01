```
 __      _______ ____  ______                                    
 \ \    / /_   _|  _ \|  ____|                                   
  \ \  / /  | | | |_) | |__                                      
   \ \/ /   | | |  _ <|  __|                                     
    \  /   _| |_| |_) | |____                                    
  ___\/  _|_____|____/|______| ________          ________ _____  
 |  __ \|  ____\ \    / /_   _|  ____\ \        / /  ____|  __ \ 
 | |__) | |__   \ \  / /  | | | |__   \ \  /\  / /| |__  | |__) |
 |  _  /|  __|   \ \/ /   | | |  __|   \ \/  \/ / |  __| |  _  / 
 | | \ \| |____   \  /   _| |_| |____   \  /\  /  | |____| | \ \ 
 |_|  \_\______|   \/   |_____|______|   \/  \/   |______|_|  \_\

```                                                              

**Vibe Reviewer** is an AI-powered code review tool that leverages Mistral's advanced language models to provide intelligent, context-aware feedback on your pull requests.

## Features

- **AI-Powered Reviews**: Get detailed, intelligent code reviews powered by Mistral AI
- **GitHub Actions Integration**: Seamlessly integrate with your CI/CD pipeline
- **Context-Aware Analysis**: Understands code changes in context
- **Customizable**: Configure review depth and focus areas
- **Lightweight**: Easy to set up and use
- **Security Guardrails**: Built-in protection against information leakage with comprehensive regex pattern matching

## Installation

### Prerequisites

- Python 3.8+
- GitHub account with repository access
- Mistral API key (or compatible LLM API)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/vibe-reviewer.git
   cd vibe-reviewer
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure GitHub Actions:**
   - Add the workflow file to your repository's `.github/workflows/` directory
   - Configure your Mistral API key as a GitHub secret

## Usage

### Basic Usage

1. **Create a `review.md` file** in your repository root with your review instructions:
   ```markdown
   # Review Instructions
   
   Please review this PR for:
   - Code quality
   - Security issues
   - Performance considerations
   - Documentation completeness
   ```

2. **Push your changes** and the review will automatically trigger via GitHub Actions

### Command Line

You can also run Vibe Reviewer locally:

```bash
python -m vibe_reviewer --pr-number 123 --repo-owner yourusername --repo-name yourrepo
```

## Configuration

### Environment Variables

- `MISTRAL_API_KEY`: Your Mistral API key
- `GITHUB_TOKEN`: GitHub personal access token
- `REVIEW_DEPTH`: Control the depth of analysis (default: "medium")

### Customizing Reviews

Create or modify the `review.md` file in your repository root to specify what aspects of the code you want reviewed. Example:

```markdown
# Review Instructions

Focus on:
- Security best practices
- Error handling
- Code readability
- Type safety
- Documentation
```

## How It Works

1. **Pull Request Detection**: Vibe Reviewer detects new pull requests
2. **Code Analysis**: It analyzes the diff and context of changes
3. **AI Review**: Mistral AI generates detailed feedback
4. **Comment Posting**: Reviews are posted as comments on the PR

## Examples

### Example Review Output

```
## Code Review Summary

### Overall Assessment
The changes look good overall with minor improvements suggested.

### Detailed Feedback

**File: `src/main.py`**
- Good use of type hints
- Consider adding error handling for file operations
- Add docstring for the `process_data` function

**File: `tests/test_main.py`**
- Comprehensive test coverage
- Add test for edge case: empty input
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For issues or questions, please open an issue on GitHub.

## Security

### Guardrails

Vibe Reviewer includes comprehensive security guardrails to prevent information leakage:

- **Automated Pattern Detection**: Uses regex patterns from [truffleHogRegexes](https://github.com/dxa4481/truffleHogRegexes) to detect sensitive information
- **Response Filtering**: All AI responses are scanned for sensitive data before being returned
- **Safety Instructions**: System prompt includes explicit instructions to never generate or suggest real API keys, secrets, or credentials
- **Supported Patterns**:
  - API keys (AWS, Google, GitHub, Slack, etc.)
  - Private keys (RSA, SSH, PGP)
  - OAuth tokens
  - Passwords in URLs
  - And many more security-sensitive patterns

If sensitive information is detected in an AI response, it will be blocked and a security violation notice will returned instead.

### Best Practices

- Never commit API keys or secrets to your repository
- Use GitHub Secrets for sensitive configuration
- Review AI-generated code carefully before merging
- Keep your Mistral API key secure

## Disclaimer

This tool is not affiliated with Mistral AI. Use at your own risk.

## Hackathon

This project was created during the **Mistral Hackathon 2026** as an innovative approach to AI-powered code reviews.
=======
