# Contributing to AIVIA

Thank you for your interest in contributing to AIVIA! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or request features
- Search existing issues before creating a new one
- Provide clear, detailed descriptions with steps to reproduce
- Include relevant system information (OS, Python version, etc.)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following our coding standards
4. Add tests if applicable
5. Update documentation as needed
6. Commit your changes with a clear message
7. Push to your fork and submit a pull request

## Commit Message Style

We follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies, etc.

### Examples:
```
feat(notebooks): add healthcare demo notebook
fix(neo4j): resolve connection timeout issue
docs(readme): update installation instructions
chore(deps): update pandas to v2.0
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and reasonably sized
- Add type hints where appropriate

## Testing

- Add tests for new functionality
- Ensure existing tests pass
- Test with both local Neo4j and Neo4j Aura

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions/classes
- Update examples if API changes
- Keep CHANGELOG.md updated

## Questions?

Feel free to open an issue for questions or discussions about the project.
