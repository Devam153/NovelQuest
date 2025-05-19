import streamlit as st
import os
import json
import re
from book_recommender import get_book_recommendations, extract_books_from_response
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="NovelQuest - Find Your Perfect Book",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state initialization
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'books' not in st.session_state:
    st.session_state.books = []
    
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

def main():
    # Sidebar
    with st.sidebar:
        st.image("https://i.imgur.com/8MmE3tY.png", width=100)
        st.title("NovelQuest")
        st.markdown("---")
        
        # API Key input
        api_key = st.text_input("Enter your Gemini API Key:", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            
        st.markdown("---")
        st.markdown("### Navigation")
        page = st.radio("", ["Home", "Book Search", "My Favorites", "About"])
        
        st.markdown("---")
        st.markdown("### Filters")
        min_pages = st.slider("Minimum Pages:", 0, 1000, 0)
        max_pages = st.slider("Maximum Pages:", 0, 1000, 1000)
        year_range = st.slider("Year Published:", 1800, 2023, (1800, 2023))
        genres = st.multiselect(
            "Genres:",
            ["Fiction", "Non-Fiction", "Fantasy", "Sci-Fi", "Mystery", "Romance", "Thriller", 
             "Historical", "Biography", "Young Adult", "Horror", "Adventure", "Classic"]
        )

    # Main content
    if page == "Home":
        display_home()
    elif page == "Book Search":
        display_book_search(api_key)
    elif page == "My Favorites":
        display_favorites()
    else:
        display_about()
    
    # Footer
    st.markdown("---")
    st.markdown("🔍 NovelQuest - Find your perfect book using AI | Made with ❤️ and Streamlit")

def display_home():
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("<h1 style='font-size:3.5em'>Find Your Perfect Book with NovelQuest</h1>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:1.5em; margin-bottom:2em;'>
        Stop wasting time on books that don't captivate you. Let our AI help you discover your next favorite read!
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### How NovelQuest Works:
        
        1. **Describe Your Perfect Book** - Share what kind of story, characters, or themes you're looking for.
        2. **AI Finds Your Match** - Our AI analyzes thousands of books to find perfect matches.
        3. **Discover & Enjoy** - Get personalized recommendations with all the details you need.
        """)
        
        get_started = st.button("Get Book Recommendations", use_container_width=True, key="get_started")
        if get_started:
            st.session_state.page = "Book Search"
            st.experimental_rerun()
    
    with col2:
        st.image("https://i.imgur.com/JlOJwF7.png", width=400)
    
    st.markdown("---")
    
    st.markdown("""
    ## Why NovelQuest?
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🔍 Beyond Simple Filters
        Find books based on themes, character types, plot specifics, and writing style - not just genres.
        """)
    
    with col2:
        st.markdown("""
        ### ⏱️ Save Time
        No more hours spent browsing through irrelevant books. Get curated recommendations in seconds.
        """)
    
    with col3:
        st.markdown("""
        ### 🌟 Discover Hidden Gems
        Find fantastic books that might not fit neatly into traditional categories but match your interests.
        """)

def display_book_search(api_key):
    st.markdown("<h1 style='text-align:center'>Find Your Next Great Read</h1>", unsafe_allow_html=True)
    st.write("Describe the perfect book you're looking for in detail. The more specific, the better!")
    
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
                # Get AI response
                response = get_book_recommendations(user_prompt, api_key)
                
                # Extract books from response
                books = extract_books_from_response(response)
                
                if books:
                    st.session_state.books = books
                    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
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

def display_favorites():
    st.markdown("<h1 style='text-align:center'>My Favorite Books</h1>", unsafe_allow_html=True)
    
    if not st.session_state.favorites:
        st.info("You haven't added any favorites yet. Explore book recommendations and click 'Add to Favorites' to see them here!")
        return
    
    # Display favorites in a nice grid
    for i, book in enumerate(st.session_state.favorites):
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.image("https://i.imgur.com/YsaUJOQ.png", width=100)
        
        with col2:
            st.markdown(f"### {book['name']}")
            st.markdown(f"**Author:** {book['author']}")
            st.markdown(f"**Genre:** {book['genre']}")
            
            if st.button("❌ Remove", key=f"remove_{i}"):
                st.session_state.favorites.pop(i)
                st.experimental_rerun()
        
        st.markdown("---")

def display_about():
    st.markdown("<h1 style='text-align:center'>About NovelQuest</h1>", unsafe_allow_html=True)
    
    st.write("""
    ## Our Mission
    
    NovelQuest was created to solve a common problem faced by book lovers: finding the perfect book that truly matches their interests and preferences.
    
    Many book readers face the challenge of finding the perfect book that aligns with their specific interests and preferences. Existing filters (like genres, authors, date) are helpful, but they often leave readers wanting more context about the book's content and themes.
    
    NovelQuest aims to create a more personalized and nuanced book recommendation experience, helping users discover books they will truly enjoy based on their specific interests.
    
    ## How We're Different
    
    - **Beyond Simple Categories**: We understand that your reading preferences are more complex than just "mystery" or "romance" - you might want a mystery with strong female characters, atmospheric settings, and no violence.
    
    - **AI-Powered Recommendations**: Our platform leverages advanced AI to understand the nuances of your preferences and match them with books that truly fit what you're looking for.
    
    - **Conversation-Based**: Unlike traditional search engines, NovelQuest allows you to have a conversation, refining your preferences as you go.
    
    ## Privacy
    
    NovelQuest values your privacy. We do not store your search queries or personal information beyond your current session.
    """)

if __name__ == "__main__":
    main()
