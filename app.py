import streamlit as st
import os
import json
from book_recommender import get_book_recommendations, extract_books_from_response
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure page
st.set_page_config(
    page_title="NovelQuest - Find Your Perfect Book",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    st.markdown("<h1 style='margin-bottom: -30px; margin-top: -35px;'>NovelQuest</h1>", unsafe_allow_html=True)
    st.markdown("## Find Your Perfect Book")
    st.markdown("Stop wasting time on books that don't captivate you. Let our AI help you discover your next favorite read!")
    
    tab1, tab2 = st.tabs(["Recommender", "About"])
    
    with tab1:
        st.markdown("<h2>What book are you looking for?</h2>", unsafe_allow_html=True)
        st.write("Describe the perfect book you're looking for in detail. The more specific, the better!")
        
        # Filters header - more minimalist
        st.markdown("### Filters")
        
        # Put all filters in a single line with custom CSS class
        st.markdown('<div class="filter-row">', unsafe_allow_html=True)
        
        # Create columns for the filters in a single row
        filter_cols = st.columns(3)
        
        with filter_cols[0]:
            # Page range filter (single slider with predefined values)
            page_range = st.select_slider(
                "Number of Pages:",
                options=['100', '150', '200', '250', '300', '350', '400', '450', '500', '550', '600', '650', '700+'],
                value=('100', '700+')
            )
        
        with filter_cols[1]:
            # Publication year filter
            year_range = st.slider("Year Published:", 1950, 2025, (1950, 2025))
        
        with filter_cols[2]:
            # Number of results slider - clean minimalist style like reference
            num_results = st.slider(
                "Number of results:", 
                min_value=1, 
                max_value=10, 
                value=5, 
                step=1,
                key="number_results_slider"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Genre selection using a collapsible section
        with st.expander("Advanced Filters", expanded=False):
            st.markdown("#### Select Genres")
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
                height=120,
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
        
        # Display "Continue the Conversation" BEFORE book recommendations if books are available
        if st.session_state.books:
            # MOVED: Continue conversation section now appears before book recommendations
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
            
            # Display book recommendations AFTER the conversation section
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
                                st.subheader(book["name"]) # Option B: Escape Markdown by backticks TO PREVENT * ... *
                                
                                # Book details in a two-column layout
                                img_col, info_col = st.columns([1, 3], gap="small")
                                
                                with img_col:
                                    st.markdown(
                                        f"""
                                        <div style="
                                            width: 150px;    /* fixed display width */
                                            height: 225px;   /* fixed display height */
                                            overflow: hidden;
                                            margin-bottom: 15px;
                                        ">
                                            
                                        <img
                                            src="{book['cover_url']}"
                                            style="
                                            width: 150px;
                                            height: 225px;
                                            object-fit: cover;   /* crop & fill the box */
                                            display: block;
                                            "
                                            alt="Cover art for {book['name']}"
                                        />
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                
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
    
    with tab2:
        # About tab with minimalist style like the reference image
        st.markdown("<h2>About NovelQuest</h2>", unsafe_allow_html=True)
        st.markdown("""
        NovelQuest is an AI-powered book recommendation tool designed to help you find your next great read.
        
        **How it works:**
        1. Describe what kind of book you're looking for
        2. Add any specific preferences using the filters
        3. Get personalized recommendations tailored just for you
        
        **Why NovelQuest:**
        - Personalized recommendations based on your unique preferences
        - Discover books you might never have found otherwise
        - Save time searching through endless book reviews and lists
        
        This project uses Google's Gemini API to provide intelligent, context-aware book recommendations.
        """)
            
    # Footer
    st.markdown("---")
    st.markdown("🔍 NovelQuest - Find the book you would want to read | Made with ❤️ and Streamlit")

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
