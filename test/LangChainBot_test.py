import os
import time
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.vectorstores import Chroma
import src.utils.constants as cs
import LangChainbot_utils as utils
from test.testdata import test_data as td

os.environ["OPENAI_API_KEY"] = cs.chain_bot_key

PERSIST = True

# List of questions to test
questions = td.test_questions

# CSV file to save the results
csv_file = "testresults/ChainBot_results.csv"
# Write results to a stylish text file
output_file = "testresults/ChainBot_cost_analysis.txt"

# Main loop simplified for clarity
if __name__ == "__main__":
    embedding_function = utils.embedding_function

    if PERSIST and os.path.exists("test_vectordb"):
        print("Reusing index...\n")
        vectorstore = Chroma(persist_directory="test_vectordb", embedding_function=embedding_function)
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
        csv_file_path = 'testdata/csvV1.csv'
        embeddings = utils.load_and_embed_csv(csv_file_path)
        vectorstore = Chroma(persist_directory="test_vectordb", embedding_function=embedding_function)
        for emb in embeddings:
            print("Adding embeddings")
            vectorstore.add_texts([emb['text']], ids=[emb['id']], embeddings=[emb['embedding']])
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-4o"),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 5}),
    )

    chat_history = []
    results = []
    total_prompt_tokens = 0
    total_response_tokens = 0
    num_questions = len(questions)
    for user_input in questions:

        try:
            print(user_input)
            start_time = time.time()
            print("Processing question...")

            prompt = utils.construct_prompt(user_input)
            result = chain.invoke(
                {"question": prompt, "chat_history": chat_history})  # Adjusted to send the entire prompt
            print(result['answer'])
            formatted_answer = utils.format_answer_with_bullets(result['answer'])
            # Calculate token usage for user_input, chat_history, and formatted_answer
            history_text = ' '.join([q + ' ' + a for q, a in chat_history])
            prompt_tokens_total = utils.count_tokens(prompt + history_text, model="gpt-4-turbo-preview")
            completion_tokens_total = utils.count_tokens(result['answer'], model="gpt-4-turbo-preview")
            token_usage_total = completion_tokens_total + prompt_tokens_total

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Question: {user_input}")
            print(f"Answer: {formatted_answer}")
            print(f"Time: {elapsed_time} seconds")
            print(f"Token Usage (total): {token_usage_total}")
            print(f"Chat_history: {chat_history}")

            results.append([user_input, formatted_answer, elapsed_time, token_usage_total])
            chat_history.append((user_input, formatted_answer))
            total_prompt_tokens += prompt_tokens_total
            total_response_tokens += completion_tokens_total
            # Ensure chat_history never exceeds 4 entries
            if len(chat_history) > 4:
                chat_history.pop(0)

        except ValueError as e:
            print(e)
            continue

    # Save results to CSV
    utils.log_results_to_csv(results, csv_file)
    print(f"Results saved to {csv_file}")

    # Calculate averages
    average_prompt_tokens = total_prompt_tokens / num_questions
    average_response_tokens = total_response_tokens / num_questions

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
