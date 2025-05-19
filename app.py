
import streamlit as st
import os
import json
import re
from book_recommender import get_book_recommendations, extract_books_from_response
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables and API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure page
st.set_page_config(
    page_title="NovelQuest - Find Your Perfect Book",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state initialization
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'books' not in st.session_state:
    st.session_state.books = []
    
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

def main():
    # Header
    st.image("https://i.imgur.com/8MmE3tY.png", width=100)
    st.title("NovelQuest")
    st.markdown("## Find Your Perfect Book")
    st.markdown("Stop wasting time on books that don't captivate you. Let our AI help you discover your next favorite read!")
    
    # Tabs for navigation
    tab1, tab2 = st.tabs(["Recommend", "About"])
    
    with tab1:
        # Main content 
        st.markdown("<h2 style='text-align:center'>Find Your Next Great Read</h2>", unsafe_allow_html=True)
        st.write("Describe the perfect book you're looking for in detail. The more specific, the better!")
        
        # Filters in a single row
        st.markdown("### Filters")
        col1, col2 = st.columns(2)
        
        with col1:
            page_range = st.select_slider(
                "Pages:",
                options=['100', '150', '200', '250', '300', '350', '400', '450', '500', '550', '600', '650', '700+'],
                value=('100', '700+')
            )
            
        with col2:
            year_range = st.slider("Year Published:", 1950, 2025, (1950, 2025))
        
        genres = st.multiselect(
            "Genres:",
            ["Fiction", "Non-Fiction", "Fantasy", "Sci-Fi", "Mystery", "Romance", "Thriller", 
             "Historical", "Biography", "Young Adult", "Horror", "Adventure", "Classic"]
        )
        
        # Book search form
        with st.form(key="book_search_form"):
            user_prompt = st.text_area(
                "What kind of book are you looking for?",
                height=150,
                placeholder="Example: I want a mystery book with a female detective who solves cold cases in a small town. I prefer books with witty dialogue and unexpected plot twists. I'd like it to be set in modern times."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button(label="Find Books", use_container_width=True)
            with col2:
                clear_button = st.form_submit_button(label="Clear Results", use_container_width=True)
        
        # Handle clear button
        if clear_button:
            st.session_state.chat_history = []
            st.session_state.books = []
        
        # Handle form submission
        if submit_button and user_prompt and api_key:
            with st.spinner("🔍 Searching for your perfect books..."):
                try:
                    # Add filters to prompt
                    filter_prompt = ""
                    if page_range != ('100', '700+'):
                        filter_prompt += f" The book should be between {page_range[0]} and {page_range[1]} pages."
                    
                    if year_range != (1950, 2025):
                        filter_prompt += f" The book should be published between {year_range[0]} and {year_range[1]}."
                    
                    if genres:
                        filter_prompt += f" The book should be in the following genres: {', '.join(genres)}."
                    
                    enhanced_prompt = user_prompt + filter_prompt
                    
                    # Get AI response
                    response = get_book_recommendations(enhanced_prompt, api_key)
                    
                    # Extract books from response
                    books = extract_books_from_response(response)
                    
                    if books:
                        st.session_state.books = books
                        st.session_state.chat_history.append({"role": "user", "content": enhanced_prompt})
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    else:
                        st.error("Sorry, I couldn't extract book recommendations from the AI response. Please try again with a different description.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        
        # Display books if available
        if st.session_state.books:
            st.markdown("## Your Personalized Book Recommendations")
            
            for i, book in enumerate(st.session_state.books):
                with st.expander(f"{i+1}. {book['name']} by {book['author']}", expanded=True):
                    cols = st.columns([1, 3])
                    
                    with cols[0]:
                        # Show a placeholder book cover
                        st.image("https://i.imgur.com/YsaUJOQ.png", width=150)
                        
                        # Add to favorites button
                        if st.button("❤️ Add to Favorites", key=f"fav_{i}"):
                            if book not in st.session_state.favorites:
                                st.session_state.favorites.append(book)
                                st.success(f"Added {book['name']} to favorites!")
                    
                    with cols[1]:
                        st.markdown(f"**Author:** {book['author']}")
                        st.markdown(f"**Genre:** {book['genre']}")
                        st.markdown(f"**Description:** {book['description']}")
                        st.markdown(f"**Why you'll like it:** {book['ai_reasoning']}")
                        
                        if 'amazon_link' in book and book['amazon_link']:
                            st.markdown(f"[Buy on Amazon]({book['amazon_link']})")
            
            # Continue conversation
            st.markdown("### Continue the Conversation")
            st.write("Not satisfied with these recommendations? Ask follow-up questions or refine your search!")
            
            followup_input = st.text_input("Your follow-up question:", key="followup")
            if st.button("Send", key="send_followup") and followup_input and api_key:
                with st.spinner("Getting more recommendations..."):
                    try:
                        # Create context from previous conversation
                        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
                        response = get_book_recommendations(followup_input, api_key, context)
                        
                        # Extract books from response
                        new_books = extract_books_from_response(response)
                        
                        if new_books:
                            st.session_state.books = new_books
                            st.session_state.chat_history.append({"role": "user", "content": followup_input})
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                            st.experimental_rerun()
                        else:
                            st.warning("I couldn't find new recommendations. Please try a different question.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    with tab2:
        st.markdown("<h2 style='text-align:center'>About NovelQuest</h2>", unsafe_allow_html=True)
        
        st.write("""
        ## Our Mission
        
        NovelQuest was created to solve a common problem faced by book lovers: finding the perfect book that truly matches their interests and preferences.
        
        Many book readers face the challenge of finding the perfect book that aligns with their specific interests and preferences. Existing filters (like genres, authors, date) are helpful, but they often leave readers wanting more context about the book's content and themes.
        
        NovelQuest aims to create a more personalized and nuanced book recommendation experience, helping users discover books they will truly enjoy based on their specific interests.
        
        ## How We're Different
        
        - **Beyond Simple Categories**: We understand that your reading preferences are more complex than just "mystery" or "romance" - you might want a mystery with strong female characters, atmospheric settings, and no violence.
        
        - **AI-Powered Recommendations**: Our platform leverages advanced AI to understand the nuances of your preferences and match them with books that truly fit what you're looking for.
        
        - **Conversation-Based**: Unlike traditional search engines, NovelQuest allows you to have a conversation, refining your preferences as you go.
        """)
        
        st.markdown("## How NovelQuest Works:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 1. Describe Your Perfect Book
            Share what kind of story, characters, or themes you're looking for in a book. The more details, the better!
            """)
        
        with col2:
            st.markdown("""
            ### 2. AI Finds Your Match
            Our advanced AI analyzes thousands of books to find perfect matches for your description.
            """)
        
        with col3:
            st.markdown("""
            ### 3. Discover & Enjoy
            Get personalized recommendations with all the details you need to find your next great read.
            """)
            
    # Footer
    st.markdown("---")
    st.markdown("🔍 NovelQuest - Find your perfect book using AI | Made with ❤️ and Streamlit")

if __name__ == "__main__":
    main()