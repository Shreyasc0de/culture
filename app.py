import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from pathlib import Path
import pycountry
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import requests
from PIL import Image
import base64
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
import hashlib
import uuid

# Color Palette
COLORS = {
    "light": {
        "primary": "#FF8DC7",  # Soft pink
        "secondary": "#FFB3D1",  # Light pink
        "accent": "#FF69B4",  # Hot pink
        "background": "#FFF0F5",  # Lavender blush
        "text": "#4A4A4A",  # Dark gray
        "success": "#85D2B5",  # Mint green
        "card_bg": "#FFFFFF",  # White for cards
        "border": "#FFE4E1",  # Misty rose
    },
    "dark": {
        "primary": "#FF69B4",  # Hot pink
        "secondary": "#DB7093",  # Pale violet red
        "accent": "#FF1493",  # Deep pink
        "background": "#2F2F2F",  # Dark background
        "text": "#FFFFFF",  # White text
        "success": "#85D2B5",  # Mint green
        "card_bg": "#3D3D3D",  # Darker gray for cards
        "border": "#4A4A4A",  # Dark gray for borders
    }
}

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Custom CSS for theme
def get_theme_css():
    colors = COLORS[st.session_state.theme]
    return f"""
    <style>
        .stApp {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        .stButton>button {{
            background-color: {colors['primary']};
            color: white;
            border-radius: 20px;
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .stTextInput>div>div>input {{
            color: {colors['text']};
            border-radius: 10px;
        }}
        .stSelectBox>div>div>input {{
            color: {colors['text']};
        }}
        .feed-card {{
            background-color: {colors['card_bg']};
            padding: 20px;
            border-radius: 15px;
            border: 1px solid {colors['border']};
            margin: 10px 0;
            transition: all 0.3s ease;
        }}
        .feed-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }}
        .user-info {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .user-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        .timestamp {{
            color: {colors['text']};
            opacity: 0.7;
            font-size: 0.8em;
        }}
        .interaction-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }}
        .stTabs {{
            background-color: {colors['card_bg']};
            border-radius: 10px;
            padding: 10px;
        }}
    </style>
    """

# Load Lottie animation
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Set up page config
st.set_page_config(
    page_title="Culture Swap: Recipes & Stories",
    page_icon="👩‍🍳",
    layout="wide"
)

# Inject custom CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Create necessary directories
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
recipes_file = data_dir / "recipes.json"
stories_file = data_dir / "stories.json"
media_dir = data_dir / "media"
media_dir.mkdir(exist_ok=True)
users_file = data_dir / "users.json"

