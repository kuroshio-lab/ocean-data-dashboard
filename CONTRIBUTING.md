# Contributing to Ocean Data Dashboard

Thank you for your interest in contributing to the Ocean Data Dashboard! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/ocean-dashboard.git
   cd ocean-dashboard
   ```
3. **Set up development environment**
   ```bash
   ./scripts/quickstart.sh
   # Or manually:
   make setup
   docker-compose up
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### 2. Make Changes

#### Backend (Django)

- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Write tests for new features
- Run linting before committing:
  ```bash
  cd backend
  black .
  isort .
  flake8
  ```

#### Frontend (Next.js/React)

- Use TypeScript for all new code
- Follow React best practices
- Use functional components with hooks
- Write meaningful component names
- Run linting before committing:
  ```bash
  cd frontend
  npm run lint
  npm run type-check
  ```

### 3. Write Tests

#### Backend Tests

```bash
cd backend
python manage.py test

# Test specific app
python manage.py test api

# With coverage
coverage run --source='.' manage.py test
coverage report
```

#### Frontend Tests

```bash
cd frontend
npm test
```

### 4. Commit Changes

Use conventional commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add endpoint for current observations

- Added CurrentObservation model
- Created serializer and viewset
- Added time-series endpoint
- Updated API documentation

Closes #123
```

```
fix(frontend): resolve chart rendering issue

Charts were not updating when location changed. Added
useEffect dependency to trigger re-fetch.

Fixes #456
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots (for UI changes)
- Test results

## Code Review Process

1. Automated checks must pass (CI/CD)
2. At least one reviewer approval required
3. Address review comments
4. Maintainer will merge when ready

## Testing Guidelines

### Backend

- Write unit tests for models and services
- Write integration tests for API endpoints
- Test edge cases and error handling
- Mock external API calls
- Aim for >80% code coverage

Example test:
```python
from django.test import TestCase
from api.models import Location

class LocationModelTest(TestCase):
    def test_location_creation(self):
        location = Location.objects.create(
            name="Test Location",
            latitude=36.0,
            longitude=-122.0,
            region="Pacific"
        )
        self.assertEqual(location.name, "Test Location")
        self.assertEqual(str(location), "Test Location (36.0, -122.0)")
```

### Frontend

- Test component rendering
- Test user interactions
- Test API integration
- Test error states
- Use React Testing Library

## Documentation

- Update README files when adding features
- Add JSDoc comments to functions
- Update API documentation
- Add examples for new features

## Performance Considerations

### Backend

- Use `select_related` and `prefetch_related` for queries
- Add database indexes for frequently queried fields
- Cache expensive computations
- Optimize Celery tasks

### Frontend

- Lazy load components when appropriate
- Optimize images
- Minimize bundle size
- Use React.memo for expensive components

## Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate and sanitize user input
- Follow OWASP best practices
- Report security issues privately to maintainers

## Database Migrations

When making model changes:

```bash
# Create migrations
python manage.py makemigrations

# Review migration file
# Then commit with your changes

# Apply in development
python manage.py migrate
```

## Questions?

- Open a GitHub issue
- Check existing documentation
- Ask in pull request comments

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🌊
