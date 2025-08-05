# Contributing to Discord Bot

Thank you for your interest in contributing to this Discord bot! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Git

### Development Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/discord-bot.git
   cd discord-bot
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy environment template:
   ```bash
   cp .env.example .env
   ```
6. Edit `.env` with your bot token and configuration

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

### Commit Messages
Use conventional commits format:
- `feat: add new music command`
- `fix: resolve queue management issue`
- `docs: update README with new commands`
- `refactor: improve error handling`

### Pull Request Process
1. Create a feature branch:
   ```bash
   git checkout -b feature/new-music-command
   ```
2. Make your changes
3. Test thoroughly:
   ```bash
   python enhanced_bot.py  # Test basic functionality
   ```
4. Run linting:
   ```bash
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
   ```
5. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add new music command"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/new-music-command
   ```
7. Create a Pull Request

## Adding New Features

### New Commands
1. **Prefix Commands**: Add to appropriate cog file in `cog/`
2. **Slash Commands**: Add to bot.tree.command() in enhanced_bot.py
3. **Error Handling**: Always include proper error handling
4. **Documentation**: Update README.md with new commands

### Testing Checklist
- [ ] Command works in Discord
- [ ] Error messages are user-friendly
- [ ] No console errors
- [ ] Documentation updated
- [ ] Code follows style guidelines

## Reporting Issues

### Bug Reports
Include:
- Bot version/commit hash
- Steps to reproduce
- Expected vs actual behavior
- Error messages/screenshots
- Discord.py version

### Feature Requests
Include:
- Clear description of the feature
- Use case examples
- Potential implementation approach
- Impact on existing functionality

## Security

### Sensitive Information
- Never commit tokens or API keys
- Use environment variables for configuration
- Review code for potential security issues
- Test permissions thoroughly

### Bot Permissions
- Request minimum necessary permissions
- Document required permissions clearly
- Test with restricted permissions

## Code Review Process

### What We Look For
- Code quality and readability
- Proper error handling
- Documentation updates
- Test coverage
- Security considerations
- Performance impact

### Review Criteria
- Does it solve the intended problem?
- Is it maintainable?
- Does it follow established patterns?
- Are there adequate tests?
- Is documentation complete?

## Getting Help

### Resources
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Python Discord](https://discord.gg/python) - Great community for help

### Communication
- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for questions and ideas
- Be respectful and constructive in all interactions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
