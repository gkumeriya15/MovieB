# Contributing Guidelines

Thank you for contributing to StreamBox!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Write tests
6. Submit a pull request

## Code Style

### Backend (Python)
- Use PEP 8 style guide
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions and classes

```python
def get_user(user_id: int) -> Optional[User]:
    """
    Get user by ID.
    
    Args:
        user_id: The user ID
        
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()
```

### Frontend (TypeScript/React)
- Use ESLint
- Use Prettier for formatting
- Use type annotations
- Use functional components with hooks

```typescript
interface UserProps {
  userName: string
  email: string
}

export const User: React.FC<UserProps> = ({ userName, email }) => {
  return (
    <div>
      <p>{userName}</p>
      <p>{email}</p>
    </div>
  )
}
```

## Git Workflow

### Commits
```bash
# Use conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: fix bug"
git commit -m "docs: update documentation"
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance
- `test`: Adding missing tests or correcting existing tests

### Branches
```bash
# Create feature branch
git checkout -b feature/user-authentication

# Create fix branch
git checkout -b fix/login-error

# Always branch from main
git checkout main
git pull origin main
```

## Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app

# Run with verbose output
pytest -v
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass: `pytest` or `npm test`
4. Update CHANGELOG.md
5. Submit PR with clear description

## PR Template

```markdown
## Description
Brief description of changes

## Type
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done...

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Project Structure

### Backend `/backend/app/`
```
app/
├── core/        # Config, database, security
├── models/      # SQLAlchemy ORM models
├── schemas/     # Pydantic schemas
├── routes/      # API endpoints
├── services/    # Business logic  
├── middleware/  # Custom middleware
├── utils/       # Utilities
└── main.py      # Entry point
```

### Frontend `/frontend/src/`
```
src/
├── pages/       # Next.js pages
├── components/  # React components
├── lib/         # Utilities & API
└── styles/      # CSS
```

## Adding a New Feature

### Backend
1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Create route in `app/routes/`
4. Add tests in `tests/`
5. Update API docs

### Frontend
1. Create component in `src/components/`
2. Create page in `src/pages/` if needed
3. Update API client in `src/lib/api.ts`
4. Add tests

## Reporting Bugs

Use GitHub Issues with this template:

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: ...
- Python/Node version: ...
- Browser: ...
```

## Performance Guidelines

### Backend
- Use database indexing for frequently queried fields
- Implement pagination for large datasets
- Use caching for expensive operations
- Minimize database queries (use joins)

### Frontend
- Code split large components
- Lazy load images
- Memoize components appropriately
- Use React.memo for large lists

## Documentation

- Docstrings for all functions
- Comments for complex logic
- Update README for major changes
- Keep API docs in sync

---

Thank you for contributing! 🚀
