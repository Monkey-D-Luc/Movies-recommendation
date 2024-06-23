import streamlit as st
import pickle
import requests
import scipy.sparse as sp
from scipy.sparse import load_npz, csr_matrix
import time

page_bg_img = '''
<style>
.stApp {
    background-image: url("https://cdn.mos.cms.futurecdn.net/rDJegQJaCyGaYysj2g5XWY-650-80.jpg.webp");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

API_KEY = '5aa2b5080fc55bd63d3ba0ea80e2677a'
def fetch_poster(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        full_path = "https://via.placeholder.com/500x750?text=No+Image"
    return full_path
def get_info(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()
    def filter_names(dict_list):
        return [d['name'] for d in dict_list]
    genre = data.get('genres',[])
    title = data.get('title')
    overview = data.get('overview')
    genres = filter_names(genre)
    return {'title': title, 'overview': overview, 'genres': genres}

def recommend(movie, movies, similarity_matrix):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Không tìm thấy phim trong dữ liệu.")
        return [], [], []

    similarity_row = similarity_matrix[index, :]
    similarity_row = similarity_row.toarray().flatten()  # Convert to numpy array
    similar_indices = similarity_row.argsort()[::-1][1:11]  # Lấy 5 chỉ số phim tương tự

    movie_names = []
    movie_posters = []
    movie_ids =[]

    for idx in similar_indices:
        id = movies.iloc[idx].id
        movie_posters.append(fetch_poster(id))
        movie_ids.append(id)
        movie_names.append(movies.iloc[idx].title)

    return movie_names, movie_posters, movie_ids


st.header("Dự án gợi ý phim")

try:
    movies = pickle.load(open('Save/movies_list.pkl', 'rb'))
    similarity_matrix = load_npz('Save/similarity.npz')
except FileNotFoundError as e:
    st.error(f"Không tìm thấy tệp: {e}")
    st.stop()

movies_list = movies['title'].values
selected_movie = st.selectbox(
    'Nhập tên bộ phim để tìm kiếm các gợi ý tương tự',
    movies_list
)

if st.button('Hiển thị gợi ý'):
    movie_names, movie_posters, movie_ids = recommend(selected_movie, movies, similarity_matrix)
    if movie_names:
        cols= st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(movie_names[i])
                st.image(movie_posters[i])

                movie_info = get_info(movie_ids[i])
                st.write("Title:", movie_info['title'])
                st.write("Overview:", movie_info['overview'])
                st.write("Genres:", ', '.join(movie_info['genres']))
        cols = st.columns(5)

        for i in range(5, 10):
            with cols[i - 5]:
                st.text(movie_names[i])
                st.image(movie_posters[i])

                movie_info = get_info(movie_ids[i])
                st.write("Title:", movie_info['title'])
                st.write("Overview:", movie_info['overview'])
                st.write("Genres:", ', '.join(movie_info['genres']))