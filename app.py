import pickle
import streamlit as st
import requests
from streamlit.components.v1 import html

# Cached function to fetch movie poster from TMDb API
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# Function to recommend movies based on similarity
@st.cache_data
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Custom CSS for enhanced UI and dark/light mode
def set_theme(is_dark_mode):
    if is_dark_mode:
        st.markdown("""
        <style>
        .stApp {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .css-1d391kg {
            background-color: #2a2a2a;
        }
        .stSelectbox, .stButton>button {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #444444;
        }
        .movie-card {
            background-color: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            text-align: center;
            height: 350px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .movie-title {
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
            height: 40px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            color: #ffffff !important;
        }
        .movie-poster {
            max-height: 250px;
            object-fit: cover;
            border-radius: 8px;
        }
        .header {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #ffffff;
        }
        .subheader {
            text-align: center;
            font-size: 18px;
            margin-bottom: 30px;
            color: #cccccc;
        }
        .toggle-container {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 20px;
        }
        .stMarkdown, .stText {
            color: #ffffff !important;
        }
        /* Style for selectbox placeholder and selected text */
        .stSelectbox [data-baseweb="select"] span, 
        .stSelectbox [data-baseweb="select"] div[role="combobox"] {
            color: #cccccc !important;  /* Light gray for placeholder and selected text in dark mode */
            font-size: 18px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
            color: #333333;
        }
        .css-1d391kg {
            background-color: #ffffff;
        }
        .stSelectbox, .stButton>button {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #e0e0e0;
        }
        .movie-card {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            height: 350px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .movie-title {
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
            height: 40px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            color: #333333 !important;
        }
        .movie-poster {
            max-height: 250px;
            object-fit: cover;
            border-radius: 8px;
        }
        .header {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333333;
        }
        .subheader {
            text-align: center;
            font-size: 18px;
            margin-bottom: 30px;
            color: #666666;
        }
        .toggle-container {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 20px;
        }
        .stMarkdown, .stText {
            color: #333333 !important;
        }
        /* Style for selectbox placeholder and selected text */
        .stSelectbox [data-baseweb="select"] span, 
        .stSelectbox [data-baseweb="select"] div[role="combobox"] {
            color: #666666 !important;  /* Dark gray for placeholder and selected text in light mode */
            font-size: 18px !important;
        }
        </style>
        """, unsafe_allow_html=True)

# Main app
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# Theme toggle
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
theme_switch = st.checkbox("Dark Mode", value=st.session_state.dark_mode, on_change=toggle_theme)
st.markdown('</div>', unsafe_allow_html=True)

# Apply theme
set_theme(st.session_state.dark_mode)

# Header and subheader
st.markdown('<div class="header">Movie Recommender System</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">By: Charoo K C</div>', unsafe_allow_html=True)

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list,
    placeholder="Choose a movie...",
    help="Select a movie to get recommendations"
)

# Show recommendations
if st.button('Show Recommendations', type="primary"):
    with st.spinner('Fetching recommendations...'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        st.markdown("### Recommended Movies")
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.markdown(
                    f'<div class="movie-card">'
                    f'<img src="{recommended_movie_posters[i]}" class="movie-poster">'
                    f'<div class="movie-title">{recommended_movie_names[i]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )