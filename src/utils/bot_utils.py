# src/bot_utils.py
import csv
from openai import OpenAI
import chromadb
import utils.constants as cs


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

instructions_str = " ".join(instructions)

def log_results_to_csv(results, csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer", "Time (seconds)", "Token Usage (total)"])
        for result in results:
            writer.writerow(result)


def openai_completion(user_input, results, chat_history):
    # Format chat history
    history_str = "\n".join([f"User: {q}\nBot: {a}" for q, a in chat_history])
    prompt = f"This is the question: {user_input}\nThis is the information you will need to answer the question:\n{results}\n\nChat history:\n{history_str}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instructions_str},
            {"role": "user", "content": prompt}
        ]
    )
    return completion, user_input


def format_nicely(results):
    formatted_results = []
    for idx, doc_id in enumerate(results['ids'][0]):
        formatted_result = []
        formatted_result.append(f"Document ID: {doc_id}")
        formatted_result.append(f"Distance: {results['distances'][0][idx]:.4f}")
        formatted_result.append(f"Document: {results['documents'][0][idx]}")
        metadata = results['metadatas'][0][idx]
        formatted_result.append("Metadata:")
        for key, value in metadata.items():
            formatted_result.append(f"  {key}: {value}")
        formatted_results.append("\n".join(formatted_result))
    return formatted_results


def add_csv_to_chroma(collection):
    with open('../data/c.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for id, row in enumerate(reader):
            print(id + 1, row['gjenstandnavn'],
                  row['gjenstandbeskrivelse'],
                  row['kategorinavn'],
                  row['kategoribeskrivelse'],
                  row['betingelse'],
                  row['verdi'],
                  row['tillatthandbagasje'],
                  row['tillattinnsjekketbagasje'],
                  row['regelverkbeskrivelse'])

            document = row['gjenstandnavn']
            metadata = {
                "gjenstandbeskrivelse": row['gjenstandbeskrivelse'],
                "kategorinavn": row['kategorinavn'],
                "kategoribeskrivelse": row['kategoribeskrivelse'],
                "betingelse": row['betingelse'],
                "verdi": row['verdi'],
                "tillatthandbagasje": row['tillatthandbagasje'],
                "tillattinnsjekketbagasje": row['tillattinnsjekketbagasje'],
                "regelverkbeskrivelse": row['regelverkbeskrivelse']
            }

            collection.upsert(
                documents=[document],
                metadatas=[metadata],
                ids=[f"id{id}"]
            )
    return collection


client = OpenAI(api_key=cs.main_key)

chroma_client = chromadb.PersistentClient()

collection = chroma_client.get_or_create_collection(
    name="item_collection",
)

if collection.count() == 0:
    collection = add_csv_to_chroma(collection)
