import streamlit as st
import pickle
import pandas as pd
import requests
import os

# Fetching poster from TMDb with error handling
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'
        )
        response.raise_for_status()  # Raise error for bad HTTP responses
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500/{data.get('poster_path', 'default-poster.jpg')}"  # Handle missing poster_path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return "default-poster.jpg"  # Fallback poster URL

# Recommending movies with validity checks
def recommend(movie):
    if movie not in movies['title'].values:
        st.error("Movie not found in the dataset.")
        return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Loading data with integrity check
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading pickle files: {e}")

# Streamlit page configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for Netflix-inspired design
st.markdown("""
    <style>
    body {
        background-color: #141414; /* Netflix black */
        color: white; /* Text in white */
    }
    .stSelectbox label {
        color: white; /* Label in white */
        font-size: 16px;
    }
    .stSelectbox select {
        background-color: #2c2c2c;
        color: white;
        border: 1px solid #E50914; /* Netflix red */
        border-radius: 5px;
        font-size: 16px;
    }
    .stButton > button {
        background-color: #E50914;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 8px 15px;
    }
    .stButton > button:hover {
        background-color: #f40612;
    }
    h1 {
        font-family: 'Arial', sans-serif;
        font-size: 2.5rem;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .stImage {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# App title
st.title('🎬 Movie Recommender System')

# Dropdown for selecting a movie
selected_movie_name = st.selectbox(
    "Type or select a movie from the dropdown:",
    movies['title'].values
)

# Button for recommendations
if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    # Displaying recommendations in columns
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.image(poster, use_container_width=True)  # Updated for deprecation
            st.write(f"**{name}**", unsafe_allow_html=True)
