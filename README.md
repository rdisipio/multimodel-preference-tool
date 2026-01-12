---
title: Multi-Model LLM Comparison Tool
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "6.3.0"
app_file: app.py
pinned: false
---

# Multi-Model LLM Comparison Tool

UX-first interface to choose the best answer among different LLM models.

## Overview

An exploratory tool for comparing responses from multiple Large Language Models (LLMs) side-by-side. Ask a question, select models, and choose which response works best for you. Built with privacy in mind - all data collection is opt-in only.

## Features

- 🤖 **Multi-Model Comparison**: Query multiple LLMs simultaneously via Groq API
- ⚖️ **Side-by-Side View**: Compare responses in a clean, readable format
- 📏 **Adjustable Output Length**: Choose Short, Medium, or Full responses
- 👍 **Preference Selection**: Mark which response works best for you
- 🔒 **Privacy-First**: Opt-in data collection only
- 🎨 **Clean UX**: Minimalist, user-friendly interface

## Supported Models

- GPT-4 (via Llama 3.3 70B on Groq)
- Claude 3 Opus (via Llama 3.1 70B on Groq)
- Gemini Pro (via Mixtral 8x7B)
- Llama 2 70B
- Mistral Large (via Mixtral 8x7B)

*Note: Model names are mapped to available Groq models for demonstration purposes*

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://huggingface.co/spaces/rdisipio/multimodel-preference-tool
   cd multimodel-preference-tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Groq API key
   ```

4. **Get your Groq API key**
   - Sign up at [Groq Console](https://console.groq.com/)
   - Generate an API key
   - Add it to your `.env` file

5. **Run the app**
   ```bash
   python app.py
   ```

### Hugging Face Spaces Deployment

This app is designed to run on Hugging Face Spaces with Gradio.

1. **Set up your Space**
   - Create a new Gradio Space on Hugging Face
   - Upload `app.py`, `requirements.txt`, and `README.md`

2. **Configure Secrets**
   - In your Space settings, add a secret:
     - Name: `GROQ_API_KEY`
     - Value: Your Groq API key

3. **Deploy**
   - Your Space will automatically build and deploy

## Usage

1. **Enter your question** in the text area
2. **Select output length**: Short, Medium, or Full
3. **Choose models** to compare (select at least one)
4. **Click "Compare answers"** to see responses
5. **Review responses** side-by-side
6. **Click "This one works for me"** to record your preference (optional)

## Privacy

- **No data collection by default**: Your questions and responses stay private
- **Opt-in preferences**: Only recorded when you click preference buttons
- **Transparent**: All data handling is visible in the open-source code
- **Local-first**: Run locally for complete privacy

## Project Background

This tool is part of an exploration in open human feedback collection for LLM evaluation. The goal is to create a lightweight, UX-first interface that makes it easy for users to compare model outputs and provide feedback.

For more details, see the project documentation in the repository.

## Built By

Human Feedback Foundation  
Linux Foundation AI & Data member

## License

See [LICENSE](LICENSE) file for details.
