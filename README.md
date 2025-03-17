# AI Library Chatbot

## Overview

The AI Library Chatbot is a smart, AI-powered assistant designed to help users with library-related inquiries. Built using Flask for the backend and Streamlit for the frontend, this chatbot integrates OpenAI's API for natural language understanding, Pinecone for vectorized FAQ retrieval, and LangChain for conversation memory. It can handle general library FAQs, appointment bookings, and sentiment-based interactions, providing an intuitive support experience.

## Features

- **Conversational AI**: Uses OpenAI's API to process and respond to user queries in a natural way.
- **FAQ Retrieval with Pinecone**: Quickly finds answers to library-related questions using a vector database.
- **Session Management**: Users can start and continue conversations within named sessions.
- **Sentiment Analysis & Escalation**: Identifies user sentiment and escalates issues when necessary.
- **Appointment Handling**: Allows users to request and confirm library appointments.
- **Multilingual Support**: Responds to users in multiple languages based on input.

## Prerequisites

- **Python Version**: Ensure you have Python **3.12.7** installed.
- **API Keys**:
  - OpenAI API Key
  - Pinecone API Key & Environment

## Environment Setup Guide

### 1. Create a `.env` File

Inside the root directory, create a `.env` file and add:

```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone API Key and Environment
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=your_pinecone_environment_here
```

Replace `your_openai_api_key_here` and `your_pinecone_api_key_here` with actual API keys.

### 2. Obtain API Keys

#### OpenAI API Key

1. Go to [OpenAI's platform](https://platform.openai.com/).
2. Sign in and generate a new API key.
3. Copy and paste it into your `.env` file.

#### Pinecone API Key

1. Go to [Pinecone's website](https://www.pinecone.io/).
2. Sign up or log in and generate a new API key.
3. Copy and paste it into your `.env` file.

### 3. Set Up the Python Environment

#### Create and activate a virtual environment:

```bash
python -m venv venv
```

- On Windows:

```bash
.\venv\Scripts\activate
```

- On macOS/Linux:

```bash
source venv/bin/activate
```

#### Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Running the Project

#### Start the Backend (`server.py`)

```bash
python server.py
```

The backend runs on `http://localhost:5000`.

#### Start the Frontend (`frontend.py`)

```bash
python frontend.py
```

If using Streamlit, access the frontend at `http://localhost:8501`.

## Tests

To verify functionality, run:

```bash
python -m unittest test_library_chatbot.py
```

This will test session creation, sentiment analysis, FAQ queries, appointment handling, and error handling.

RAG integration test, run:

```bash
python test_faq_search.py
```
