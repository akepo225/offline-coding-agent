# Basic Aider Usage Examples

> Essential terminal workflows for getting started with Aider in restricted Windows environments.

## 🚀 Getting Started

### Starting Aider

```bash
# Navigate to your project directory
cd C:\Users\YourName\Documents\my-project

# Start Aider with local model
python -m aider --model ..\offline-coding-agent\models\qwen2.5-coder-8b-instruct.Q4_K_M.gguf
```

### First Session Workflow

```bash
# 1. Start Aider
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf

# 2. Create your first file
/create new_script.py

# 3. Ask Aider to generate code
> Write a simple Python script that prints "Hello, World!" and includes basic error handling

# 4. Review the generated code
# (Aider will show you the file with changes)

# 5. Save and commit the changes
/commit "Add initial Hello World script with error handling"

# 6. Exit Aider
/quit
```

## 📝 Common Workflows

### Workflow 1: Creating a New Python Function

```bash
# Start Aider with your target file
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf my_script.py

# Add the file to context (if not automatically added)
/add my_script.py

# Request function creation
> Create a Python function called validate_email that takes an email string as input and returns True if it's a valid email format, False otherwise. Use regex pattern matching.

# Aider will show you the changes - press 'y' to accept

# Test the function
> Add some test cases to verify the validate_email function works correctly

# Review and commit
/diff
/commit "Add email validation function with test cases"
```

### Workflow 2: Debugging Existing Code

```bash
# Start Aider with problematic file
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf buggy_script.py

# Describe the problem
> This script is throwing a TypeError when I run it. The error says "unsupported operand type(s) for +: 'int' and 'str'" on line 15. Can you help me fix it?

# Aider will analyze and fix the issue

# Review the fix
> Explain what was causing the error and how you fixed it

# Test the solution
> Add some input validation to prevent similar errors in the future

# Commit the fix
/commit "Fix TypeError in buggy_script.py and add input validation"
```

### Workflow 3: Refactoring Code

```bash
# Start Aider with file to refactor
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf old_code.py

# Request refactoring
> Refactor this code to use modern Python features, improve readability, and follow PEP 8 style guidelines. Also add type hints.

# Review the changes
/diff

# Ask for specific improvements
> Can you improve the performance of the data processing loop by using list comprehensions?

# Final review
> Add comprehensive docstrings to all functions

# Commit refactored code
/commit "Refactor old_code.py with modern Python features and type hints"
```

### Workflow 4: Working with Multiple Files

```bash
# Start Aider in project directory
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf

# Add multiple files to context
/add main.py
/add utils.py
/add config.py

# Make cross-file changes
> Create a new function in utils.py called load_config that loads configuration from a JSON file. Then update main.py to use this function instead of hardcoded values.

# Review changes across all files
/diff

# Commit changes
/commit "Extract configuration loading to utils.py and update main.py"
```

## 🔧 File Management Commands

### Adding and Removing Files

```bash
# Add specific file
/add script.py

# Add multiple files
/add *.py

# Add entire directory
/add src/

# Remove file from context
/remove script.py

# List all files in context
/ls

# Clear all context
/clear
```

### File Operations

```bash
# Create new file
/create new_file.py

# Read file content
/read existing_file.py

# Show diff of changes
/diff

# Undo last change
/undo

# Git status
/git
```

## 🎯 Specific Task Examples

### Example 1: Building a REST API

```bash
# Start Aider
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf

# Create API structure
> Create a Flask REST API with the following endpoints:
> - GET /api/users - List all users
> - GET /api/users/<id> - Get specific user
> - POST /api/users - Create new user
> - PUT /api/users/<id> - Update user
> - DELETE /api/users/<id> - Delete user
>
> Include proper error handling, input validation, and JSON responses.

# Aider will create multiple files (app.py, models.py, etc.)

# Add requirements
/create requirements.txt
> Add Flask and related dependencies to requirements.txt

# Create example usage
/create example_client.py
> Write a Python script that demonstrates how to use this API

# Review and commit
/diff
/commit "Create complete Flask REST API with CRUD operations"
```

### Example 2: Data Analysis Script

