import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval
from urllib.parse import quote

# Setting up the Streamlit page configuration
st.set_page_config(page_title="AnimeVerse Recommendation Bot", page_icon="🌸", layout="wide")
st.title("AnimeVerse Guide")

# Initialize session state variables
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "recommendations_shown" not in st.session_state:
    st.session_state.recommendations_shown = False
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper functions to update session state
def complete_setup():
    st.session_state.setup_complete = True

def show_recommendations():
    st.session_state.recommendations_shown = True

# Placeholder image functions
def get_anime_placeholder(title, genre=None, dimensions="300x450"):
    """Creates custom anime-themed placeholder images"""
    
    # Define color schemes based on genre
    genre_colors = {
        "action": "FF5733/FFFFFF",       # Orange background, white text
        "adventure": "FF9900/FFFFFF",    # Dark orange background, white text
        "romance": "FF9EF0/000000",      # Pink background, black text
        "comedy": "FFEC33/000000",       # Yellow background, black text
        "horror": "300030/FF0000",       # Dark purple background, red text
        "fantasy": "33A1FF/FFFFFF",      # Blue background, white text
        "sci-fi": "33FFB8/000000",       # Teal background, black text
        "slice of life": "B8FF33/000000", # Light green background, black text
        "sports": "FF3352/FFFFFF",       # Red background, white text
        "mecha": "8F8F8F/FFFF00",        # Gray background, yellow text
        "isekai": "9E33FF/FFFFFF",       # Purple background, white text
        "mystery": "000066/FFFFFF",      # Dark blue background, white text
        "psychological": "660066/FFFFFF", # Dark purple background, white text
        "drama": "006666/FFFFFF",        # Dark teal background, white text
        "supernatural": "663300/FFFFFF", # Brown background, white text
        "default": "3357FF/FFFFFF"       # Default blue background, white text
    }
    
    # Select color scheme based on genre
    colors = genre_colors.get(genre.lower() if genre else "default", genre_colors["default"])
    
    # Encode the title for URL
    encoded_title = quote(title)
    
    # Generate placeholder URL
    placeholder_url = f"https://via.placeholder.com/{dimensions}/{colors}?text={encoded_title}"
    
    return placeholder_url

def get_themed_placeholder(title, content_type="anime", genre=None):
    """Creates placeholders with different layouts based on content type"""
    
    encoded_title = quote(title)
    
    # Set appropriate emoji based on content type
    type_emoji = {
        "manga": "📚",
        "movie": "🎬",
        "light novel": "📘",
        "anime": "📺"
    }.get(content_type.lower(), "✨")
    
    # Get genre-specific colors
    genre_colors = {
        "action": "FF5733/FFFFFF",
        "romance": "FF9EF0/000000",
        "comedy": "FFEC33/000000",
        "horror": "300030/FF0000",
        "fantasy": "33A1FF/FFFFFF",
        "default": "3357FF/FFFFFF"
    }
    colors = genre_colors.get(genre.lower() if genre else "default", genre_colors["default"])
    
    # Adjust dimensions based on content type
    dimensions = {
        "manga": "350x500",
        "movie": "300x450",
        "light novel": "250x400",
        "anime": "300x450"
    }.get(content_type.lower(), "300x450")
    
    # Generate URL with type-specific emoji
    return f"https://via.placeholder.com/{dimensions}/{colors}?text={type_emoji}+{encoded_title}"

def create_anime_links(title):
    """Create formatted links to popular anime databases for a given title"""
    mal_link = f"https://myanimelist.net/search/all?q={quote(title)}"
    anilist_link = f"https://anilist.co/search/anime?search={quote(title)}"
    
    links_html = f"""
    <div style="margin-top: 10px; margin-bottom: 10px;">
        <a href="{mal_link}" target="_blank" style="text-decoration: none; padding: 5px 10px; background-color: #2E51A2; color: white; border-radius: 5px; margin-right: 10px;">
            MyAnimeList
        </a>
        <a href="{anilist_link}" target="_blank" style="text-decoration: none; padding: 5px 10px; background-color: #02A9FF; color: white; border-radius: 5px;">
            AniList
        </a>
    </div>
    """
    return links_html

