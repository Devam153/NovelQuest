import os
import re
import google.generativeai as genai
import time
import urllib.parse
import requests

def configure_genai(api_key):
    """Configure the Gemini API with the provided API key."""
    genai.configure(api_key=api_key)
    
def generate_amazon_in_link(book_title, author):
    """Generate a valid Amazon India search link for a book."""
    query = f"{book_title} {author} book"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.amazon.in/s?k={encoded_query}"

def fetch_cover_via_openlibrary(title, author):
    """
    Search OpenLibrary for title+author, grab the first cover_i or ISBN.
    """
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": title, "author": author, "limit": 1},
            timeout=5
        )
        data = resp.json()
        docs = data.get("docs", [])
        if not docs:
            return None

        doc = docs[0]
        # try cover_i
        if doc.get("cover_i"):
            cover_id = doc["cover_i"]
            return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        #fallback to ISBN
        if doc.get("isbn"):
            isbn = doc["isbn"][0]
            return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
    except Exception:
        pass
    return None

def get_book_recommendations(user_prompt, api_key, num_results=5, context=None):
    """Get book recommendations from Gemini API based on user prompt."""
    configure_genai(api_key)
    
    generation_config = {
        "temperature": 0.5,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,  
        "response_mime_type": "text/plain",
    }
    
    
    system_prompt = f"""You are an AI that recommends books. Your task is to suggest exactly {num_results} books that match the user's description **very closely**. 
    You will engage in a **conversation** with the user, refining recommendations based on their preferences. BUT In the end of ur answer do not ask any follow up questions that ai cahtbots generally ask for for better user experience i dont need that here okay so do not.
    
    For each book, provide the following information in this EXACT format (follow this format precisely):

    Name: <Book Name>
    Author: <Author>
    Genre: <Genre 1>, <Genre 2>, <Genre 3> (List all applicable genres as a comma-separated list)
    Price: <Approximate price in INR (Indian Rupees), e.g. ₹499>
    ai_reasoning: <Brief reasoning for recommending this book like why the user will like it make it atelast 25 words.>
    Amazon Link:
    description: <description of the book atleast 75 words for each.>

    Repeat the above format for all {num_results} books. Do not include any other text between book recommendations. Number them as Book 1, Book 2, etc.

    IMPORTANT: DO NOT include questions like "Are these the kind of books you're looking for?", "What do you think of these?", "Would you like me to refine the suggestions based on any specific preferences?", or similar conversational questions or follow-ups in your responses or in book descriptions. Simply provide the information in the format requested. for eg- 'What kind of thriller do you prefer? This will help me narrow down the suggestions.' JSUT GIVE ME THE DESCRIPTIONS DO NOT BE THE AI BOT AND ASK ANY FOLLOW UP QUESITON THAT YOU ARE PROGRAMMED TO ASK FOR.

    After listing all {num_results} books, you can continue the conversation by asking clarifying questions related to refining recommendations, but **only after** all book information is presented.
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
    
    # regex expression with only giving in the necessary details
    # It now looks for the start of the next book OR the end of the string,
    # ensuring it doesn't capture trailing conversational questions.
    book_pattern = r"(?:Book\s*\d*:?\s*)?Name:\s*(.*?)[\r\n]+\s*Author:\s*(.*?)[\r\n]+\s*Genre:\s*(.*?)[\r\n]+\s*Price:\s*(.*?)[\r\n]+\s*ai_reasoning:\s*(.*?)[\r\n]+\s*(?:Amazon Link:)?.*?[\r\n]+\s*description:\s*(.*?)(?=\s*(?:Book\s*\d*:?\s*)?Name:|\Z)"
    
    matches = re.findall(book_pattern, response_text, re.DOTALL)
    
    print(f"Attempting to extract books from text with length {len(response_text)}")
    print(f"Found {len(matches)} book matches with primary pattern")
    
    # try fallback.
    if not matches:
        fallback_pattern = r"(?:.*?)(?:name|title|book):\s*(.*?)[\r\n]+.*?(?:author|by|writer):\s*(.*?)[\r\n]+.*?(?:genre|category|type):\s*(.*?)[\r\n]+.*?(?:price|cost):\s*(.*?)[\r\n]+.*?(?:reason|why|recommendation):\s*(.*?)[\r\n]+.*?(?:description|about|summary):\s*(.*?)(?=(?:.*?(?:name|title|book):)|$)"
        matches = re.findall(fallback_pattern, response_text, re.DOTALL | re.IGNORECASE)
        print(f"Using fallback pattern, found {len(matches)} matches")
    
    # Define a regex to catch common  questions at the end of a string
    # This will be applied after extraction to fields that might contain them.
    conversational_question_pattern = r"\s*(?:What do you think of these\?|Are these the kind of books you're looking for\?|Would you like me to refine the suggestions based on any specific preferences\?).*$"

    for match in matches:
        if len(match) == 6:
            name, author, genre, price, ai_reasoning, description = [item.strip() for item in match]
            
            description = re.sub(conversational_question_pattern, '', description, flags=re.DOTALL).strip()
            ai_reasoning = re.sub(conversational_question_pattern, '', ai_reasoning, flags=re.DOTALL).strip()
            
            amazon_link = generate_amazon_in_link(name, author)
            cover_url = fetch_cover_via_openlibrary(name, author) or "https://i.imgur.com/YsaUJOQ.png"
            
            book = {
                "name": name,
                "author": author,
                "genre": genre,
                "price": price,
                "ai_reasoning": ai_reasoning,
                "amazon_link": amazon_link,
                "cover_url": cover_url,
                "description": description
            }
            
            books.append(book)
    
    return books