```bash
# Start Aider with data file
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf data.csv

# Create analysis script
> Create a Python script that analyzes the data in data.csv. The script should:
> 1. Load the CSV data using pandas
> 2. Perform basic statistical analysis
> 3. Create visualizations using matplotlib
> 4. Export results to a new CSV file
> 5. Include proper error handling for missing or invalid data

# Review generated analysis
> Add comments explaining each step of the analysis

# Test with sample data
> Create a small test dataset to verify the script works correctly

# Finalize
/commit "Add data analysis script with visualization and error handling"
```

### Example 3: Web Scraping Tool

```bash
# Start Aider
python -m aider --model models/qwen2.5-coder-8b-instruct.Q4_K_M.gguf

# Create web scraper
> Create a web scraping tool that:
> 1. Takes a URL as input
> 2. Extracts all links from the page
> 3. Follows links to a depth of 2 levels
> 4. Saves results to a JSON file
> 5. Includes rate limiting and error handling
> 6. Uses requests and BeautifulSoup libraries

# Add configuration file
/create config.json
> Create a configuration file that allows users to set:
> - Maximum depth to crawl
> - Delay between requests
> - File output location
> - URL patterns to ignore

# Create requirements
/create requirements.txt
> Add required packages for web scraping

# Create usage example
/create example_usage.py
> Show how to use the web scraper with different configurations

# Commit complete solution
/commit "Create comprehensive web scraping tool with configuration"
```

## 🔍 Advanced Aider Features

### Using System Prompts

```bash
# Set context for Aider
> You are an expert Python developer specializing in data science and machine learning. Focus on writing clean, efficient, and well-documented code.

> Now create a machine learning pipeline that loads data, preprocesses it, trains a model, and evaluates performance.
```

### Iterative Development

```bash
# Step 1: Create basic structure
> Create a basic class structure for a data processing pipeline

# Step 2: Add methods
> Add a method to load data from CSV files with error handling

# Step 3: Implement functionality
> Implement the data loading method with pandas

# Step 4: Add validation
> Add input validation to ensure data quality

# Step 5: Add logging
> Add logging to track processing steps and errors

# Review entire implementation
/diff
/commit "Implement complete data processing pipeline with validation and logging"
```

### Code Review Mode

```bash
# Ask for code review
> Please review the current code and suggest improvements for:
> 1. Performance optimization
> 2. Security best practices
> 3. Code readability
> 4. Error handling
> 5. Documentation

# Apply suggestions selectively
> Implement the performance optimizations you suggested, but keep the current structure for now.
```

## 🚨 Common Pitfalls and Solutions

### Pitfall 1: Too Much Context

```bash
# ❌ Bad: Adding too many files at once
/add *.py                    # 50+ files
> This might overwhelm the model

# ✅ Good: Selective file addition
/add main.py utils.py config.py
> Focus on relevant files only
```

### Pitfall 2: Vague Requests

```bash
# ❌ Bad: Vague request
> Make this better

# ✅ Good: Specific request
> Refactor this function to use list comprehensions and add type hints for better performance and readability
```

### Pitfall 3: No Code Review

```bash
# ❌ Bad: Accepting changes without review
# (Always press 'y' immediately)

# ✅ Good: Review before accepting
# (Read the changes, then press 'y' if satisfied)
```

### Pitfall 4: Forgetting to Commit

```bash
# ❌ Bad: Making many changes without committing
# (Losing work if something goes wrong)

# ✅ Good: Commit frequently
/commit "Add user authentication"
/commit "Fix validation bugs"
/commit "Add database connection"
```

## 📋 Quick Reference

### Essential Commands
```bash
/add file.py              # Add file to context
/remove file.py           # Remove file from context
/diff                     # Show changes
/commit                   # Commit changes
/undo                     # Undo last change
/help                     # Show all commands
/quit                     # Exit aider
```

### Best Practices
1. **Start small** - Add files gradually
2. **Be specific** - Use clear, detailed requests
3. **Review changes** - Always check before accepting
4. **Commit frequently** - Save work often
5. **Use /diff** - Review all changes before committing

### Example Session Flow
```bash
1. python -m aider --model models/...
2. /add relevant_file.py
3. > Specific request for changes
4. [Review changes]
5. /commit "Descriptive commit message"
6. /quit
```

---

**Practice these workflows to become proficient with Aider in your terminal environment!**