def embed_youtube_trailer(anime_title):
    """Creates a YouTube search link for an anime trailer"""
    search_query = f"{anime_title} official trailer"
    youtube_search = f"https://www.youtube.com/results?search_query={quote(search_query)}"
    
    trailer_html = f"""
    <a href="{youtube_search}" target="_blank" style="text-decoration: none; padding: 5px 10px; background-color: #FF0000; color: white; border-radius: 5px; display: inline-block;">
        <span style="vertical-align: middle;">▶️ Watch Trailer</span>
    </a>
    """
    return trailer_html

def display_anime_card(title, genre=None, content_type="anime", description="", year=None, appeal=None):
    """Displays an enhanced anime recommendation card"""
    
    # Create columns for card layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display the placeholder image based on content type and genre
        placeholder_url = get_themed_placeholder(title, content_type, genre)
        st.image(placeholder_url, use_column_width=True)
    
    with col2:
        # Title with year if available
        if year:
            st.markdown(f"#### {title} ({year})")
        else:
            st.markdown(f"#### {title}")
        
        # Genre badge if available
        if genre:
            st.markdown(f"**Genre:** {genre.title()}")
        
        # Description
        if description:
            st.write(description)
        
        # Appeal/why they'll like it
        if appeal:
            st.markdown(f"**Why you'll enjoy it:** {appeal}")
        
        # External links
        st.markdown(create_anime_links(title), unsafe_allow_html=True)
        st.markdown(embed_youtube_trailer(title), unsafe_allow_html=True)

# Setup stage for collecting user preferences
if not st.session_state.setup_complete:
    st.subheader('Tell us about your anime & manga preferences')

    # Initialize session state for user preferences
    if "username" not in st.session_state:
        st.session_state["username"] = ""
    if "favorite_anime" not in st.session_state:
        st.session_state["favorite_anime"] = ""
    if "favorite_genres" not in st.session_state:
        st.session_state["favorite_genres"] = ""

    # Get user preference input
    st.session_state["username"] = st.text_input(label="Your Nickname", value=st.session_state["username"], placeholder="What should we call you?", max_chars=40)
    st.session_state["favorite_anime"] = st.text_area(label="Favorite Anime/Manga", value=st.session_state["favorite_anime"], placeholder="List some anime or manga you've enjoyed", max_chars=200)
    st.session_state["favorite_genres"] = st.text_area(label="Favorite Genres", value=st.session_state["favorite_genres"], placeholder="What genres do you enjoy? (e.g., shonen, slice of life, mecha)", max_chars=200)
    
    # Preferences Section
    st.subheader('Your Preferences')

    # Initialize session state for preferences
    if "experience_level" not in st.session_state:
        st.session_state["experience_level"] = "Beginner"
    if "content_type" not in st.session_state:
        st.session_state["content_type"] = "Both anime and manga"
    if "content_length" not in st.session_state:
        st.session_state["content_length"] = "No preference"

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["experience_level"] = st.radio(
            "Your anime/manga experience level",
            key="experience",
            options=["Beginner", "Intermediate", "Veteran Weeb"],
            index=["Beginner", "Intermediate", "Veteran Weeb"].index(st.session_state["experience_level"])
        )

    with col2:
        st.session_state["content_type"] = st.selectbox(
            "What are you looking for?",
            ("Both anime and manga", "Anime only", "Manga only", "Light novels", "Movies"),
            index=("Both anime and manga", "Anime only", "Manga only", "Light novels", "Movies").index(st.session_state["content_type"])
        )

    st.session_state["content_length"] = st.selectbox(
        "Preferred length",
        ("No preference", "Short (1-12 episodes/1-3 volumes)", "Medium (12-24 episodes/3-10 volumes)", "Long (24+ episodes/10+ volumes)", "Completed series only"),
        index=("No preference", "Short (1-12 episodes/1-3 volumes)", "Medium (12-24 episodes/3-10 volumes)", "Long (24+ episodes/10+ volumes)", "Completed series only").index(st.session_state["content_length"])
    )

    # Button to complete setup
    if st.button("Start Chatting", on_click=complete_setup):
        st.write("Profile complete. Let's find your next favorite anime or manga!")

