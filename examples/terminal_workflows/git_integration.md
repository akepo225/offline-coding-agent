# Git Integration Workflows with Aider

> Complete guide for using Aider with Git in restricted environments, specifically optimized for Bitbucket web interface compatibility.

## 🔀 Git Setup for Restricted Environments

### Initial Git Configuration

```bash
# Configure Git user (required for commits)
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# Verify configuration
git config --global --list

# Configure line endings (Windows)
git config --global core.autocrlf true
```

### Repository Setup

```bash
# Initialize new repository
git init

# Or clone existing repository
git clone https://bitbucket.org/company/project.git
cd project

# Check status
git status
```

## 🚀 Aider + Git Workflows

### Workflow 1: Basic Git Operations with Aider

```bash
# Start Aider in your Git repository
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Create or modify files
/add src/main.py
> Create a Python application with basic structure and error handling

# Review changes
/diff

# Commit with Aider-generated message
/commit

# Aider will show you the commit message and ask for confirmation
# Press 'y' to accept or edit the message

# Check Git status
/git
```

### Workflow 2: Feature Development

```bash
# Start Aider
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Create a new feature
/add src/user_auth.py
> Implement user authentication system with login, logout, and session management

# Add tests
/add tests/test_auth.py
> Create comprehensive unit tests for the authentication system

# Review all changes
/diff

# Commit feature
/commit "Add user authentication system with comprehensive tests"

# Create documentation
/add docs/authentication.md
> Write documentation explaining how to use the authentication system

# Commit documentation
/commit "Add authentication documentation"

# Check Git log
git log --oneline -5
```

### Workflow 3: Bug Fixing

```bash
# Create hotfix branch first
git checkout -b hotfix/empty-list-bug

# Start Aider with problematic file
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf src/buggy_module.py

# Describe the bug
> This function is throwing an IndexError when processing empty lists. Please fix the bug and add proper input validation.

# Review the fix
/diff

# Test the fix
> Add unit tests to verify the fix works for edge cases including empty lists, None values, and invalid inputs.

# Commit the bug fix
/commit "Fix IndexError in process_data function and add input validation"

# (optional) Switch back when done
git checkout main
```

## 🌐 Bitbucket Integration

### Workflow 1: Offline Development, Online Sync

```bash
# Work offline with Aider
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Make changes and commit locally
/add src/
> Implement new feature for data export functionality
/commit "Add data export feature with CSV and JSON support"

# Continue working offline
/add tests/test_export.py
> Add comprehensive tests for data export functionality
/commit "Add tests for data export feature"

# When ready to sync (use web interface)
# 1. Open Bitbucket in browser
# 2. Go to your repository
# 3. Upload changes or use web-based Git if available
```

### Workflow 2: Branch Management

```bash
# Create feature branch (manual Git)
git checkout -b feature/user-dashboard

# Start Aider for feature development
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Develop feature
/add src/dashboard.py
> Create user dashboard with data visualization components

/add templates/dashboard.html
> Create HTML template for the user dashboard

/add static/dashboard.css
> Add styling for the dashboard

# Commit feature work
/commit "Implement user dashboard with visualization"

# Continue development
/add tests/test_dashboard.py
> Add tests for dashboard functionality
/commit "Add dashboard tests"

# Merge to main (manual Git operations)
git checkout main
git merge feature/user-dashboard
git push origin main  # If push is available
```

### Workflow 3: Working with Pull Requests (Web-based)

```bash
# Develop feature in branch
git checkout -b feature/api-improvements

# Use Aider for development
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

/add src/api.py
> Improve REST API with better error handling and pagination

/add docs/api_changes.md
> Document the API improvements and breaking changes

/commit "Improve REST API with pagination and better error handling"

# Push changes (if possible) or prepare for web-based PR
git add .
git commit -m "Ready for review: API improvements"

# Create pull request via Bitbucket web interface:
# 1. Go to Bitbucket repository
# 2. Click "Create pull request"
# 3. Select source and target branches
# 4. Add description and create PR
```

## 📝 Advanced Git Workflows

### Workflow 1: Staging and Selective Commits

```bash
# Start Aider
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Work on multiple features
/add src/auth.py
> Implement authentication system

/add src/database.py
> Add database connection and utilities

/add config/settings.py
> Create configuration management

# Review all changes
/diff

# Commit specific changes (manual staging)
git add src/auth.py
git commit -m "Add authentication system"

# Continue with Aider for other changes
/commit "Add database utilities and configuration"

# Check commit history
git log --oneline -3
```

### Workflow 2: Undo and Recovery

```bash
# Make changes with Aider
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
/add src/feature.py
> Implement new feature (but it has bugs)
/commit "Add new feature"

# Realize there's a problem - undo with Aider
/undo

# Or use Git to undo commits
git reset --soft HEAD~1  # Keep changes, undo commit
# or
git reset --hard HEAD~1  # Discard changes

# Fix the issue
> Fix the bugs in the feature implementation
/commit "Fix bugs in new feature"
```

### Workflow 3: Merge Conflict Resolution

