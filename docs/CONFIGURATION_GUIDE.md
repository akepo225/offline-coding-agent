# Configuration Guide

## Overview

The Offline Coding Agent supports hardware-specific configurations to optimize performance based on your machine's capabilities. All configuration parameters are read from YAML files in the `config/` directory.

## Quick Start

### Using Pre-configured Profiles

**Default (Balanced)**
```bash
./start_assistant.sh
# Or explicitly:
./start_assistant.sh --config config/default.yaml
```

**High Performance (32GB+ RAM)**
```bash
./start_assistant.sh --config config/high_performance.yaml
```

**Low-End (8GB RAM)**
```bash
./start_assistant.sh --config config/low_end.yaml
```

## Configuration Profiles

### Default Configuration
**Hardware:** 16GB RAM, Mid-range CPU
**Use Case:** General coding tasks, balanced performance

```yaml
inference:
  n_ctx: 4096           # Context window
  n_batch: 512          # Batch size
  max_tokens: 1024      # Max response length
  temperature: 0.3      # Deterministic for code
  top_p: 0.9
  repeat_penalty: 1.1
```

**Performance Characteristics:**
- Response time: ~5-10 seconds
- Context capacity: ~3000 words
- Memory usage: ~8GB
- Tool chaining: 5-7 tools per session

### High Performance Configuration
**Hardware:** 32GB+ RAM, Modern multi-core CPU
**Use Case:** Complex projects, large codebases, multi-step tasks

```yaml
inference:
  n_ctx: 8192           # 2x context
  n_batch: 1024         # 2x batch size
  max_tokens: 2048      # 2x response length
  temperature: 0.4      # Slightly more creative
  top_p: 0.9
  repeat_penalty: 1.1
```

**Performance Characteristics:**
- Response time: ~8-15 seconds
- Context capacity: ~6000 words
- Memory usage: ~12-16GB
- Tool chaining: 7-10 tools per session
- Best for: Architecture analysis, refactoring, documentation

### Low-End Configuration
**Hardware:** 8GB RAM, Older or slower CPUs
**Use Case:** Quick tasks, simple operations, resource-constrained environments

```yaml
inference:
  n_ctx: 2048           # ½ context
  n_batch: 256          # ½ batch size
  max_tokens: 512       # ½ response length
  temperature: 0.2      # Very deterministic
  top_p: 0.9
  repeat_penalty: 1.1
```

**Performance Characteristics:**
- Response time: ~3-5 seconds
- Context capacity: ~1500 words
- Memory usage: ~4-6GB
- Tool chaining: 3-5 tools per session
- Best for: File operations, simple scripts, quick edits

## Configuration Parameters Reference

### Inference Parameters

#### `n_ctx` - Context Window Size
**Range:** 512 - 32768 tokens
**Impact:** Memory usage, context capacity

- **Low (2048):** 8GB RAM, ~1500 words of context
- **Mid (4096):** 16GB RAM, ~3000 words of context
- **High (8192):** 32GB RAM, ~6000 words of context
- **Ultra (16384):** 64GB+ RAM, ~12000 words of context

**When to increase:**
- Working with large files
- Complex multi-file projects
- Need more conversation history

**When to decrease:**
- Limited RAM
- Simple single-file tasks
- Need faster responses

#### `n_batch` - Batch Processing Size
**Range:** 128 - 2048
**Impact:** Processing speed, RAM usage

- **Low (256):** Slower but uses less RAM
- **Mid (512):** Balanced
- **High (1024):** Faster but uses more RAM

**When to increase:**
- Have plenty of RAM
- Want faster prompt processing
- Working with long prompts

#### `max_tokens` - Maximum Response Length
**Range:** 128 - 4096 tokens
**Impact:** Generation time, response completeness

- **Fast (512):** Quick responses, may be incomplete
- **Balanced (1024):** Good for most tasks
- **Quality (2048):** Comprehensive responses
- **Ultra (4096):** Very detailed, slow

**When to increase:**
- Need longer code generation
- Want detailed explanations
- Complex multi-step tasks

**When to decrease:**
- Want faster responses
- Simple yes/no or short answers
- Limited time budget

#### `temperature` - Randomness Control
**Range:** 0.0 - 2.0
**Impact:** Creativity vs determinism

- **Code (0.2-0.3):** Deterministic, repeatable
- **Balanced (0.5-0.7):** Mix of creativity and consistency
- **Creative (0.8-1.0):** More varied solutions

**For coding tasks:** Keep low (0.2-0.4)
**For brainstorming:** Increase to 0.6-0.8

#### `top_p` - Nucleus Sampling
**Range:** 0.0 - 1.0
**Impact:** Response diversity

