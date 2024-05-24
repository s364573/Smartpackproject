from openai import OpenAI
import src.utils.constants as cs
import src.utils.bot_utils as bot
import chromadb
import csv
import time
from test.testdata import test_data as td

chroma_client = chromadb.PersistentClient()
client = OpenAI(api_key=cs.Original_bot_key)
collection = chroma_client.get_collection(name="test_collection")

csv_file = "testresults/OriginalBot_results.csv"
output_file = "testresults/OriginalBot_cost_analysis.txt"

questions = td.test_questions
# Join instructions into a single string
instructions_str = " ".join(bot.instructions)


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
    with open('testdata/csvV1.csv', newline='') as csvfile:
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


results = []
chat_history = []
total_prompt_tokens = 0
total_response_tokens = 0
num_questions = len(questions)

for query in questions:
    start_time = time.time()
    response = collection.query(
        query_texts=[query],  # Chroma will embed this for you
        n_results=5  # how many results to return
    )
    result_from_chroma = format_nicely(response)
    formatted_results_str = "\n\n".join(result_from_chroma)
    openai_result, user_input = openai_completion(query, formatted_results_str,chat_history)
    end_time = time.time()
    print(openai_result)
    print(f"Question: {user_input}")
    print(f"Answer: {openai_result.choices[0].message.content}")
    print("Time taken:", end_time - start_time)
    print(f"Token Usage (total): {openai_result.usage.total_tokens}")
    print(f"Token Usage (prompt): {openai_result.usage.prompt_tokens}")
    print(f"Token Usage (response): {openai_result.usage.completion_tokens}")
    total_prompt_tokens += openai_result.usage.prompt_tokens
    total_response_tokens += openai_result.usage.completion_tokens

    results.append([user_input, openai_result.choices[0].message.content, end_time - start_time, openai_result.usage.total_tokens])
    chat_history.append((user_input, openai_result.choices[0].message.content))  # Ensure it's a tuple


    # Ensure chat_history never exceeds 4 entries
    if len(chat_history) > 4:
        chat_history.pop(0)

# Calculate costs
cost_per_prompt_token = 5.00 / 1_000_000  # $5.00 per 1M tokens
cost_per_response_token = 15.00 / 1_000_000  # $15.00 per 1M tokens

total_prompt_cost = total_prompt_tokens * cost_per_prompt_token
total_response_cost = total_response_tokens * cost_per_response_token
total_cost = total_prompt_cost + total_response_cost

# Calculate averages
average_prompt_tokens = total_prompt_tokens / num_questions
average_response_tokens = total_response_tokens / num_questions

# Calculate costs for 4200 queries
total_prompt_tokens_4200 = average_prompt_tokens * 4200
total_response_tokens_4200 = average_response_tokens * 4200

total_prompt_cost_4200 = total_prompt_tokens_4200 * cost_per_prompt_token
total_response_cost_4200 = total_response_tokens_4200 * cost_per_response_token
total_cost_4200 = total_prompt_cost_4200 + total_response_cost_4200

# Save results to CSV
bot.log_results_to_csv(results, csv_file)

with open(output_file, "w") as f:
    f.write("=" * 50 + "\n")
    f.write(" " * 15 + "COST ANALYSIS REPORT\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Results saved to: {csv_file}\n\n")

    f.write("TOTAL TOKEN USAGE\n")
    f.write("-" * 50 + "\n")
    f.write(f"Prompt tokens: {total_prompt_tokens}\n")
    f.write(f"Response tokens: {total_response_tokens}\n")
    f.write("\n")

    f.write("AVERAGE TOKEN USAGE PER QUESTION\n")
    f.write("-" * 50 + "\n")
    f.write(f"Average prompt tokens: {average_prompt_tokens:.2f}\n")
    f.write(f"Average response tokens: {average_response_tokens:.2f}\n")
    f.write("\n")

    f.write("TOTAL COST\n")
    f.write("-" * 50 + "\n")
    f.write(f"Prompt tokens cost: ${total_prompt_cost:.2f}\n")
    f.write(f"Response tokens cost: ${total_response_cost:.2f}\n")
    f.write(f"Overall cost: ${total_cost:.2f}\n")
    f.write("\n")

    f.write("ESTIMATED COST FOR 4200 QUERIES\n")
    f.write("-" * 50 + "\n")
    f.write(f"Total prompt tokens: {total_prompt_tokens_4200}\n")
    f.write(f"Total response tokens: {total_response_tokens_4200}\n")
    f.write(f"Total prompt tokens cost: ${total_prompt_cost_4200:.2f}\n")
    f.write(f"Total response tokens cost: ${total_response_cost_4200:.2f}\n")
    f.write(f"Overall cost for 4200 queries: ${total_cost_4200:.2f}\n")
    f.write("=" * 50 + "\n")

print(f"Cost analysis written to {output_file}")