# Chat phase
if st.session_state.setup_complete and not st.session_state.recommendations_shown and not st.session_state.chat_complete:

    st.info(
    """
    Tell AnimeVerse Guide what kind of stories you're in the mood for today!
    """,
    icon="✨",
    )

    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])

    # Setting OpenAI model if not already initialized
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # Initializing the system prompt for the chatbot
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system",
            "content": (f"You are AnimeVerse Guide, an enthusiastic and knowledgeable anime and manga recommendation assistant. "
                        f"You're helping {st.session_state['username']} find new anime and manga to enjoy. "
                        f"They enjoy {st.session_state['favorite_anime']} and prefer genres like {st.session_state['favorite_genres']}. "
                        f"Their experience level is {st.session_state['experience_level']}, they're looking for {st.session_state['content_type']}, "
                        f"and prefer {st.session_state['content_length']} content. "
                        f"Engage in a friendly conversation about anime and manga, using occasional Japanese terms (with translations), "
                        f"and references to popular anime. Ask about their preferences to provide personalized recommendations. "
                        f"Be enthusiastic but not overwhelming. Provide specific recommendations with brief descriptions. "
                        f"Avoid any inappropriate or adult-only content in your recommendations.")
        }]

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Handle user input and OpenAI response
    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your message", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

            # Increment the user message count
            st.session_state.user_message_count += 1

    # Check if the user message count reaches 5
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

# Show "Get Personalized Recommendations" 
if st.session_state.chat_complete and not st.session_state.recommendations_shown:
    if st.button("Get Personalized Recommendations", on_click=show_recommendations):
        st.write("Creating your personalized anime and manga list...")

