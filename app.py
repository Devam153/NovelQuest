import streamlit as st
import os
import json
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

# Define genre options
genre_options = [
    "Fiction", "Non-Fiction", "Fantasy", "Science Fiction", "Mystery", 
    "Romance", "Thriller", "Historical Fiction", "Biography", 
    "Young Adult", "Horror", "Adventure", "Classics", "Literary Fiction",
    "Poetry", "Self-Help", "Psychological Thriller", "Suspense", "Comedy",
    "Drama", "Satire", "Memoir", "Crime", "Action", "Philosophy"
]

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
        
        # Filters
        st.markdown("### Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Page range filter (single slider with predefined values)
            page_range = st.select_slider(
                "Pages:",
                options=['100', '150', '200', '250', '300', '350', '400', '450', '500', '550', '600', '650', '700+'],
                value=('100', '700+')
            )
        
        with col2:
            # Publication year filter
            year_range = st.slider("Year Published:", 1950, 2025, (1950, 2025))
        
        # Number of results slider
        num_results = st.slider("Number of results:", min_value=1, max_value=10, value=5, step=1)
        
        # Genre selection using a collapsible section
        with st.expander("Select Genres (check all that apply)", expanded=False):
            # Create a 5-column layout for genres
            genre_cols = st.columns(5)
            selected_genres = []
            
            # Distribute genres across the columns
            for i, genre in enumerate(genre_options):
                col_index = i % 5
                with genre_cols[col_index]:
                    if st.checkbox(genre, key=f"genre_{genre}"):
                        selected_genres.append(genre)
        
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
                    
                    if selected_genres:
                        filter_prompt += f" The book should be in one or more of these genres: {', '.join(selected_genres)}."
                    
                    enhanced_prompt = user_prompt + filter_prompt
                    
                    # Get AI response with specified number of results
                    response = get_book_recommendations(enhanced_prompt, api_key, num_results=num_results)
                    
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
                    if "429" in str(e):
                        st.warning("You've reached the API rate limit. Please try again in a few minutes or check your Gemini API quota at https://ai.google.dev/")
        
        # Display books in an improved layout if available
        if st.session_state.books:
            st.markdown("## Your Personalized Book Recommendations")
            
            # Calculate number of columns (2 for desktop view)
            cols_per_row = 2
            
            # Create rows of books
            for i in range(0, len(st.session_state.books), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j in range(cols_per_row):
                    idx = i + j
                    if idx < len(st.session_state.books):
                        book = st.session_state.books[idx]
                        with cols[j]:
                            with st.container(border=True):
                                st.markdown(f"### {book['name']}")
                                
                                # Book details in a two-column layout
                                img_col, info_col = st.columns([1, 2])
                                
                                with img_col:
                                    # Show a placeholder book cover
                                    st.image("https://i.imgur.com/YsaUJOQ.png", width=150)
                                
                                with info_col:
                                    st.markdown(f"**Author:** {book['author']}")
                                    st.markdown(f"**Genre:** {book['genre']}")
                                    st.markdown(f"**Price:** {book.get('price', '₹499')}")
                                
                                # Description and reasoning in a single column
                                with st.expander("Description & Details", expanded=False):
                                    st.markdown(f"**Description:** {book['description']}")
                                    st.markdown(f"**Why you'll like it:** {book['ai_reasoning']}")
                                
                                # Amazon link (now using Amazon.in)
                                if 'amazon_link' in book and book['amazon_link']:
                                    st.markdown(f"[Buy on Amazon India]({book['amazon_link']})")
            
            # Continue conversation section
            st.markdown("### Continue the Conversation")
            st.write("Not satisfied with these recommendations? Ask follow-up questions or refine your search!")
            
            followup_input = st.text_input("Your follow-up question:", key="followup")
            if st.button("Send", key="send_followup") and followup_input and api_key:
                with st.spinner("Getting more recommendations..."):
                    try:
                        # Create context from previous conversation
                        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
                        response = get_book_recommendations(followup_input, api_key, num_results=num_results, context=context)
                        
                        # Extract books from response
                        new_books = extract_books_from_response(response)
                        
                        if new_books:
                            st.session_state.books = new_books
                            st.session_state.chat_history.append({"role": "user", "content": followup_input})
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                            # Proper rerun
                            st.rerun()
                        else:
                            st.warning("I couldn't find new recommendations. Please try a different question.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        if "429" in str(e):
                            st.warning("You've reached the API rate limit. Please try again in a few minutes.")
    
    with tab2:
        # ... keep existing code (About tab content)
            
    # Footer
        st.markdown("---")
        st.markdown("🔍 NovelQuest - Find your perfect book using AI | Made with ❤️ and Streamlit")

if __name__ == "__main__":
    if not api_key or api_key == "your_api_key_here":
        st.error("⚠️ Gemini API key not found. Please add your API key to the .env file.")
        st.code("""
# In your .env file:
GEMINI_API_KEY=your_actual_api_key_here
        """)
        st.markdown("Get your API key from [Google AI Studio](https://ai.google.dev/)")
    else:
        main()