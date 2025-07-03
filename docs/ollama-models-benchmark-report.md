# Ollama Models Benchmark Report
**Generated: July 3, 2025**  
**Test Date: 2025-07-03 11:21:32**

## Executive Summary

Comprehensive benchmark testing of 7 AI models (6 Ollama + 1 Gemini) for shopping item categorization in both English and Czech languages. Tests included 16 items per model (8 English, 8 Czech) measuring both accuracy and response time.

## 🏆 Key Findings

### **Best Overall Performance**
- **🎯 Highest Accuracy**: `deepseek-r1:latest` & `qwen3:latest` (87.5% each)
- **⚡ Fastest Response**: `gemini-1.5-flash` (0.246s average)
- **⚖️ Best Balance**: `gemini-1.5-flash` (speed vs accuracy trade-off)

### **Language-Specific Performance**
- **🇺🇸 English**: Most models achieved 87.5% accuracy (except gemma3n:latest)
- **🇨🇿 Czech**: Significant variation (12.5% to 87.5%), highlighting multilingual challenges

## 📊 Detailed Results

| Model | Overall Accuracy | English Accuracy | Czech Accuracy | Avg Response Time |
|-------|------------------|------------------|----------------|-------------------|
| **deepseek-r1:latest** | **87.5%** | 87.5% | **87.5%** | 30.190s |
| **qwen3:latest** | **87.5%** | 87.5% | **87.5%** | 62.981s |
| gemma3:4b | 75.0% | 87.5% | 62.5% | **1.940s** |
| gemma3:latest | 75.0% | 87.5% | 62.5% | **1.954s** |
| llama4:latest | 75.0% | 75.0% | 75.0% | 11.060s |
| gemma3n:latest | 56.2% | 62.5% | 50.0% | 3.642s |
| **gemini-1.5-flash** | 50.0% | 87.5% | 12.5% | **0.246s** |

## 🔍 Key Insights

### **Accuracy Analysis**
1. **Top Performers**: DeepSeek R1 and Qwen3 excel in both languages (87.5% each)
2. **Czech Language Challenge**: Gemini performs poorly in Czech (12.5% vs 87.5% English)
3. **Consistent Performance**: Gemma3 variants show similar accuracy patterns
4. **Language Balance**: LLaMA4 shows most balanced cross-language performance (75% both)

### **Performance Analysis**
1. **Speed Champion**: Gemini is 8x faster than nearest Ollama competitor
2. **Ollama Performance Tiers**:
   - **Fast**: Gemma3 variants (~2s)
   - **Medium**: Gemma3n (~4s), LLaMA4 (~11s)
   - **Slow**: DeepSeek (~30s), Qwen3 (~63s)

### **Error Patterns**
1. **Common Mistakes**:
   - Ice cream categorization (Dairy vs Dessert/Frozen)
   - Bread categorization (Bakery vs Pantry)
   - Czech translation challenges
2. **DeepSeek Issue**: Produces verbose reasoning text instead of single category
3. **Qwen3 Issue**: Similar verbose output with internal reasoning

## 🔄 Fallback Strategy Recommendations

### **Production Configuration**
```yaml
Primary Provider: gemini-1.5-flash
- Pros: Fastest response (0.246s), Good English accuracy (87.5%)
- Cons: Poor Czech performance (12.5%)

Fallback Provider: gemma3:4b
- Pros: Good overall accuracy (75%), Balanced languages, Fast (1.94s)
- Cons: Slower than Gemini, Some Czech accuracy issues
```

### **Alternative High-Accuracy Configuration**
```yaml
Primary Provider: deepseek-r1:latest
- Pros: Best accuracy (87.5%), Excellent Czech support
- Cons: Very slow (30s), Verbose output needs cleaning

Fallback Provider: gemma3:4b
- Pros: Fast fallback, Good accuracy
- Cons: Lower accuracy than primary
```

## 🎯 Recommendations by Use Case

### **For Production (Speed Priority)**
- **Primary**: `gemini-1.5-flash` - Fast API responses, good English accuracy
- **Fallback**: `gemma3:4b` - Reliable local processing

### **For Accuracy (Quality Priority)**
- **Primary**: `deepseek-r1:latest` - Best overall accuracy
- **Fallback**: `qwen3:latest` - Similar accuracy, backup option

### **For Multilingual Applications**
- **Primary**: `deepseek-r1:latest` - Excellent Czech support (87.5%)
- **Fallback**: `llama4:latest` - Balanced language performance

### **For Development/Testing**
- **Primary**: `gemma3:4b` - Good balance of speed and accuracy
- **Fallback**: `gemma3:latest` - Nearly identical alternative

## ⚠️ Important Notes

1. **DeepSeek & Qwen3 Output Issue**: These models include verbose reasoning text that needs post-processing to extract the category name
2. **Czech Language Support**: Only DeepSeek R1, Qwen3, and LLaMA4 show strong Czech categorization capabilities
3. **Response Time Impact**: Consider user experience implications of 30-60s response times for high-accuracy models
4. **Resource Requirements**: Larger models require more system resources and may impact concurrent operations

## 📈 Implementation Priorities

1. **Immediate**: Implement `gemma3:4b` as primary Ollama fallback provider
2. **Short-term**: Add output cleaning for DeepSeek/Qwen3 to enable high-accuracy mode
3. **Long-term**: Consider Czech-specific prompt engineering for Gemini to improve multilingual performance

---
*This benchmark provides data-driven insights for optimizing AI provider selection in the FamilyCart application's categorization system.*
