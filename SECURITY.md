# Security Policy

## Supported Versions

We currently support the following versions of AIVIA:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in AIVIA, please report it responsibly.

### How to Report

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email security concerns to: [INSERT SECURITY EMAIL]
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- We will acknowledge receipt within 48 hours
- We will provide regular updates on our progress
- We will credit you in our security advisories (unless you prefer to remain anonymous)

### Scope

This security policy applies to:
- The AIVIA codebase and dependencies
- Documentation and examples
- Demo notebooks and sample data

### Out of Scope

- Issues with third-party services (Neo4j, OpenAI, etc.)
- Synthetic/demo data (no real sensitive information)
- Local development environment issues

## Security Considerations

### Current Status
- **No secrets in code**: All demo data is synthetic
- **No production credentials**: Uses local Neo4j or demo endpoints
- **Minimal dependencies**: Only essential packages included

### Best Practices
- Always use environment variables for sensitive configuration
- Keep dependencies updated
- Use virtual environments for isolation
- Review code changes for security implications

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.1, 0.1.2) and will be clearly marked in the CHANGELOG.md.

## Thank You

We appreciate your help in keeping AIVIA secure for all users.
