import streamlit as st
import pickle
import requests
import pandas as pd
from Recommend import fetch_poster

API_KEY = '5aa2b5080fc55bd63d3ba0ea80e2677a'


def get_item_based_recommendations(user_id, user_item_matrix, item_similarity_df, top_n=10):
    user_ratings = user_item_matrix.loc[user_id].dropna()
    user_ratings = user_ratings[user_ratings > 0]
    scores = {}
    for item, rating in user_ratings.items():
        similar_items = item_similarity_df[item].drop(item).sort_values(ascending=False)
        for similar_item, similarity in similar_items.items():
            if similar_item not in user_ratings.index:
                if similar_item not in scores:
                    scores[similar_item] = 0
                scores[similar_item] += similarity * rating
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    recommended_items = [item for item, score in sorted_scores[:top_n]]
    return recommended_items


def get_movie_details(movie_ids, top_n=10):
    movie_names = []
    movie_posters = []
    valid_movie_ids = []

    for movie_id in movie_ids:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url).json()
        title = data.get('title')
        movie_poster = fetch_poster(movie_id)

        # Kiểm tra nếu tiêu đề và poster hợp lệ
        if title and not movie_poster.endswith("No+Image"):
            movie_names.append(title)
            movie_posters.append(movie_poster)
            valid_movie_ids.append(movie_id)

        # Nếu đã có đủ số phim cần thiết thì dừng vòng lặp
        if len(movie_names) >= top_n:
            break

    # Nếu không đủ số phim cần thiết, thêm các phim từ danh sách gợi ý
    while len(movie_names) < top_n and len(movie_ids) > 0:
        movie_id = movie_ids.pop(0)
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url).json()
        title = data.get('title')
        movie_poster = fetch_poster(movie_id)

        # Kiểm tra nếu tiêu đề và poster hợp lệ
        if title and not movie_poster.endswith("No+Image"):
            movie_names.append(title)
            movie_posters.append(movie_poster)
            valid_movie_ids.append(movie_id)

    return movie_names[:top_n], movie_posters[:top_n], valid_movie_ids[:top_n]


def app():
    st.header("Gợi ý theo thông tin người dùng")
    try:
        rating = pd.read_csv('Save/ratings_small.csv')
        user_matrix = rating.pivot_table(index='userId', columns='movieId', values='rating')
        similar_matrix = pickle.load(open('Save/user.pkl', 'rb'))
    except FileNotFoundError as e:
        st.error(f"Không tìm thấy tệp: {e}")
        st.stop()

    user_list = list(range(1, 601))
    selected_user = st.selectbox(
        'Thông tin của người dùng',
        user_list
    )
    if st.button('Hiển thị gợi ý'):
        recommended_movie_ids = get_item_based_recommendations(selected_user, user_matrix, similar_matrix, top_n=10)
        movie_names, movie_posters, movie_ids = get_movie_details(recommended_movie_ids, top_n=10)

        if movie_names:
            cols = st.columns(5)
            for i in range(10):
                with cols[i % 5]:
                    st.text(movie_names[i])
                    st.image(movie_posters[i])


