# Smartpack

This project is a Python-based web application that provides a CRUD interface for data stored in a database and uses an AI model to process user queries and generate responses.

## Getting Started

To get started with this project, clone the repository to your local machine and navigate to the `src` directory. This directory contains all the source code for the application.

## Setting Up the variables
Add the following variables that you got provided in the project submission. The file should be named constants.py and should be placed in the utils folder.


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

- main.py: The start of the application, instantiating different modules 
- CRUDdb.py: Handles the CRUD operations for the relational database. Contains the API-endpoints for the CRUD as well as the 	query-endpoint for the chatbot. 
- sql.py: Establishes the connection between the relational database. 
- client.py: A test script for the examiner to check the applications functionality  
- utils/bot_utils.py: Contains utility functions for data formatting and interaction with the vector database. 

## Authors

- Agnar Kåre Hereid Spilde
- Henrik Halse Vik
- Dennis Johnsen
- Alexander Paulsen