- **Focused (0.8):** More predictable
- **Balanced (0.9):** Good mix
- **Diverse (0.95-1.0):** More variety

#### `repeat_penalty` - Repetition Prevention
**Range:** 1.0 - 2.0
**Impact:** Prevents repetitive text

- **None (1.0):** No penalty
- **Light (1.1):** Recommended default
- **Strong (1.3-1.5):** Use if seeing repetition

## Creating Custom Configurations

### Step 1: Copy a Template

```bash
cp config/default.yaml config/my_config.yaml
```

### Step 2: Edit Parameters

```yaml
# My Custom Configuration
model:
  name: "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"
  path: "./models"

inference:
  n_ctx: 6144        # Custom: Between mid and high
  n_threads: 8       # Set to your CPU core count
  n_batch: 768       # Custom: Between mid and high
  max_tokens: 1536   # Custom value
  temperature: 0.35  # Slightly more creative than default
  top_p: 0.9
  repeat_penalty: 1.1
  verbose: false
```

### Step 3: Use Your Configuration

```bash
./start_assistant.sh --config config/my_config.yaml
```

## Hardware-Specific Recommendations

### 8GB RAM Laptop
```yaml
inference:
  n_ctx: 2048
  n_batch: 256
  max_tokens: 512
```
**Expected:** ~4GB model + ~4GB inference = Safe

### 16GB RAM Desktop
```yaml
inference:
  n_ctx: 4096
  n_batch: 512
  max_tokens: 1024
```
**Expected:** ~4GB model + ~8GB inference = Comfortable

### 32GB RAM Workstation
```yaml
inference:
  n_ctx: 8192
  n_batch: 1024
  max_tokens: 2048
```
**Expected:** ~4GB model + ~12GB inference = Plenty of headroom

### 64GB+ RAM Server
```yaml
inference:
  n_ctx: 16384
  n_batch: 2048
  max_tokens: 4096
```
**Expected:** ~4GB model + ~20GB inference = Maximum performance

## Performance Tuning Tips

### Faster Responses
1. Reduce `max_tokens` to 512-768
2. Lower `temperature` to 0.2
3. Reduce `n_ctx` if not needed
4. Use `--auto-confirm` to skip prompts

### Better Quality
1. Increase `max_tokens` to 2048+
2. Increase `n_ctx` for more context
3. Slightly increase `temperature` (0.3-0.4)
4. Add more files to context with `/add`

### Memory Optimization
1. Reduce `n_ctx` (biggest impact)
2. Reduce `n_batch`
3. Set `performance.model_keep_alive: false`
4. Limit `max_tokens`

## Troubleshooting

### "Out of Memory" Error
**Solution:** Reduce `n_ctx` and `n_batch`
```yaml
inference:
  n_ctx: 2048      # Reduce by half
  n_batch: 256     # Reduce by half
```

### Responses Too Short
**Solution:** Increase `max_tokens`
```yaml
inference:
  max_tokens: 2048  # Double it
```

### Responses Too Slow
**Solution:** Reduce `max_tokens` and `n_ctx`
```yaml
inference:
  n_ctx: 2048
  max_tokens: 512
```

### Model Not Using Context
**Solution:** Increase `n_ctx` and verify files are added
```bash
# In interactive mode:
/add file1.py
/add file2.py
/list  # Verify files are in context
```

### Repetitive Responses
**Solution:** Increase `repeat_penalty`
```yaml
inference:
  repeat_penalty: 1.3  # Stronger penalty
```

## Examples

### Quick File Operations (Low-End Config)
```bash
./start_assistant.sh --config config/low_end.yaml --auto-confirm
> Read config.py and write a summary to summary.md
```
**Fast:** ~3-5 seconds per iteration

### Complex Refactoring (High Performance Config)
```bash
./start_assistant.sh --config config/high_performance.yaml
/add old_module.py
/add new_requirements.md
> Refactor old_module.py to match new requirements
```
**Thorough:** ~8-15 seconds per iteration, comprehensive analysis

### Balanced Development (Default Config)
```bash
./start_assistant.sh
> Create a Python class for user authentication with tests
```
**Optimal:** ~5-10 seconds per iteration, good quality

## Configuration File Locations

- `config/default.yaml` - Balanced (ships with project)
- `config/high_performance.yaml` - For powerful machines
- `config/low_end.yaml` - For resource-constrained systems
- `config/*.yaml` - Add your own custom configs

## See Also

- [README.md](../README.md) - General usage guide
- [CLAUDE.md](../CLAUDE.md) - Development instructions
- [COMPACT_SUMMARY.md](COMPACT_SUMMARY.md) - Quick reference
- [working_assistant.py](../working_assistant.py) - Implementation details
