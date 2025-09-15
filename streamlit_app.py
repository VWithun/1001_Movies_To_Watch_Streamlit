import streamlit as st
import pandas as pd
from collections import Counter
import random

# --- Load CSV ---
df = pd.read_csv("movies_with_full_info_poster.csv")
df.rename(columns={"year": "Year"}, inplace=True)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Decade"] = (df["Year"] // 10 * 10).astype("Int64")
df['Genres'] = df['Genres'].fillna('')
df['Genres_list'] = df['Genres'].str.split(', ')

# --- Sidebar Filters ---
st.sidebar.header("🎬 Filter Movies")

# Multi-select genre
all_genres = sorted(set(g for lst in df['Genres_list'] for g in lst))
selected_genres = st.sidebar.multiselect("Select Genre(s)", all_genres)

# Decade filter
decades = sorted(df["Decade"].dropna().unique())
selected_decade = st.sidebar.selectbox("Select Decade", ["All"] + [str(d) for d in decades])

# Actor search
actor_search = st.sidebar.text_input("Search Actor")

# --- Filter the Data ---
filtered_df = df.copy()

if selected_genres:
    filtered_df = filtered_df[filtered_df['Genres_list'].apply(lambda lst: any(g in lst for g in selected_genres))]

if selected_decade != "All":
    filtered_df = filtered_df[filtered_df["Decade"] == int(selected_decade)]

if actor_search:
    filtered_df = filtered_df[filtered_df["Actors"].str.contains(actor_search, case=False, na=False)]

# --- Display ---
st.title("1001 Movies You Must See Before You Die 🎥")
url = "https://www.imdb.com/list/ls024863935/?view=compact&sort=alpha%2Casc"
st.markdown(f"Based on IMDb 1001 List: [🔗 Link]({url})")

st.write(f"Showing **{len(filtered_df)} movies**")
st.dataframe(filtered_df[['Title','Year','Genres','Actors','Director']])

# --- Statistics Section ---
st.subheader("📊 Movie Statistics")

# Most common actor
actors_list = df['Actors'].dropna().str.split(', ').sum()
actor_counts = Counter(actors_list)
top_actors = actor_counts.most_common(5)
st.write("**Top 5 actors appearing in most movies:**")
for actor, count in top_actors:
    st.write(f"- {actor}: {count} movies")

# Most common director
director_counts = df['Director'].value_counts().head(5)
st.write("**Top 5 directors with most movies:**")
st.bar_chart(director_counts)

# Genre counts
genre_counts = Counter(g for lst in df['Genres_list'] for g in lst)
genre_df = pd.DataFrame(genre_counts.items(), columns=['Genre','Count']).sort_values(by='Count', ascending=False)
st.write("**Most common genres overall:**")
st.dataframe(genre_df.style.format({'Count':'{:.0f}'}))

# Movies per decade
decade_counts = df['Decade'].value_counts().sort_index()
st.write("**Number of movies per decade:**")
st.bar_chart(decade_counts)

# --- Random Movie Picker ---
st.subheader("🎲 Can't decide what to watch?")
if st.button("Pick a Random Movie"):
    if filtered_df.empty:
        st.write("No movies match your filters. Try changing your selections.")
    else:
        movie = filtered_df.sample(1).iloc[0]

        st.write(f"**{movie['Title']} ({movie['Year']})**")
        st.write(f"Genres: {movie['Genres']}")
        st.write(f"Director: {movie['Director']}")
        st.write(f"Actors: {movie['Actors']}")

        # Plot / summary
        if 'Plot' in movie and movie['Plot']:
            st.write(f"**Plot:** {movie['Plot']}")

        # IMDb / OMDb URL
        if 'OMDb_URL' in movie and movie['OMDb_URL']:
            st.markdown(f"[🔗 IMDb / OMDb Link]({movie['OMDb_URL']})")

        # Poster image (smaller width, container width not used)
        if 'Poster_URL' in movie and movie['Poster_URL'] and movie['Poster_URL'] != "N/A":
            st.image(movie['Poster_URL'], width=250)
