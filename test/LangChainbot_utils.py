# src/bot_utils.py
import os
import re
import pandas as pd
from langchain_openai.embeddings import OpenAIEmbeddings
import openai
import tiktoken
import csv

# Define constants
APIKEY = "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"
os.environ["OPENAI_API_KEY"] = APIKEY

embedding_function = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=openai.api_key)

# Precompile regex patterns for efficiency
transition_phrases = ["Angående", "Også videre", "osv", "I tillegg", "Note:"]
transition_phrases_pattern = re.compile(r"(?<!\.)\s(" + "|".join(transition_phrases) + ")")

def count_tokens(*texts, model):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        raise ValueError(f"Could not automatically map {model} to a tokenizer. Please use a valid model name.")
    total_tokens = sum(len(encoding.encode(text)) for text in texts)
    return total_tokens


def format_answer_with_bullets(answer):
    # Use compiled regex for replacing transition phrases
    answer = transition_phrases_pattern.sub(r". \1", answer)

    # Efficient sentence splitting
    items = re.split(r'(?<=[^A-Z].[.?]) (?=[A-Z])', answer)
    bullet_formatted_answer = "\n".join(f"• {item.strip()}" for item in items if item)

    return "" + bullet_formatted_answer


def construct_prompt(user_input):
    instructions = [
        "Focus exclusively on responding to inquiries concerning items allowed in luggage for air travel.",
        "You only respond to inquiries concerning items allowed in luggage for air travel.",
        "You may give recommendations about items to bring for travel, if asked.",
        "Examine the details of each item mentioned by the user, assessing their permissibility based on current regulations.",
        "Offer thorough explanations to ensure users understand the reasoning behind each decision.",
        "Maintain clarity and brevity in your responses, avoiding unnecessary elaboration.",
        "Respond only in Norwegian.",
        "We have these categories to choose from within the context: Mat, Sportsutstyr, Batteri, Verktøy, Våpen, Flytende væsker, Eksplosive stoffer, Medisiner, Skarpe gjenstander, Brennbart stoff"
    ]
    instruction_text = " ".join(instructions)  # Combine the list into a single string separated by spaces.
    return f"Instructions for the AI:\n{instruction_text}\n\nUser: {user_input}\nAI:"


def load_and_embed_csv(csv_file_path):
    # Load CSV data
    data = pd.read_csv(csv_file_path)

    # Combine relevant columns into one text field for embedding
    data['combined_text'] = data.apply(
        lambda
            row: f"{row['gjenstandnavn']} {row['gjenstandbeskrivelse']} {row['kategorinavn']} {row['kategoribeskrivelse']} {row['regelverkbeskrivelse']}",
        axis=1
    )

    # Generate embeddings
    data['embedding'] = data['combined_text'].apply(lambda x: embedding_function.embed_query(x))

    # Prepare embeddings for vector store insertion
    embeddings = [{'id': str(row['gjenstandid']), 'embedding': row['embedding'], 'text': row['combined_text']} for
                  _, row in data.iterrows()]
    return embeddings

def log_results_to_csv(results, csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer", "Time (seconds)", "Token Usage (total)"])
        for result in results:
            writer.writerow(result)