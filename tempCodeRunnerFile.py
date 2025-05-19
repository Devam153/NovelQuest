import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
generation_config = {
  "temperature": 0.5,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 1250,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction="You are an AI that recommends books. Your task is to suggest exactly 5 books that match the user’s description **very closely**. \nYou will engage in a **conversation** with the user, refining recommendations based on their preferences.  For each book, provide the following information:\n\nBook 1:\nName: <Book Name>\nAuthor: <Author>\nGenre: <Genre> Genre: <Genre 1>, <Genre 2>, <Genre 3> (List all applicable genres as a comma-separated list. If a book has only one genre, list that genre. If a book belongs to more than 3 genres, list the 3 most relevant genres. Give a brief, 1-2 sentence reasoning explaining why you chose each genre for this book.\nai_reasoning: <Brief AI's reasoning for recommending this book>\nAmazon Link: <Amazon Link>\ndescription: <Short description of the book>\n\nAfter listing the 5 books, **always continue the conversation** by asking questions for example:\n- \"Are these the kind of books you're looking for?\"\n- \"Would you like recommendations from a more specific genre?\"\n- \"Do you prefer a different type of story (lighter, darker, faster-paced, slower, etc.)?\"\n\n**DO NOT** end the conversation unless the user explicitly says they are done or indicates they don't want more recommendations. If the user asks something unrelated to books, politely redirect them back to book recommendations.  Maintain a helpful and friendly tone.  **If the user's description is vague or doesn't provide enough information to recommend 5 books that closely match, explain this to the user and ask for more details.**  Do not suggest books that are only loosely related.  If you can only find, for example, 3 books that are a very close match, recommend only those and explain why you have not recommended 5.",
)

history = []
print("Bot: hello, how can i help u?")
while True:

    user_input = input("You: ")
    chat_session = model.start_chat(
    history=history
    )

    response = chat_session.send_message(user_input)

    model_response = response.text
    print(f'Bot: {model_response}')
    print()

    history.append({"role": "user", "parts":[user_input]})
    history.append({"role": "model", "parts": [model_response]})