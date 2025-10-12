# Model Evaluation for Offline Coding Agent

## Hardware Constraints
- **Target Environment**: Windows business laptops
- **RAM**: 32GB (sufficient for most models)
- **VRAM**: 128MB integrated (CPU-only inference required)
- **Storage**: Need reasonable download sizes
- **Network**: Offline operation (one-time download)

## Model Candidates Analysis

### Tier 1: Recommended (Best Balance)

#### 1. Qwen2.5-Coder-8B ⭐ **TOP RECOMMENDED**
- **Size**: ~4.7GB (Q4_K_M), ~5.8GB (Q5_K_M)
- **Pros**: Specifically trained for code, excellent performance, 32K context window, great for complex projects
- **Cons**: Higher resource usage than smaller models
- **Memory Usage**: ~8-10GB RAM
- **Performance**: 15-30 tokens/second on modern CPUs
- **Best For**: Professional code generation and complex projects

#### 2. DeepSeek-Coder-1.3B
- **Size**: ~2.6GB (base), ~1.3GB (4-bit quantized)
- **Pros**: Very lightweight, specifically trained for code, fast responses
- **Cons**: Smaller context window, limited for complex tasks
- **Memory Usage**: ~4GB RAM
- **Performance**: 40-60 tokens/second
- **Best For**: Quick responses, minimal resource usage

#### 3. Qwen3-8B (General Purpose)
- **Size**: ~4.9GB (Q4_K_M), ~6.2GB (Q5_K_M)
- **Pros**: Latest 2025 architecture, large 32K+ context, enhanced reasoning, multi-language support
- **Cons**: Not coding-specific, higher resource usage, slower than specialized models
- **Memory Usage**: ~6-8GB RAM
- **Performance**: 5-15 tokens/second
- **Best For**: Mixed coding + general reasoning tasks

#### 4. Phi-3-mini (3.8B)
- **Size**: ~7.5GB (base), ~4GB (4-bit quantized)
- **Pros**: Microsoft support, excellent reasoning, good performance
- **Cons**: Not specifically code-trained, older architecture
- **Memory Usage**: ~8GB RAM
- **Performance**: 20-30 tokens/second
- **Best For**: Balanced performance with reasonable resource usage

### Tier 2: Alternative Options

#### 4. DeepSeek-Coder-6.7B
- **Size**: ~13GB (base), ~7GB (4-bit quantized)
- **Pros**: Superior code generation, larger context
- **Cons**: Heavier resource usage
- **Memory Usage**: ~15GB RAM
- **Best For**: Maximum performance when resources allow

#### 5. StarCoderBase-3B
- **Size**: ~6GB (base), ~3GB (4-bit quantized)
- **Pros**: Specifically trained for code, good performance
- **Cons**: Older model, less efficient than newer alternatives
- **Memory Usage**: ~10GB RAM
- **Best For**: Reliable code generation with moderate resources

## Quantization Strategy

### Recommended Quantization Levels
- **4-bit (GGUF/Q4_K_M)**: Best balance of quality and size
- **8-bit**: Better quality, moderate size reduction
- **FP16**: Highest quality, largest size (use with caution)

### Implementation Options
1. **llama.cpp**: Excellent CPU performance, wide model support
2. **transformers + bitsandbytes**: Good integration, Python-native
3. **ollama**: Easy setup, good CPU support

## Deployment Recommendations

### Primary Recommendation: Qwen2.5-Coder-8B (Q4_K_M) ⭐ **BEST CHOICE**
- **File Size**: ~4.7GB
- **RAM Usage**: ~8GB
- **Performance**: Excellent professional-grade code generation
- **Context Window**: 32K tokens (supports large files and projects)
- **Setup**: Excellent with llama.cpp
- **Best For**: Professional development and complex projects

### Secondary Choice: DeepSeek-Coder-1.3B (4-bit)
- **File Size**: ~1.3GB
- **RAM Usage**: ~4GB
- **Performance**: Fast code completion and generation
- **Context Window**: 16K tokens
- **Setup**: Simple with llama.cpp
- **Best For**: Quick responses and resource-constrained environments

### Alternative: Qwen3-8B (Q4_K_M) - General Purpose
- **File Size**: ~4.9GB
- **RAM Usage**: ~6GB
- **Performance**: Good for coding + general reasoning
- **Context Window**: 32K+ tokens (expandable to 131K)
- **Setup**: Good with llama.cpp
- **Best For**: Mixed coding and general AI tasks

## Next Steps
1. Download and test recommended models
2. Benchmark performance on target hardware
3. Evaluate code generation quality
4. Make final selection based on testing results