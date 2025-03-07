# AI-Chatbot-Library

## Environment Setup Guide

This project uses environment variables stored in a `.env` file to configure sensitive information securely.

### 1. Create a `.env` File

Inside the root directory of the project, create a new file named `.env` and add the following content:

```
# OpenAI API Key OPENAI_API_KEY=your_openai_api_key_here  # Pinecone API Key and Environment PINECONE_API_KEY=your_pinecone_api_key_here PINECONE_ENV=your_pinecone_environment_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.  
Replace `your_pinecone_api_key_here` with your Pinecone API key and `your_pinecone_environment_here` with your Pinecone environment.

### 2. Obtain API Keys

#### OpenAI API Key

If you do not have an OpenAI API key, follow these steps:

1. Go to [OpenAI's platform](https://platform.openai.com/).
2. Sign in or create an account.
3. Navigate to the API Keys section and generate a new API key.
4. Copy the key and paste it into your `.env` file.

#### Pinecone API Key

To obtain a Pinecone API key:

1. Go to [Pinecone's website](https://www.pinecone.io/).
2. Sign up or log in.
3. Navigate to the API Keys section and generate a new key.
4. Copy the key and paste it into your `.env` file.

### 3. Set Up the Python Environment

To set up your Python environment, follow these steps:

1. **Create a virtual environment**: Run the following command to create a virtual environment:

```bash
python -m venv venv
```

2. **Activate the virtual environment**:

- On Windows:

```bash
   .\venv\Scripts\activate
```

- On macOS/Linux:

```bash
   source venv/bin/activate
```

3. **Install the required dependencies**: Run the following command to install the project dependencies from `requirements.txt`:

```bash
   pip install -r requirements.txt
```

### 4. Running the Project

#### Backend: `server.py`

To run the backend (Flask server):

1. **Navigate to the project directory** (if you are not already there):

```bash
cd path/to/your/project
```

2. **Run the Flask server**:

```bash
python server.py
```

The server should now be running. You can test it by visiting `http://localhost:5000` in your web browser.

#### Frontend: `frontend.py`

If you have a frontend component to run (for example, using Streamlit or another framework), follow these steps:

1. **Navigate to the project directory** (if not already there):

```bash
cd path/to/your/project
```

2. **Run the frontend**:

```bash
python frontend.py
```

The frontend should now be running. You can test it by visiting the appropriate URL provided by the frontend application (such as `http://localhost:8501` for Streamlit).
