import streamlit as st
import requests
from scipy.sparse import load_npz
import pickle
API_KEY = '5aa2b5080fc55bd63d3ba0ea80e2677a'
@st.cache_data
def load_movies():
    movies = pickle.load(open('Save/movies_list.pkl', 'rb'))
    similarity_matrix = load_npz('Save/similarity.npz')
    return movies, similarity_matrix
def fetch_poster(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        full_path = "https://via.placeholder.com/500x750?text=No+Image"
    return full_path
# Hàm gợi ý các bộ phim tương tự
def recommend(movie, movies, similarity_matrix):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Không tìm thấy phim trong dữ liệu.")
        return [], [], []

    similarity_row = similarity_matrix[index, : ]
    similarity_row = similarity_row.toarray().flatten()
    similar_indices = similarity_row.argsort()[::-1][1:11]

    movie_names = []
    movie_posters = []
    movie_ids =[]

    for idx in similar_indices:
        id = movies.iloc[idx].id
        movie_posters.append(fetch_poster(id))
        movie_ids.append(id)
        movie_names.append(movies.iloc[idx].title)
    return movie_names, movie_posters, movie_ids

def main_page():
    st.header("Tìm kiếm phim tương ứng")
    movies, similarity_matrix = load_movies()
    movies_list = movies['title'].values
    query = st.text_input("Nhập tên phim:")
    filtered_movies = [movie for movie in movies_list if query.lower() in movie.lower()]
    selected_movie = st.selectbox(
        'Chọn phim từ kết quả tìm kiếm',
        filtered_movies
    )
    if st.button('Hiển thị gợi ý'):
        movie_names, movie_posters, movie_ids = recommend(selected_movie, movies, similarity_matrix)
        if movie_names:
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    st.text(movie_names[i])
                    st.image(movie_posters[i])
            cols = st.columns(5)
            for i in range(5, 10):
                with cols[i - 5]:
                    st.text(movie_names[i])
                    st.image(movie_posters[i])
