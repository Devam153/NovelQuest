import os
import re
import google.generativeai as genai

def configure_genai(api_key):
    """Configure the Gemini API with the provided API key."""
    genai.configure(api_key=api_key)
    
def get_book_recommendations(user_prompt, api_key, context=None):
    """Get book recommendations from Gemini API based on user prompt."""
    # Configure Gemini
    configure_genai(api_key)
    
    # Create the model
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    }
    
    # Enhanced system prompt
    system_prompt = """You are an AI that recommends books. Your task is to suggest exactly 5 books that match the user's description **very closely**.
    You will engage in a **conversation** with the user, refining recommendations based on their preferences.
    
    For each book, provide the following information in this exact format:
    
    Book 1:
    Name: <Book Name>
    Author: <Author>
    Genre: <Genre 1>, <Genre 2>, <Genre 3> (List all applicable genres as a comma-separated list)
    ai_reasoning: <Brief AI's reasoning for recommending this book>
    Amazon Link: <Amazon Link>
    description: <Short description of the book>
    
    Book 2:
    ...and so on for all 5 books.
    
    After listing the 5 books, **continue the conversation** by asking questions, for example:
    - "Are these the kind of books you're looking for?"
    - "Would you like recommendations from a more specific genre?"
    - "Do you prefer a different type of story?"
    
    If the user's description is vague or doesn't provide enough information, explain this and ask for more details.
    Only suggest books that closely match the user's request."""
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=system_prompt,
    )
    
    try:
        # If there's context, use it to create a conversation
        if context:
            chat = model.start_chat(history=[])
            response = chat.send_message(f"Previous conversation: {context}\n\nNew request: {user_prompt}")
        else:
            response = model.generate_content(user_prompt)
        
        return response.text
    except Exception as e:
        raise Exception(f"Error getting recommendations: {str(e)}")

def extract_books_from_response(response_text):
    """Extract structured book information from the AI response."""
    books = []
    
    # Regular expression pattern to match book sections
    book_pattern = r"Book \d+:\s*Name: (.*?)\s*Author: (.*?)\s*Genre: (.*?)\s*ai_reasoning: (.*?)\s*Amazon Link: (.*?)\s*description: (.*?)(?=\s*Book \d+:|$)"
    
    # Find all matches
    matches = re.findall(book_pattern, response_text, re.DOTALL)
    
    for match in matches:
        name, author, genre, ai_reasoning, amazon_link, description = [item.strip() for item in match]
        
        book = {
            "name": name,
            "author": author,
            "genre": genre,
            "ai_reasoning": ai_reasoning,
            "amazon_link": amazon_link,
            "description": description
        }
        
        books.append(book)
    
    return books