# Initialize or load users data
def load_users():
    if users_file.exists():
        with open(users_file, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(users_file, 'w') as f:
        json.dump(users, f)

users_db = load_users()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication functions
def register_user(username, password, email):
    if username in users_db:
        return False, "Username already exists"
    
    hashed_pwd = hash_password(password)
    users_db[username] = {
        "password": hashed_pwd,
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "id": str(uuid.uuid4())
    }
    save_users(users_db)
    return True, "Registration successful"

def login_user(username, password):
    if username not in users_db:
        return False, "Username not found"
    
    hashed_pwd = hash_password(password)
    if users_db[username]["password"] == hashed_pwd:
        st.session_state.authenticated = True
        st.session_state.current_user = username
        return True, "Login successful"
    return False, "Incorrect password"

def logout_user():
    st.session_state.authenticated = False
    st.session_state.current_user = None

# Authentication UI
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        colored_header(
            label="👩‍🍳 Culture Swap: Recipes & Stories",
            description="Share your family's culinary traditions and stories with the community.",
            color_name="red-70"
        )
        
        # Load welcome animation
        welcome_animation = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_UJNc2t.json")
        if welcome_animation:
            st_lottie(welcome_animation, height=200)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_submitted = st.form_submit_button("Login")
                
                if login_submitted:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                email = st.text_input("Email")
                register_submitted = st.form_submit_button("Register")
                
                if register_submitted:
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif not new_username or not new_password or not email:
                        st.error("Please fill all fields")
                    else:
                        success, message = register_user(new_username, new_password, email)
                        if success:
                            st.success(message)
                            st.info("Please login with your new account")
                        else:
                            st.error(message)

else:
    # Theme toggle in sidebar
    with st.sidebar:
        st.write(f"👤 Welcome, {st.session_state.current_user}!")
        st.write("🎨 Theme Settings")
        if st.button("Toggle Theme"):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()
        if st.button("Logout"):
            logout_user()
            st.rerun()

    # Header section with animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        colored_header(
            label="👩‍🍳 Culture Swap: Recipes & Stories",
            description="Share your family's culinary traditions and stories with the community.",
            color_name="red-70"
        )

    # Navigation with animations
    page = option_menu(
        menu_title=None,
        options=["Browse", "Add Recipe", "Add Story"],
        icons=["house", "book", "chat-square-text"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": COLORS[st.session_state.theme]['primary']},
            "icon": {"color": "white", "font-size": "25px"},
            "nav-link": {
                "font-size": "20px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": COLORS[st.session_state.theme]['secondary'],
            },
            "nav-link-selected": {"background-color": COLORS[st.session_state.theme]['secondary']},
        }
    )

    # Initialize session state
    if 'recipes' not in st.session_state:
        st.session_state.recipes = []
    
    if 'stories' not in st.session_state:
        st.session_state.stories = []

    # Load existing data
    def load_data():
        if recipes_file.exists():
            with open(recipes_file, 'r') as f:
                st.session_state.recipes = json.load(f)
        if stories_file.exists():
            with open(stories_file, 'r') as f:
                st.session_state.stories = json.load(f)

    # Save data
    def save_data():
        with open(recipes_file, 'w') as f:
            json.dump(st.session_state.recipes, f)
        with open(stories_file, 'w') as f:
            json.dump(st.session_state.stories, f)

    # Load existing data at startup
    load_data()

    # Get all countries for cultural tags
    CULTURE_TAGS = [country.name for country in pycountry.countries]
    MEAL_TAGS = ["Breakfast", "Lunch", "Dinner", "Dessert", "Snack", "Appetizer", "Beverage"]
    DIETARY_TAGS = ["Vegetarian", "Vegan", "Gluten-Free", "Kid-Friendly", "Dairy-Free", "Nut-Free", "Halal", "Kosher"]
    OCCASION_TAGS = ["Festival", "Wedding", "Birthday", "Holiday", "Everyday", "Religious", "Celebration"]
    SEASONS = ["Spring", "Summer", "Fall", "Winter"]

    def save_uploaded_file(uploaded_file):
        if uploaded_file is not None:
            file_path = media_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return str(file_path)
        return None

    if page == "Add Recipe":
        st.header("Share a Family Recipe")
        
        # Load cooking animation
        cooking_animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_tfb3estd.json")
        if cooking_animation:
            st_lottie(cooking_animation, height=200)
        
        with st.form("recipe_form"):
            title = st.text_input("Recipe Title")
            description = st.text_area("Description and Story Behind the Recipe")
            ingredients = st.text_area("Ingredients (one per line)")
            instructions = st.text_area("Cooking Instructions")
            
            # Media upload
            st.write("📸 Add Photos or Videos")
            uploaded_files = st.file_uploader("Upload media", type=["jpg", "jpeg", "png", "mp4"], accept_multiple_files=True)
            
            col1, col2 = st.columns(2)
            with col1:
                culture = st.multiselect("Cultural Origin", CULTURE_TAGS)
                meal_type = st.multiselect("Meal Type", MEAL_TAGS)
            with col2:
                dietary = st.multiselect("Dietary Tags", DIETARY_TAGS)
                season = st.multiselect("Best Season", SEASONS)
            
            submitted = st.form_submit_button("Share Recipe", use_container_width=True)
            
            if submitted and title and ingredients and instructions:
                media_paths = [save_uploaded_file(f) for f in uploaded_files] if uploaded_files else []
                
                recipe = {
                    "title": title,
                    "description": description,
                    "ingredients": ingredients.split("\n"),
                    "instructions": instructions,
                    "culture_tags": culture,
                    "meal_type": meal_type,
                    "dietary_tags": dietary,
                    "season": season,
                    "date_added": datetime.now().strftime("%Y-%m-%d"),
                    "hearts": 0,
                    "media": media_paths
                }
                st.session_state.recipes.append(recipe)
                save_data()
                st.success("Recipe shared successfully!")
                st.balloons()

    elif page == "Add Story":
        st.header("Share a Cultural Story")
        
        # Load storytelling animation
        story_animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_M9p23l.json")
        if story_animation:
            st_lottie(story_animation, height=200)
        
        with st.form("story_form"):
            title = st.text_input("Story Title")
            story = st.text_area("Your Story")
            
            # Media upload
            st.write("📸 Add Photos or Videos")
            uploaded_files = st.file_uploader("Upload media", type=["jpg", "jpeg", "png", "mp4"], accept_multiple_files=True)
            
            culture = st.multiselect("Cultural Tags", CULTURE_TAGS)
            occasion = st.multiselect("Occasion", OCCASION_TAGS)
            
            submitted = st.form_submit_button("Share Story", use_container_width=True)
            
            if submitted and title and story:
                media_paths = [save_uploaded_file(f) for f in uploaded_files] if uploaded_files else []
                
                story_entry = {
                    "title": title,
                    "story": story,
                    "culture_tags": culture,
                    "occasion": occasion,
                    "date_added": datetime.now().strftime("%Y-%m-%d"),
                    "hearts": 0,
                    "media": media_paths
                }
                st.session_state.stories.append(story_entry)
                save_data()
                st.success("Story shared successfully!")
                st.balloons()

    else:  # Browse page
        st.header("📱 Your Culture Feed")
        
        # Add story/recipe quick action buttons
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            quick_add = st.selectbox(
                "Share something...",
                ["What's on your mind?", "Share a Recipe", "Share a Story"],
                key="quick_add"
            )
            if quick_add != "What's on your mind?":
                if quick_add == "Share a Recipe":
                    st.switch_page("Add Recipe")
                else:
                    st.switch_page("Add Story")

        # Filters with animation
        with st.expander("🔍 Filter Your Feed", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_culture = st.multiselect("Culture", CULTURE_TAGS)
            with col2:
                filter_season = st.multiselect("Season", SEASONS)
            with col3:
                filter_dietary = st.multiselect("Dietary", DIETARY_TAGS)

        # Combined feed of recipes and stories
        all_content = []
        
        # Add recipes to content
        for recipe in st.session_state.recipes:
            all_content.append({
                "type": "recipe",
                "content": recipe,
                "date": datetime.strptime(recipe['date_added'], "%Y-%m-%d"),
                "author": recipe.get('author', 'Anonymous')
            })
        
        # Add stories to content
        for story in st.session_state.stories:
            all_content.append({
                "type": "story",
                "content": story,
                "date": datetime.strptime(story['date_added'], "%Y-%m-%d"),
                "author": story.get('author', 'Anonymous')
            })
        
        # Sort content by date
        all_content.sort(key=lambda x: x['date'], reverse=True)

        # Display feed
        for item in all_content:
            # Apply filters
            content = item['content']
            if ((filter_culture and not any(tag in content.get("culture_tags", []) for tag in filter_culture)) or
                (filter_season and not any(tag in content.get("season", []) for tag in filter_season)) or
                (filter_dietary and "dietary_tags" in content and not any(tag in content["dietary_tags"] for tag in filter_dietary))):
                continue

            st.markdown(f"""
                <div class="feed-card">
                    <div class="user-info">
                        <img src="https://api.dicebear.com/6.x/avataaars/svg?seed={item['author']}" class="user-avatar">
                        <div>
                            <strong>{item['author']}</strong><br>
                            <span class="timestamp">{item['date'].strftime('%B %d, %Y')}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.container():
                if item['type'] == 'recipe':
                    st.subheader(f"📖 {content['title']}")
                    st.write(content['description'])
                    
                    with st.expander("View Recipe Details"):
                        st.write("**Ingredients:**")
                        for ingredient in content['ingredients']:
                            st.write(f"• {ingredient}")
                        st.write("**Instructions:**")
                        st.write(content['instructions'])
                        
                        if content.get('media'):
                            media_cols = st.columns(len(content['media']))
                            for col, media_path in zip(media_cols, content['media']):
                                with col:
                                    if media_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                                        st.image(media_path)
                                    elif media_path.lower().endswith('.mp4'):
                                        st.video(media_path)
                else:  # Story
                    st.subheader(f"📚 {content['title']}")
                    st.write(content['story'])
                    
                    if content.get('media'):
                        media_cols = st.columns(len(content['media']))
                        for col, media_path in zip(media_cols, content['media']):
                            with col:
                                if media_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                                    st.image(media_path)
                                elif media_path.lower().endswith('.mp4'):
                                    st.video(media_path)

                # Tags and interactions
                st.markdown("---")
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    for tag in content.get('culture_tags', []):
                        st.badge(f"Culture: {tag}")
                    for tag in content.get('dietary_tags', []):
                        st.badge(f"Diet: {tag}")
                with cols[1]:
                    if st.button(f"❤️ {content['hearts']}", key=f"{item['type']}_{content['title']}"):
                        content['hearts'] += 1
                        save_data()
                        st.balloons()
                with cols[2]:
                    st.button("💬 Comment", key=f"comment_{item['type']}_{content['title']}") 