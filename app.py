import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="IMDB Top 250 Movies Analysis", layout="wide")

# ----------------- Data Loading -----------------
@st.cache_data
def load_data():
    df = pd.read_csv('movie_ratings.csv')

    def clean_currency(val):
        if pd.isna(val):
            return None
        cleaned = re.sub(r'[^\d.]', '', str(val))
        try:
            return float(cleaned)
        except:
            return None

    df['budget_clean'] = df['budget'].apply(clean_currency)
    df['box_office_clean'] = df['box_office'].apply(clean_currency)
    return df

df = load_data()

# ----------------- Sidebar Filters -----------------
st.sidebar.header("Filter Movies")
year_range = st.sidebar.slider("Select Year Range", int(df['year'].min()), int(df['year'].max()), (2000, 2025))
genres = st.sidebar.multiselect("Select Genre(s)", options=df['genre'].dropna().unique())
certificate = st.sidebar.selectbox("Select Certificate", options=['All'] + list(df['certificate'].dropna().unique()))

filtered_df = df[
    (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])
]

if genres:
    filtered_df = filtered_df[filtered_df['genre'].str.contains('|'.join(genres), case=False, na=False)]

if certificate != 'All':
    filtered_df = filtered_df[filtered_df['certificate'] == certificate]

# ----------------- Main Section -----------------
st.title("🎬 IMDB Top 250 Movies Analysis Dashboard")

st.subheader(f"🎯 Showing {len(filtered_df)} Movies Based on Your Filters")
st.dataframe(filtered_df[['rank', 'name', 'year', 'rating', 'genre', 'certificate']])

# ----------------- Top Movies -----------------
st.subheader("⭐ Top 5 Highest Rated Movies")
st.dataframe(filtered_df.sort_values(by='rating', ascending=False).head(5)[['name', 'year', 'rating']])

st.subheader("💰 Top 5 Highest Box Office Collection Movies")
st.dataframe(filtered_df.sort_values(by='box_office_clean', ascending=False).head(5)[['name', 'year', 'box_office']])

# ----------------- Directors -----------------
st.subheader("🎥 Top 10 Directors with Most Movies in Top 250")
top_directors = df['directors'].value_counts().head(10)
st.bar_chart(top_directors)


# ----------------- Highest Rated per Genre -----------------
if genres:
    st.subheader("🎬 Highest Rated Movie in Selected Genre(s)")
    highest_rated_genre = filtered_df.loc[filtered_df.groupby('genre')['rating'].idxmax()][['genre', 'name', 'rating']]
    st.dataframe(highest_rated_genre)

# ----------------- Movie Details Viewer -----------------
st.subheader("🔎 Movie Details Viewer")
if not filtered_df.empty:
    selected_movie = st.selectbox("Select a Movie", options=filtered_df['name'].unique())
    if selected_movie:
        movie_details = df[df['name'] == selected_movie].iloc[0]
        st.markdown(f"""
        **Name:** {movie_details['name']}  
        **Year:** {movie_details['year']}  
        **Rating:** {movie_details['rating']}  
        **Genre:** {movie_details['genre']}  
        **Certificate:** {movie_details['certificate']}  
        **Runtime:** {movie_details['run_time']}  
        **Tagline:** {movie_details['tagline']}  
        **Budget:** {movie_details['budget']}  
        **Box Office:** {movie_details['box_office']}  
        **Directors:** {movie_details['directors']}  
        **Writers:** {movie_details['writers']}  
        **Casts:** {movie_details['casts']}  
        """)
else:
    st.info("No movies match your filter criteria.")
