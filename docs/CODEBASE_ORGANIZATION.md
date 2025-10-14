# Codebase Organization

**Last Updated:** 2025-10-14  
**Status:** ✅ Cleaned and Reorganized

## Directory Structure

```
offline-coding-agent/
├── 📁 archive/              # Old assistant versions (historical reference)
│   ├── agentic_assistant.py
│   ├── simple_ai_assistant.py
│   ├── smart_assistant.py
│   └── README.md
│
├── 📁 config/               # Configuration files
│   ├── default.yaml         # Main configuration
│   └── aider_config.yml     # Aider integration config
│
├── 📁 docs/                 # Documentation
│   ├── 📁 github/          # GitHub-specific documentation
│   │   ├── GITHUB_ISSUES.md
│   │   ├── GITHUB_ISSUES_BATCH.md
│   │   ├── GITHUB_ORGANIZATION.md
│   │   ├── GITHUB_README.md
│   │   ├── GITHUB_REPO_SETUP.md
│   │   ├── REPOSITORY_SUMMARY.md
│   │   └── README.md
│   │
│   ├── COMPACT_SUMMARY.md               # Quick reference guide
│   ├── AUTONOMOUS_LOOP_FINAL_REPORT.md  # Production readiness report
│   ├── AUTONOMOUS_EXECUTION_*.md        # Implementation details
│   ├── agent_evaluation.md
│   ├── aider_setup_guide.md
│   ├── concept.md
│   ├── implementation_guide.md
│   ├── installation_guide.md
│   ├── model_comparison.md
│   ├── model_evaluation.md
│   ├── technical_architecture.md
│   └── troubleshooting_restricted_environments.md
│
├── 📁 examples/             # Example projects and workflows
│   └── terminal_workflows/
│
├── 📁 models/               # Downloaded AI models (gitignored)
│   └── Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
│
├── 📁 scripts/              # Utility scripts
│   ├── download_model.py    # Model download script
│   ├── install_aider.py     # Aider installation
│   └── verify_installation.py
│
├── 📁 src/                  # Source code (legacy CLI)
│   ├── model/
│   ├── utils/
│   ├── cli.py
│   └── __init__.py
│
├── 📁 temp/                 # Temporary files and scratch work
│   ├── my_python_project/
│   └── README.md
│
├── 📁 test_logs/            # Autonomous loop test documentation
│   ├── autonomous_test_session_*.md
│   └── autonomous_test_session_final_assessment.md
│
├── 📁 tests/                # Test files and results
│   ├── test_aider.py
│   ├── TEST_RESULTS.md
│   └── README.md
│
├── 📁 venv/                 # Python virtual environment (gitignored)
│
├── 📄 CLAUDE.md             # Instructions for Claude Code
├── 📄 LICENSE               # MIT License
├── 📄 README.md             # Main project README
├── 📄 requirements.txt      # Python dependencies
├── 📄 setup.py              # Package setup
├── 📄 start_assistant.sh    # Convenience script to launch assistant
└── 📄 working_assistant.py  # Main AI assistant (current version)
```

## Key Files

### Core Application
- **`working_assistant.py`** - Main AI coding assistant (executable)
- **`start_assistant.sh`** - Convenience launcher script
- **`requirements.txt`** - Python package dependencies
- **`config/default.yaml`** - Configuration settings

### Documentation
- **`README.md`** - Project overview and quick start
- **`CLAUDE.md`** - Instructions for Claude Code AI
- **`docs/`** - Comprehensive documentation
  - Technical architecture
  - Implementation guides
  - Model evaluation
  - Troubleshooting

### Development
- **`tests/`** - Test files and results
- **`scripts/`** - Utility scripts (model download, installation)
- **`src/`** - Legacy CLI source code (not currently used)

### Reference
- **`archive/`** - Old assistant implementations
- **`temp/`** - Temporary files and examples

## Reorganization Changes

### Files Moved

| Old Location | New Location | Reason |
|--------------|--------------|--------|
| `agentic_assistant.py` | `archive/` | Old version |
| `simple_ai_assistant.py` | `archive/` | Old version |
| `smart_assistant.py` | `archive/` | Old version |
| `test_aider.py` | `tests/` | Test file |
| `TEST_RESULTS.md` | `tests/` | Test results |
| `my_python_project/` | `temp/` | Temporary example |
| `GITHUB_*.md` | `docs/github/` | GitHub docs |
| `REPOSITORY_SUMMARY.md` | `docs/github/` | GitHub docs |
| `AUTONOMOUS_LOOP_FINAL_REPORT.md` | `docs/` | Generated documentation |
| `COMPACT_SUMMARY.md` | `docs/` | Generated documentation |

### New Folders Created

- **`archive/`** - Historical assistant versions
- **`tests/`** - Centralized testing
- **`test_logs/`** - Autonomous loop test documentation
- **`temp/`** - Temporary files
- **`docs/github/`** - GitHub-specific documentation

### Benefits

1. ✅ **Cleaner root directory** - Only essential files in root
2. ✅ **Better organization** - Related files grouped together
3. ✅ **Clear separation** - Production vs archive vs temp
4. ✅ **Easy navigation** - Logical folder structure
5. ✅ **Documented structure** - README in each major folder

## Quick Navigation

```bash
# Core application
./working_assistant.py --help
./start_assistant.sh

# Run tests
cd tests/
python test_aider.py

# Download model
python scripts/download_model.py

# View documentation
cd docs/
cat technical_architecture.md

# Check old implementations
cd archive/
ls -la
```

## Maintenance

- **Keep temp/ clean** - Remove unnecessary files regularly
- **Update tests/** - Add new test files as features are developed
- **Document changes** - Update README files when structure changes
- **Archive old code** - Move deprecated code to archive/ with README