# Show recommendations screen
if st.session_state.recommendations_shown:
    st.subheader("Your Personalized Recommendations")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    # Initialize new OpenAI client instance for recommendations
    recommendations_client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])

    # Generate recommendations using the stored messages
    recommendations_completion = recommendations_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are an anime and manga recommendation specialist.
             Based on the conversation, provide a personalized list of recommendations in JSON compatible format.
             For each recommendation include:
             - title: Full title of the anime/manga
             - year: Release year (if known)
             - genre: Primary genre (e.g., action, romance, fantasy)
             - content_type: Either "anime", "manga", "movie", or "light novel"
             - description: Brief description (1-2 sentences)
             - appeal: Why they'll love it based on their preferences
             
             Format your response with clear section headings and organize as follows:
             
             ## Overall Theme
             [Brief description of what you think the user will enjoy]
             
             ## Top Recommendations
             [List 5 recommendations with complete details for each]
             
             ## Hidden Gems
             [List 3 lesser-known recommendations with complete details for each]
             
             ## Where to Watch/Read
             [General information about legal platforms for anime/manga]
             """},
            {"role": "user", "content": f"Here's my conversation with AnimeVerse Guide. Please provide personalized recommendations based on this: {conversation_history}"}
        ]
    )

    # Get the recommendation text
    recommendation_text = recommendations_completion.choices[0].message.content
    
    # Display the Overall Theme section
    if "## Overall Theme" in recommendation_text:
        theme_parts = recommendation_text.split("## Overall Theme", 1)
        if len(theme_parts) > 1:
            theme_content = theme_parts[1].split("##")[0].strip()
            st.markdown("## Overall Theme")
            st.write(theme_content)
    
    # Display Top Recommendations with enhanced visualization
    if "## Top Recommendations" in recommendation_text:
        st.markdown("## Top Recommendations")
        
        # Parse and extract each recommendation
        top_rec_section = recommendation_text.split("## Top Recommendations", 1)[1].split("##")[0]
        top_recommendations = top_rec_section.strip().split("\n\n")
        
        for rec in top_recommendations:
            if not rec.strip():
                continue
                
            # Extract details from the recommendation text
            title = ""
            year = ""
            genre = ""
            content_type = "anime"  # default
            description = ""
            appeal = ""
            
            # Parse the information
            lines = rec.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. ") or line.startswith("4. ") or line.startswith("5. "):
                    # Extract title and possibly year from formats like "Title (2010)"
                    title_part = line[3:].strip()
                    if " - " in title_part:
                        title_part = title_part.split(" - ")[0].strip()
                    if " (" in title_part and ")" in title_part:
                        title = title_part.split(" (")[0].strip()
                        year = title_part.split(" (")[1].split(")")[0].strip()
                    else:
                        title = title_part
                
                if "genre:" in line.lower() or "genre" in line.lower():
                    genre = line.split(":", 1)[1].strip() if ":" in line else ""
                
                if "type:" in line.lower() or "content type:" in line.lower():
                    content_type = line.split(":", 1)[1].strip() if ":" in line else "anime"
                
                if "description:" in line.lower():
                    description = line.split(":", 1)[1].strip() if ":" in line else ""
                
                if "appeal:" in line.lower() or "why they'll love it:" in line.lower() or "why you'll love it:" in line.lower():
                    appeal = line.split(":", 1)[1].strip() if ":" in line else ""
            
            # If description wasn't explicitly labeled, use any remaining text
            if not description and len(lines) > 1:
                for line in lines[1:]:
                    if not line.lower().startswith(("genre:", "type:", "content type:", "appeal:", "why they'll love it:", "why you'll love it:")) and not line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                        description += line.strip() + " "
                description = description.strip()
            
            # Display the recommendation card
            display_anime_card(
                title=title,
                genre=genre,
                content_type=content_type,
                description=description,
                year=year,
                appeal=appeal
            )
            st.markdown("---")
    
    # Display Hidden Gems section
    if "## Hidden Gems" in recommendation_text:
        st.markdown("## Hidden Gems")
        
        # Parse and extract each hidden gem
        hidden_gems_section = recommendation_text.split("## Hidden Gems", 1)[1].split("##")[0]
        hidden_gems = hidden_gems_section.strip().split("\n\n")
        
        for rec in hidden_gems:
            if not rec.strip():
                continue
                
            # Extract details (similar to above)
            title = ""
            year = ""
            genre = ""
            content_type = "anime"  # default
            description = ""
            appeal = ""
            
            # Parse the information
            lines = rec.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. "):
                    # Extract title and possibly year
                    title_part = line[3:].strip()
                    if " - " in title_part:
                        title_part = title_part.split(" - ")[0].strip()
                    if " (" in title_part and ")" in title_part:
                        title = title_part.split(" (")[0].strip()
                        year = title_part.split(" (")[1].split(")")[0].strip()
                    else:
                        title = title_part
                
                if "genre:" in line.lower() or "genre" in line.lower():
                    genre = line.split(":", 1)[1].strip() if ":" in line else ""
                
                if "type:" in line.lower() or "content type:" in line.lower():
                    content_type = line.split(":", 1)[1].strip() if ":" in line else "anime"
                
                if "description:" in line.lower():
                    description = line.split(":", 1)[1].strip() if ":" in line else ""
                
                if "appeal:" in line.lower() or "why they'll love it:" in line.lower() or "why you'll love it:" in line.lower():
                    appeal = line.split(":", 1)[1].strip() if ":" in line else ""
            
            # If description wasn't explicitly labeled, use any remaining text
            if not description and len(lines) > 1:
                for line in lines[1:]:
                    if not line.lower().startswith(("genre:", "type:", "content type:", "appeal:", "why they'll love it:", "why you'll love it:")) and not line.strip().startswith(("1.", "2.", "3.")):
                        description += line.strip() + " "
                description = description.strip()
            
            # Display the recommendation card
            display_anime_card(
                title=title,
                genre=genre,
                content_type=content_type,
                description=description,
                year=year,
                appeal=appeal
            )
            st.markdown("---")
    
    # Display Where to Watch/Read section
    if "## Where to Watch/Read" in recommendation_text:
        st.markdown("## Where to Watch/Read")
        watch_read_section = recommendation_text.split("## Where to Watch/Read", 1)[1].strip()
        st.write(watch_read_section)
    
    # Button to start a new recommendation
    if st.button("Start Fresh", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")