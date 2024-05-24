# Smartpack

This project is a Python-based web application that provides a CRUD interface for data stored in a database and uses an AI model to process user queries and generate responses.

## Getting Started

To get started with this project, clone the repository to your local machine and navigate to the `src` directory. This directory contains all the source code for the application.

### Prerequisites

You will need Python 3.9 or later installed on your machine. You will also need the following Python packages:

- FastAPI
- psycopg2
- pandas
- OpenAI
- chromadb

You can install these packages using pip:

```bash
pip install fastapi psycopg2 pandas openai chromadb
```

## Running the Application

This application is designed to be run locally for development purposes. To run the application, navigate to the `src` directory and run the `main.py` script:

```bash
python main.py
```

To test the application, you can run the `client.py` script:

```bash
python client.py
```

## Built With

- **Python**: The main programming language used.
- **FastAPI**: The web framework used for building the API.
- **psycopg2**: The PostgreSQL adapter used for database interactions.
- **pandas**: The data analysis and manipulation library used.
- **OpenAI's GPT model**: Used for natural language processing tasks.
- **chromadb**: Used for creating and managing the Chroma vector store.

## Components

- `bot.py`: Handles the interaction with the OpenAI model and the Chroma vector store. Loads data from a CSV file, generates embeddings for the data, and uses those embeddings to create a `ConversationalRetrievalChain` with the `ChatOpenAI` model.
- `CRUDdb.py`: Contains the CRUD (Create, Read, Update, Delete) operations for interacting with the database. Uses the FastAPI framework to define API endpoints for these operations.
- `main.py`: The main script and the entry point for the application. Imports functionality from other scripts, such as `CRUDdb.py` and `bot.py`.
- `sql.py`: Handles the interaction with the PostgreSQL database. Contains functions for creating a database connection, executing SQL queries, and formatting data.
- `client.py`: A script for testing the application. Sends a GET request to the application and prints the response.
- `utils/bot_utils.py`: Contains utility functions for the bot, such as formatting responses and adding data to the Chroma vector store.

## Authors

- Agnar Kåre Hereid Spilde
- Henrik Halse Vik
- Dennis Johnsen
- Alexander Paulsen
