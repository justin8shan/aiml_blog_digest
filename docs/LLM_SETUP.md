# LLM Categorization Setup Guide

## Overview

The blog digest uses **LLM-based categorization** via **OpenRouter** or **GitHub Models** for more accurate article grouping. This guide explains the setup and usage.

## Benefits of LLM Categorization

✅ **Much more accurate** than keyword matching  
✅ **Context-aware** - understands article meaning, not just keywords  
✅ **Handles ambiguity** - can categorize articles that span multiple topics  
✅ **Cost-effective** - ~$0.01-0.02 per week with OpenRouter  
✅ **Free option** - GitHub Models offers free tier  
✅ **Automatic fallback** - uses keywords if LLM unavailable  
✅ **Multiple providers** - Choose between OpenRouter or GitHub

## Provider Comparison

| Feature | OpenRouter | GitHub Models |
|---------|-----------|---------------|
| **Cost** | ~$0.01-0.02/week | Free tier available |
| **Models** | 100+ models | 10+ popular models |
| **Setup** | API key from OpenRouter | GitHub token |
| **Quality** | Excellent | Excellent |
| **Best for** | Production, variety | Free tier, GitHub users |

## Setup Instructions

### Option A: OpenRouter (Recommended)

#### 1. Get OpenRouter API Key

1. Go to https://openrouter.ai/keys
2. Sign up or log in (can use Google/GitHub)
3. Click "Create Key"
4. Name it (e.g., "Blog Digest")
5. Copy the key (starts with `sk-or-v1-...`)
6. **Important**: Add credits or connect payment method

#### 2. Set Environment Variable

**macOS/Linux:**
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
```

**Add to your shell profile** (~/.zshrc or ~/.bash_profile):
```bash
echo 'export OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### 3. Configure Provider

Edit `config/llm_categories.yaml`:
```yaml
llm:
  provider: "openrouter"
  model: "openai/gpt-4o-mini"
```

#### 4. Add to GitHub Secrets

For automated runs via GitHub Actions:

1. Go to your repo: https://github.com/justin8shan/aiml_blog_digest
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `OPENROUTER_API_KEY`
5. Value: Your API key
6. Click **Add secret**

---

### Option B: GitHub Models (Free Tier)

#### 1. Get GitHub Token

**Method 1: Personal Access Token**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: "Blog Digest LLM"
4. Select scopes: `repo`, `read:org`
5. Click "Generate token"
6. Copy the token (starts with `ghp_...`)

**Method 2: GitHub Models Portal**
1. Go to https://github.com/marketplace/models
2. Browse available models
3. Follow instructions to get access token

#### 2. Set Environment Variable

**macOS/Linux:**
```bash
export GITHUB_TOKEN="ghp_your-token-here"
```

**Add to your shell profile:**
```bash
echo 'export GITHUB_TOKEN="ghp_your-token-here"' >> ~/.zshrc
source ~/.zshrc
```

#### 3. Configure Provider

Edit `config/llm_categories.yaml`:
```yaml
llm:
  provider: "github"
  model: "gpt-4o-mini"
```

#### 4. Add to GitHub Secrets

1. Go to your repo settings
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GH_MODELS_TOKEN`
5. Value: Your GitHub token
6. Click **Add secret**

### 4. Install OpenAI Package

```bash
pip install openai
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

## Usage

### With LLM Categorization (Default)

```bash
cd src
python main.py
```

### Without LLM (Keyword-based)

```bash
cd src
python main.py --no-llm
```

### Test Mode (No Email)

```bash
cd src
python main.py --no-email
```

## Cost Estimation

### OpenRouter Pricing

**Using `openai/gpt-4o-mini`:**
- Input: ~50 articles × 200 tokens = 10,000 tokens
- Output: ~50 categories × 5 tokens = 250 tokens
- Cost: ~$0.015 per run (weekly)
- **Monthly cost: ~$0.06**

**Using `openai/gpt-4o`:**
- Same usage: ~$0.15 per run
- **Monthly cost: ~$0.60**

