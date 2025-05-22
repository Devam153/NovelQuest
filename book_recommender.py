
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
        "max_output_tokens": 2048,  # Increased token limit
        "response_mime_type": "text/plain",
    }
    
    # System prompt with more specific format instructions to ensure consistent output
    # and explicitly asking not to include questions about book preferences
    system_prompt = f"""You are an AI that recommends books. Your task is to suggest exactly {num_results} books that match the user's description **very closely**. 
    You will engage in a **conversation** with the user, refining recommendations based on their preferences.
    
    For each book, provide the following information in this EXACT format (follow this format precisely):

    Name: <Book Name>
    Author: <Author>
    Genre: <Genre 1>, <Genre 2>, <Genre 3> (List all applicable genres as a comma-separated list)
    Price: <Approximate price in INR (Indian Rupees), e.g. ₹499>
    ai_reasoning: <Brief AI's reasoning for recommending this book>
    Amazon Link:
    description: <description of the book atleast 75 words for each.>

    Repeat the above format for all {num_results} books. Do not include any other text between book recommendations. Number them as Book 1, Book 2, etc.

    IMPORTANT: DO NOT include questions like "Are these the kind of books you're looking for?" or similar questions in your responses or in book descriptions. Simply provide the information in the format requested.

    After listing all {num_results} books, you can continue the conversation by asking questions.
    Do not end the conversation unless the user explicitly says they are done.
    Maintain a helpful and friendly tone. If the user's description is vague, ask for more details.
    List prices in Indian Rupees (₹) as these books will be purchased from Amazon India.

    IMPORTANT: Always maintain the exact format shown above for each book with the specified fields in that exact order."""
    
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
    
    # More robust pattern that handles various formats AI might return
    # This regex is more forgiving about spacing, formatting and the Book X: prefix
    book_pattern = r"(?:Book\s*\d*:?\s*)?Name:\s*(.*?)[\r\n]+\s*Author:\s*(.*?)[\r\n]+\s*Genre:\s*(.*?)[\r\n]+\s*Price:\s*(.*?)[\r\n]+\s*ai_reasoning:\s*(.*?)[\r\n]+\s*(?:Amazon Link:)?.*?[\r\n]+\s*description:\s*(.*?)(?=(?:\s*(?:Book\s*\d*:?\s*)?Name:)|$)"
    
    # Find all matches
    matches = re.findall(book_pattern, response_text, re.DOTALL)
    
    # Debug the extraction
    print(f"Attempting to extract books from text with length {len(response_text)}")
    print(f"Found {len(matches)} book matches")
    
    if not matches:
        # Super flexible fallback pattern - capture any book-like structure
        fallback_pattern = r"(?:.*?)(?:name|title|book):\s*(.*?)[\r\n]+.*?(?:author|by|writer):\s*(.*?)[\r\n]+.*?(?:genre|category|type):\s*(.*?)[\r\n]+.*?(?:price|cost):\s*(.*?)[\r\n]+.*?(?:reason|why|recommendation):\s*(.*?)[\r\n]+.*?(?:description|about|summary):\s*(.*?)(?=(?:.*?(?:name|title|book):)|$)"
        matches = re.findall(fallback_pattern, response_text, re.DOTALL | re.IGNORECASE)
        
        print(f"Using fallback pattern, found {len(matches)} matches")
    
    for match in matches:
        if len(match) == 6:
            name, author, genre, price, ai_reasoning, description = [item.strip() for item in match]
            
            # Remove any questions from the description or ai_reasoning
            description = re.sub(r'Are these the kind of books you\'re looking for\?.*$', '', description).strip()
            ai_reasoning = re.sub(r'Are these the kind of books you\'re looking for\?.*$', '', ai_reasoning).strip()
            
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
