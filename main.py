import pickle
import streamlit as st
import requests
import pandas as pd
import numpy as np

def fetch_poster(movie_title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key=42a9195ec4a5cee8666cdbed4702b83f&query={movie_title}"
        search_data = requests.get(search_url).json()
        results = search_data.get('results')
        if results:
            movie_id = results[0]['id']
            movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=42a9195ec4a5cee8666cdbed4702b83f&language=en-US"
            movie_data = requests.get(movie_details_url).json()
            poster_path = movie_data.get('poster_path')
            if poster_path:
                full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                return full_path
        return "https://via.placeholder.com/500"  # Placeholder image in case no poster is found
    except Exception as e:
        print(f"Error fetching poster for movie title {movie_title}: {e}")
        return "https://via.placeholder.com/500"  # Placeholder image in case of an error

# Load movies and similarity matrix
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))

# Extract movie titles
movies_list = movies['Series_Title'].values



def recommend(movie):
    index = movies[movies['Series_Title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommend_movie = []
    recommend_poster = []
    for i in distances[1:6]:
        movie_title = movies.iloc[i[0]].Series_Title
        recommend_movie.append(movie_title)
        recommend_poster.append(fetch_poster(movie_title))
    return recommend_movie, recommend_poster

# Function to recommend movies with ratings
def recommendWithRatings(user_ratings, movies, similarity, threshold=5, top_n=5):
    adjusted_similarities = np.zeros(similarity.shape[0])

    for movie, rating in user_ratings.items():
        if movie in movies['Series_Title'].values:
            index = movies[movies['Series_Title'] == movie].index[0]
            normalized_rating = rating - 5
            adjusted_similarities += similarity[index] * normalized_rating

    for movie, rating in user_ratings.items():
        if rating < threshold:
            index = movies[movies['Series_Title'] == movie].index[0]
            adjusted_similarities = np.where(similarity[index] < threshold, adjusted_similarities * 0.5, adjusted_similarities)

    recommended_indices = adjusted_similarities.argsort()[-top_n:][::-1]
    recommended_indices = [i for i in recommended_indices if movies.iloc[i].Series_Title not in user_ratings]

    recommended_movies = []
    recommended_posters = []

    for index in recommended_indices:
        recommended_movies.append(movies.iloc[index].Series_Title)
        recommended_posters.append(fetch_poster(movies.iloc[index].Series_Title))

    return recommended_movies, recommended_posters

# st.header("Film Wizard")
# selectvalue = st.selectbox("Select movies from dropdown", movies_list)

# if st.button("Show Recommend"):
#     movie_name, movie_poster = recommend(selectvalue)
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         st.text(movie_name[0])
#         st.image(movie_poster[0])
#     with col2:
#         st.text(movie_name[1])
#         st.image(movie_poster[1])
#     with col3:
#         st.text(movie_name[2])
#         st.image(movie_poster[2])
#     with col4:
#         st.text(movie_name[3])
#         st.image(movie_poster[3])
#     with col5:
#         st.text(movie_name[4])
#         st.image(movie_poster[4])

st.header("Rate Movies to Get Recommendations")

if 'user_ratings' not in st.session_state:
    st.session_state['user_ratings'] = {}

movie_to_rate = st.selectbox("Select a movie to rate", movies_list, key="movie_to_rate_selectbox")
rating = st.number_input("Rate the movie (1-10)", min_value=1, max_value=10, value=5, key="rating_input")

if st.button("Add Rating"):
    st.session_state['user_ratings'][movie_to_rate] = rating
    st.write(f"Added rating: {movie_to_rate} - {rating}")

if st.button("Get Recommendations Based on Ratings"):
    user_ratings = st.session_state['user_ratings']
    if user_ratings:
        recommended_movies, recommended_posters = recommendWithRatings(user_ratings, movies, similarity, threshold=5, top_n=5)
        st.write("Recommended Movies:")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(recommended_movies[0])
            st.image(recommended_posters[0])
        with col2:
            st.text(recommended_movies[1])
            st.image(recommended_posters[1])
        with col3:
            st.text(recommended_movies[2])
            st.image(recommended_posters[2])
        with col4:
            st.text(recommended_movies[3])
            st.image(recommended_posters[3])
        with col5:
            st.text(recommended_movies[4])
            st.image(recommended_posters[4])
    else:
        st.write("Please add at least one rating before getting recommendations.")