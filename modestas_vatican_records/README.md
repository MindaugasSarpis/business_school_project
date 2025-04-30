# Vatican Records Chatbot

A RAG (Retrieval-Augmented Generation) based chatbot application that allows users to interact with PDF documents through a conversational interface. The application uses Chainlit for the UI, ChromaDB for vector storage, and integrates with LLMs for generating responses.

## Project Structure

- `app.py`: Main application file containing the Chainlit chat interface
- `main.py`: Entry point for running the application
- `setup.py`: Environment setup and dependency installation script
- `chatbot/`: Core chatbot implementation
  - `session.py`: Session management and RAG operations
  - `llm.py`: Language model integration
  - `reranking.py`: Document reranking functionality
  - `utils/`: Utility functions and logging configuration
- `chroma_db/`: Vector database storage
- `tests/`: Test suite for the application
- `.chainlit/`: Chainlit configuration files

## Key Components

1. **Chainlit Interface**: Provides a user-friendly chat interface
2. **ChromaDB**: Vector database for storing and retrieving document embeddings
3. **RAG Pipeline**: 
   - Document retrieval
   - Context reranking
   - Response generation using LLMs
4. **Session Management**: Handles conversation history and context

## Prerequisites

- Python 3.x
- Poetry (for dependency management)
- Virtual environment support

## Installation

1. Clone the repository
2. Run the setup script:
   ```bash
   python setup.py
   ```
   This will:
   - Create a virtual environment
   - Install Poetry
   - Configure Poetry
   - Install all dependencies
   - Set up the test environment

## Running the Application

1. After installation, start the chatbot:
   ```bash
   python main.py
   ```
   This will launch the Chainlit interface in your default web browser.

2. The application will:
   - Load necessary resources
   - Initialize the chat session
   - Be ready to accept user queries

## Features

- Interactive chat interface
- PDF document processing and querying
- Context-aware responses
- Document source attribution
- Conversation history management

## Development

- The project uses Poetry for dependency management
- Tests can be run using `python test.py`
- Environment variables are managed through `.env` files in the tests directory

## Notes

- The application testing requires proper configuration of API keys and environment variables
- Document processing and embedding generation happens during the initial setup
- The chat interface provides real-time feedback on the processing status
