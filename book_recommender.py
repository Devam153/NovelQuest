
import os
import re
import google.generativeai as genai
import time
import urllib.parse

def configure_genai(api_key):
    """Configure the Gemini API with the provided API key."""
    genai.configure(api_key=api_key)
    
def generate_amazon_in_link(book_title, author):
    """Generate a valid Amazon India search link for a book."""
    query = f"{book_title} {author} book"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.amazon.in/s?k={encoded_query}"

def get_book_recommendations(user_prompt, api_key, num_results=5, context=None):
    """Get book recommendations from Gemini API based on user prompt."""
    # Configure Gemini
    configure_genai(api_key)
    
    # Create the model
    generation_config = {
        "temperature": 0.5,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1250,
        "response_mime_type": "text/plain",
    }
    
    # System prompt with dynamic number of results and Indian pricing
    system_prompt = f"""You are an AI that recommends books. Your task is to suggest exactly {num_results} books that match the user's description **very closely**. 
    You will engage in a **conversation** with the user, refining recommendations based on their preferences.
    
    For each book, provide the following information in this exact format:

    Book 1:
    Name: <Book Name>
    Author: <Author>
    Genre: <Genre 1>, <Genre 2>, <Genre 3> (List all applicable genres as a comma-separated list)
    Price: <Approximate price in INR (Indian Rupees), e.g. ₹499>
    ai_reasoning: <Brief AI's reasoning for recommending this book>
    Amazon Link: <Leave this blank - I will generate it automatically>
    description: <Short description of the book>

    Book 2:
    ... and so on for all {num_results} books.

    After listing the {num_results} books, **always continue the conversation** by asking questions for example:
    - "Are these the kind of books you're looking for?"
    - "Would you like recommendations from a more specific genre?"
    - "Do you prefer a different type of story (lighter, darker, faster-paced, slower, etc.)?"

    **DO NOT** end the conversation unless the user explicitly says they are done or indicates they don't want more recommendations. If the user asks something unrelated to books, politely redirect them back to book recommendations. Maintain a helpful and friendly tone. **If the user's description is vague or doesn't provide enough information to recommend {num_results} books that closely match, explain this to the user and ask for more details.** Do not suggest books that are only loosely related.
    
    IMPORTANT: List prices in Indian Rupees (₹) as these books will be purchased from Amazon India."""
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction=system_prompt,
        )
        
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
    """Extract structured book information from the AI response and generate valid Amazon links."""
    books = []
    
    # Updated regex pattern to match book sections including price
    book_pattern = r"Book \d+:\s*Name: (.*?)\s*Author: (.*?)\s*Genre: (.*?)\s*Price: (.*?)\s*ai_reasoning: (.*?)\s*Amazon Link:.*?description: (.*?)(?=\s*Book \d+:|$)"
    
    # Find all matches
    matches = re.findall(book_pattern, response_text, re.DOTALL)
    
    for match in matches:
        if len(match) == 6:
            name, author, genre, price, ai_reasoning, description = [item.strip() for item in match]
            
            # Generate a valid Amazon.in link
            amazon_link = generate_amazon_in_link(name, author)
            
            book = {
                "name": name,
                "author": author,
                "genre": genre,
                "price": price,
                "ai_reasoning": ai_reasoning,
                "amazon_link": amazon_link,
                "description": description
            }
            
            books.append(book)
    
    return books