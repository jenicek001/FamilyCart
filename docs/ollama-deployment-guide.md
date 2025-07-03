# Ollama Integration Deployment Guide

## Overview
This guide explains how to deploy FamilyCart with Ollama support as an alternative to Google Gemini for AI-powered features (item categorization, translation, icon suggestion).

## Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM (16GB recommended for larger models)
- For GPU acceleration: NVIDIA GPU with Container Toolkit installed

## Configuration Options

### Option 1: Use Google Gemini (Default)
No additional setup required. Set in `backend/.env`:
```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash
```

### Option 2: Use Ollama with Docker Compose (Recommended)

1. **Enable Ollama service** in `docker-compose.yml`:
   ```yaml
   # Uncomment the entire ollama service section
   ollama:
     image: ollama/ollama:latest
     container_name: familycart-ollama
     ports:
       - "11434:11434"
     volumes:
       - ollama_data:/root/.ollama
     # ... rest of configuration
   ```

2. **Update backend environment** in `backend/.env`:
   ```bash
   AI_PROVIDER=ollama
   OLLAMA_BASE_URL=http://ollama:11434
   OLLAMA_MODEL_NAME=llama3.2
   OLLAMA_TIMEOUT=120
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Pull the model** (one-time setup):
   ```bash
   # Connect to Ollama container and pull model
   docker exec -it familycart-ollama ollama pull llama3.2
   
   # Alternative: pull from host if Ollama port is exposed
   curl -X POST http://localhost:11434/api/pull -d '{"model":"llama3.2"}'
   ```

### Option 3: Use External Ollama Server

If you have Ollama running on another machine:

1. **Configure backend** in `backend/.env`:
   ```bash
   AI_PROVIDER=ollama
   OLLAMA_BASE_URL=http://your-ollama-server:11434
   OLLAMA_MODEL_NAME=llama3.2
   OLLAMA_TIMEOUT=120
   ```

2. **Ensure model is available** on the remote server:
   ```bash
   # On the Ollama server
   ollama pull llama3.2
   ```

## Recommended Models

### For Development/Testing
- **llama3.2** (1B/3B): Fast, lightweight, good for basic tasks
- **qwen2.5:1.5b**: Very fast, excellent multilingual support

### For Production
- **llama3.2:3b**: Good balance of speed and quality
- **qwen2.5:3b**: Better multilingual support for international users
- **mistral:7b**: High quality, slower but more accurate

### For High-Performance Deployments
- **llama3.1:8b**: Excellent quality, requires more resources
- **mixtral:8x7b**: High quality, requires significant resources

## Model Installation Commands

```bash
# Lightweight models (good for testing)
docker exec -it familycart-ollama ollama pull llama3.2:1b
docker exec -it familycart-ollama ollama pull qwen2.5:1.5b

# Recommended production models
docker exec -it familycart-ollama ollama pull llama3.2:3b
docker exec -it familycart-ollama ollama pull qwen2.5:3b

# High-quality models (requires more resources)
docker exec -it familycart-ollama ollama pull llama3.1:8b
docker exec -it familycart-ollama ollama pull mistral:7b
```

## GPU Acceleration (NVIDIA)

### Prerequisites
1. Install NVIDIA Container Toolkit:
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

### Enable GPU in Docker Compose
Uncomment the GPU configuration in `docker-compose.yml`:
```yaml
ollama:
  # ... other configuration
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

## Environment Variables Reference

### Backend Configuration
```bash
# AI Provider Selection
AI_PROVIDER=ollama                    # Options: "gemini", "ollama"

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server URL
OLLAMA_MODEL_NAME=llama3.2            # Model name to use
OLLAMA_TIMEOUT=120                    # Request timeout in seconds

# Gemini Configuration (still supported)
GOOGLE_API_KEY=your_key_here          # Google Gemini API key
GEMINI_MODEL_NAME=gemini-1.5-flash    # Gemini model name
```

## Testing the Integration

### 1. Check AI Provider Status
```bash
curl http://localhost:8000/api/v1/ai/status
```

Expected response:
```json
{
  "provider_name": "ollama",
  "model_name": "llama3.2",
  "status": "active"
}
```

### 2. Test Item Categorization
```bash
curl -X POST http://localhost:8000/api/v1/ai/categorize-item \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{"item_name": "milk"}'
```

### 3. Test Icon Suggestion
```bash
curl -X POST http://localhost:8000/api/v1/ai/suggest-icon \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{"item_name": "milk", "category_name": "Dairy"}'
```

## Performance Comparison

| Provider | Model | Speed | Quality | Resource Usage | Cost |
|----------|-------|--------|---------|----------------|------|
| Gemini | gemini-1.5-flash | Very Fast | High | None (API) | Per request |
| Ollama | llama3.2:1b | Fast | Good | Low (1-2GB RAM) | Free |
| Ollama | llama3.2:3b | Medium | High | Medium (3-4GB RAM) | Free |
| Ollama | llama3.1:8b | Slow | Very High | High (8-12GB RAM) | Free |

## Troubleshooting

### Common Issues

1. **"Model not found" error**
   ```bash
   # Pull the model
   docker exec -it familycart-ollama ollama pull llama3.2
   ```

2. **Connection refused to Ollama**
   ```bash
   # Check if Ollama container is running
   docker ps | grep ollama
   
   # Check Ollama logs
   docker logs familycart-ollama
   ```

3. **Out of memory errors**
   - Use a smaller model (e.g., llama3.2:1b)
   - Increase Docker memory limits
   - Enable GPU acceleration if available

4. **Slow response times**
   - Use GPU acceleration
   - Switch to a smaller model
   - Increase `OLLAMA_TIMEOUT` value

### Health Checks

```bash
# Check if Ollama is responding
curl http://localhost:11434/api/tags

# Check available models
curl http://localhost:11434/api/tags | jq '.models[].name'

# Test model directly
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.2","prompt":"Hello world","stream":false}'
```

## Production Recommendations

1. **Use a dedicated Ollama server** for better resource management
2. **Enable GPU acceleration** for better performance
3. **Use model quantization** (Q4_K_M) for memory efficiency
4. **Implement monitoring** for model performance and availability
5. **Set up model preloading** to reduce first-request latency
6. **Configure appropriate timeouts** based on your model size

## Migration from Gemini to Ollama

1. **Backup your current configuration**
2. **Install and test Ollama** with a small model first
3. **Update environment variables** to use Ollama
4. **Test all AI endpoints** thoroughly
5. **Monitor performance** and adjust model/configuration as needed
6. **Keep Gemini configuration** as fallback option

## Security Considerations

- **Network isolation**: Run Ollama in a private network if possible
- **Resource limits**: Set memory and CPU limits to prevent resource exhaustion  
- **Model validation**: Only use trusted, well-known models
- **Access control**: Secure Ollama endpoints if exposed externally

---

**Last Updated**: January 2025  
**Tested with**: Ollama v0.5.1, Docker Compose v2.21+
