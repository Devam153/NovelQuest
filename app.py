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

# Define CSS directly in the app
css = """
/* Custom font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Global styles */
* {
    font-family: 'Poppins', sans-serif;
}

/* Light mode theme (default) */
body {
    background-color: #f8f8f8;
    color: #333333;
}

/* Main container styling */
.main {
    padding: 2rem 3rem;
    background-color: #ffffff;
}

/* Header styling */
h1, h2, h3 {
    color: #9b87f5; /* Purple accent */
}

/* Button styling */
.stButton > button {
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    background-color: #9b87f5;
    color: #ffffff;
}

.stButton > button:hover {
    background-color: #7E69AB;
    box-shadow: none;
    transform: none;
}

/* Form styling */
.stTextArea, .stTextInput {
    border-radius: 8px;
}

.stTextArea > div, .stTextInput > div {
    border: 1px solid #d1d1d1;
    background-color: #ffffff;
}

.stTextArea > div:focus, .stTextInput > div:focus {
    border: 1px solid #9b87f5;
}

/* Card styling */
[data-testid="stExpander"] {
    border-radius: 10px;
    border: 1px solid #e5e5e5;
    margin-bottom: 1rem;
    overflow: hidden;
    transition: all 0.3s ease;
    background-color: #ffffff;
}

[data-testid="stExpander"]:hover {
    box-shadow: none;
    transform: none;
}

/* Slider styling - fixed to avoid highlighting issues */
.stSlider > div > div > div {
    background-color: #9b87f5 !important;
}

/* Remove selection highlight from slider values */
.stSlider [role="slider"] {
    background-color: #9b87f5 !important;
    box-shadow: none !important;
    outline: none !important;
    border: none !important;
}

.stSlider [role="slider"]:focus,
.stSlider [role="slider"]:active,
.stSlider [role="slider"]:hover {
    box-shadow: none !important;
    outline: none !important;
    border: none !important;
}

/* Fix highlighting on slider thumb */
.streamlit-slider .thumb {
    background-color: #9b87f5 !important;
    border: none !important;
    box-shadow: none !important;
}

.streamlit-slider .track {
    background-color: rgba(155, 135, 245, 0.3) !important;
}

/* Remove selection highlight */
.streamlit-slider .thumb:focus,
.streamlit-slider .thumb:active,
.streamlit-slider .thumb:hover {
    box-shadow: none !important;
    outline: none !important;
    border: none !important;
}

/* Year slider specific fixes */
[data-testid="stSlider"] [data-baseweb="slider"] {
    background-color: #ffffff !important;
}

[data-testid="stSlider"] [data-baseweb="thumb"] {
    background-color: #9b87f5 !important;
    border-color: #9b87f5 !important;
    box-shadow: none !important;
}

/* Book card styling */
[data-testid="container"] {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    border: 1px solid #e0e0e0;
}

[data-testid="container"]:hover {
    box-shadow: none;
    transform: none;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    background-color: #ffffff;
}

.stTabs [data-baseweb="tab"] {
    height: 4rem;
    white-space: pre-wrap;
    border-radius: 4px 4px 0 0;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    font-weight: 600;
    color: #555555;
    background-color: #f3f3f3;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(155, 135, 245, 0.1) !important;
    color: #9b87f5 !important;
}

/* Checkbox styling */
.stCheckbox label {
    color: #333333;
}

.stCheckbox [data-testid="stMarkdownContainer"] p {
    font-size: 0.9rem;
}

/* Footer styling */
footer {
    text-align: center;
    margin-top: 3rem;
    color: #6b7280;
}

/* Links */
a {
    color: #9b87f5 !important;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Book cards grid */
.book-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    background-color: #ffffff;
}

.book-card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    border: 1px solid #e0e0e0;
}

.book-card:hover {
    box-shadow: none;
    transform: none;
}

/* Dropdown - make it look better */
.stSelectbox {
    background-color: #ffffff;
}

.stSelectbox > div > div {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
}

/* Fix for the select genres dropdown */
[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border-color: #d1d1d1;
}

/* Override Streamlit's default dark theme elements */
.stApp {
    background-color: #f8f8f8 !important;
}

.stApp [data-testid="stAppViewContainer"] {
    background-color: #f8f8f8 !important;
}

/* Make sure all text is readable */
p, h1, h2, h3, h4, h5, h6, span, label, div {
    color: #333333;
}

/* Override slider track colors */
.stSlider [data-baseweb="track"] {
    background-color: rgba(155, 135, 245, 0.3) !important;
}

.stSlider [data-baseweb="tick"] {
    background-color: #9b87f5 !important;
}

/* Fix slider year labels */
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #333333 !important;
}

/* Put filters in a single horizontal line */
.filter-row {
    display: flex !important;
    flex-direction: row !important;
    gap: 2rem !important;
    align-items: center !important;
    width: 100% !important;
    margin-bottom: 1rem !important;
}

.filter-row > div {
    min-width: 0 !important;
    flex: 1 !important;
}

/* Number of results slider - clean minimalist style */
.number-results-slider {
    padding: 0 !important;
    margin: 0 !important;
}

.number-results-slider [data-testid="stSliderNumbers"] {
    display: flex !important;
    justify-content: space-between !important;
}

/* Fix selections being highlighted */
::selection {
    background-color: rgba(155, 135, 245, 0.2) !important;
}

/* Responsive design adjustments */
@media (max-width: 768px) {
    .main {
        padding: 1rem;
    }
    
    h1 {
        font-size: 1.8rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
    }
}

/* Fix background colors for interactive elements */
[data-testid="stForm"] {
    background-color: #ffffff !important;
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid #e5e5e5;
}
"""

# Apply the CSS
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

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
    
    # Tabs for navigation - minimal style like reference image
    tab1, tab2 = st.tabs(["Recommend", "About"])
    
    with tab1:
        # Main content 
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
                "Pages:",
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