**Using `anthropic/claude-3.5-sonnet`:**
- Same usage: ~$0.10 per run
- **Monthly cost: ~$0.40**

### GitHub Models Pricing

**Free Tier:**
- Generous free tier for personal use
- Rate limits apply
- Perfect for weekly blog digest

**After free tier:**
- Similar to OpenRouter pricing
- Pay-per-use model

## Configuration

### Change Provider

Edit `config/llm_categories.yaml`:

```yaml
llm:
  provider: "openrouter"  # or "github"
  model: "openai/gpt-4o-mini"
```

### Available Models

#### OpenRouter Models

Format: `"provider/model-name"`

**Recommended:**
- `openai/gpt-4o-mini` - Fast, cheap, good quality
- `openai/gpt-4o` - Best quality
- `anthropic/claude-3.5-sonnet` - Excellent alternative
- `meta-llama/llama-3.1-70b-instruct` - Open source

See full list: https://openrouter.ai/models

#### GitHub Models

Format: `"model-name"`

**Recommended:**
- `gpt-4o-mini` - Fast, free tier available
- `gpt-4o` - Best quality
- `meta-llama-3.1-405b-instruct` - Large open source
- `phi-3.5-mini-instruct` - Small, efficient
- `ai21-jamba-1.5-large` - Alternative provider

See full list: https://github.com/marketplace/models

### Customize Categories

Edit the `categories` section in `config/llm_categories.yaml`:

```yaml
categories:
  - name: "Your Category Name"
    description: "Clear description for LLM to understand what belongs here"
```

**Tips for good category descriptions:**
- Be specific and detailed
- Include examples of topics
- Mention key technologies or concepts

## Troubleshooting

### "OPENROUTER_API_KEY not found" or "GITHUB_TOKEN not found"
- Verify the environment variable is set: `echo $OPENROUTER_API_KEY` or `echo $GITHUB_TOKEN`
- Make sure OpenRouter keys start with `sk-or-v1-`
- Make sure GitHub tokens start with `ghp_`
- Restart your terminal after setting it

### "Rate limit exceeded"
- **OpenRouter**: Reduce `batch_size` in config, wait a minute
- **GitHub Models**: You hit free tier limits, wait for reset or upgrade

### "Insufficient credits" (OpenRouter)
- Add credits or payment method in OpenRouter dashboard
- Check your balance: https://openrouter.ai/credits

### "Authentication failed" (GitHub Models)
- Verify token has correct scopes: `repo`, `read:org`
- Regenerate token if expired
- Check GitHub Models access: https://github.com/marketplace/models

### "Invalid JSON response"
- The LLM returned malformed JSON
- System automatically falls back to keyword matching
- Check logs for details
- Try a different model in config

### Which provider should I choose?

**Choose OpenRouter if:**
- ✅ You want access to 100+ models
- ✅ You need consistent performance
- ✅ Small cost (~$0.06/month) is acceptable
- ✅ You want to try different providers easily

**Choose GitHub Models if:**
- ✅ You want to start completely free
- ✅ You're already a GitHub user
- ✅ You're okay with rate limits
- ✅ You don't need exotic models

### Fallback Behavior

The system automatically falls back to keyword matching if:
- API key/token is not set
- API request fails
- Response cannot be parsed
- `fallback_to_keywords: true` in config

## Quick Start Examples

### Using OpenRouter with GPT-4o-mini
```yaml
# config/llm_categories.yaml
llm:
  provider: "openrouter"
  model: "openai/gpt-4o-mini"
```
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
python main.py
```

### Using GitHub Models (Free)
```yaml
# config/llm_categories.yaml
llm:
  provider: "github"
  model: "gpt-4o-mini"
```
```bash
export GITHUB_TOKEN="ghp_..."
python main.py
```

### Using Keyword Fallback Only
```bash
python main.py --no-llm
```

## Questions?

- Check main README.md for general setup
- Review config files for all options
- Open GitHub issue for bugs