```bash
# If you encounter merge conflicts:
git pull origin main  # This might create conflicts

# Start Aider to help resolve conflicts
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf conflicted_file.py

# Ask for help
> There are merge conflicts in this file. Please help me resolve them by keeping the best changes from both versions.

# Review resolved conflicts
/diff

# Commit the resolution
git add conflicted_file.py
git commit -m "Resolve merge conflicts in conflicted_file.py"
```

## 🔧 Git Configuration for Aider

### Optimizing Git Settings for Aider

```bash
# Configure Git to work better with Aider
git config --global core.editor "notepad"  # Simple editor for commit messages
git config --global merge.tool "vscode"    # If VS Code is available
git config --global diff.tool "vscode"

# Set up useful aliases
git config --global alias.tree "log --graph --oneline --decorate --all"
git config --global alias.st "status"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.ci "commit"
```

### Aider Git Configuration

In your `config/aider_config.yml`:

```yaml
git:
  auto_commits: false          # Manual control for better commit messages
  gitignore: true              # Respect .gitignore
  detect_repo: true            # Auto-detect git repositories
  show_diffs: true             # Show changes before committing
  commit_message_template: "AI: {description}\n\nGenerated with offline coding agent"
  push_after_commit: false     # Manual push control for restricted environments

  # Bitbucket-specific settings
  remote_origin_pattern: "bitbucket.org"
  web_workflow_compatible: true
```

## 🎯 Real-World Project Workflow

### Complete Example: Web Application Development

```bash
# 1. Initialize project
mkdir my-web-app
cd my-web-app
git init

# 2. Start Aider for initial structure
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# 3. Create project structure
> Create a Flask web application with the following structure:
> - app.py (main application)
> - requirements.txt (dependencies)
> - config.py (configuration)
> - templates/ (HTML templates)
> - static/ (CSS, JS)
> - tests/ (unit tests)

# 4. Implement basic functionality
/add app.py
> Create a basic Flask app with homepage and user registration

/add config.py
> Create configuration management for development and production

/add templates/index.html
> Create homepage template with user-friendly interface

# 5. Review and commit initial structure
/diff
/commit "Create initial Flask application structure"

# 6. Add database functionality
/add models.py
> Implement user model with SQLAlchemy

/add app.py
> Add database integration and user authentication routes

# 7. Create tests
/add tests/test_app.py
> Create comprehensive tests for the application

# 8. Commit database integration
/commit "Add database models and user authentication"

# 9. Add styling
/add static/style.css
> Create responsive CSS styling for the application

# 10. Final review and commit
/diff
/commit "Add responsive styling and complete user interface"

# 11. Prepare for deployment
/add Dockerfile
> Create Dockerfile for containerized deployment

/add docker-compose.yml
> Create docker-compose for development and production

# 12. Final commit
/commit "Add Docker configuration for deployment"

# 13. Create documentation
/add README.md
> Write comprehensive README with installation and usage instructions

/commit "Add project documentation"

# 14. Prepare for Bitbucket
git status
git log --oneline -10

# 15. Sync with Bitbucket (web interface or git push if available)
```

## 🚨 Troubleshooting Git Issues

### Issue 1: Git commands not working

```bash
# Check Git installation
git --version

# If Git is not found, use Git Bash or install Git for Windows
# In Git Bash, you can use all Git commands normally
```

### Issue 2: Permission issues with Git

```bash
# Check repository permissions
ls -la .git/

# Fix permissions (if possible)
git config --global core.sharedRepository group

# Or work in user directory
cd C:\Users\%USERNAME%\Documents\
```

### Issue 3: Merge conflicts

```bash
# Start Aider to help resolve conflicts
python -m aider --model models/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf conflicted_file.py

> Please help resolve the merge conflicts in this file by choosing the appropriate changes

# Review and commit resolution
/diff
git add conflicted_file.py
git commit -m "Resolve merge conflicts"
```

### Issue 4: Large files causing issues

```bash
# Check for large files
git ls-files | xargs ls -la

# Add large files to .gitignore
echo "*.large" >> .gitignore
echo "data/" >> .gitignore

# Remove already committed large files
git rm --cached large_file.dat
git commit -m "Remove large files from tracking"
```

## 📋 Git + Aider Quick Reference

### Essential Commands
```bash
# Aider commands
/diff                     # Show changes
/commit                   # Commit changes
/undo                     # Undo last change
/git                      # Show git status

# Git commands
git status                # Show repository status
git add .                 # Stage all changes
git commit -m "message"   # Commit with message
git log --oneline -5      # Show recent commits
git checkout -b branch    # Create new branch
git merge branch          # Merge branch
```

### Best Practices
1. **Commit frequently** with descriptive messages
2. **Review changes** before committing
3. **Use branches** for features and fixes
4. **Sync regularly** with Bitbucket (if possible)
5. **Write good commit messages** that explain what and why

### Workflow Template
```bash
1. git checkout -b feature-name
2. python -m aider --model models/...
3. /add relevant_files
4. > Make specific changes
5. /diff (review changes)
6. /commit (save work)
7. git add . && git commit (sync to Git)
8. Repeat steps 4-7 as needed
9. git checkout main && git merge feature-name
```

---

**These workflows ensure smooth integration between Aider and Git, even in restricted environments with limited connectivity.**