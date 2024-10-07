import pandas as pd
import json
import streamlit as st
import sqlite3


# config
pd.options.mode.chained_assignment = None  # default='warn'
#st.set_page_config(initial_sidebar_state='collapsed')

#
#
# SETTING UP DATABASE FOR USE
#
#


# retreiving the username from session state
if 'username' in st.session_state:
    username = st.session_state['username']

# set up selected movies session state variable
if 'selected_movies' not in st.session_state:
    st.session_state.selected_movies = []


# set up sqlite database for the username and their genres
conn = sqlite3.connect('movies.db',check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS movies (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        USERNAME TEXT(50), MOVIE_TITLE TEXT(50),
        UNIQUE(USERNAME, movie_title)
        )
    """
)
conn.commit()



# loading csv file with movies
movies_db = pd.read_csv('tmdb_5000_movies.csv')

# parse the database to be only the title, genres, and vote avg of the movies
df = movies_db[['title','genres','vote_average']]

# json extraction to get genre names from genres list
df.loc[:, 'genre'] = df['genres'].apply(lambda x: [genre['name'] for genre in json.loads(x)])

# getting rid of the genres column
df = df.drop('genres', axis=1)

# reformatting the database so it is easier to view
df = df[['title', 'genre', 'vote_average']]

# rename the vote_average Column to rating
df = df.rename(columns={'vote_average':'rating'})


# setting up a dictionary to hold each movies genres and rating as well as list with all movie names
movie_dict = {}
movie_names = []


# use iterrows to get specific information about each movie (cant index the row otherwise)
for i,row in df.iterrows():
    
    current_movie_title = row['title']
    movie_names.append(row['title'])
    
    # first store all of the genres in the dict
    movie_dict[current_movie_title] = row['genre']
    
    # then store the rating at the end of the array
    movie_dict[current_movie_title].append(row['rating'])


#
#
# IMPLEMENTING RECOMMENDATION ALGORITHM
#
#

# function that gets the seen movies from the database and updates the fav genres
def get_movies_update_genres() -> None:
    
    # get all movies with current username
    cursor.execute("SELECT MOVIE_TITLE FROM movies WHERE USERNAME = ?", (username,))
    seen = cursor.fetchall()
    
    # initializing seen_movies and favorite_genres
    st.session_state.seen_movies = set([movie[0] for movie in seen])  
    st.session_state.favorite_genres = dict()

    # populating favorite_genres
    for title in st.session_state.seen_movies:
        for genre in movie_dict[title][:-1]:
            st.session_state.favorite_genres[genre] = st.session_state.favorite_genres.get(genre, 0) + 1
    
    return None

# function to recommend n movies to the user based off of seen movies and fav genres
def recommend_movie(seen_movies: set, favorite_genres: dict, movie_dict: dict, top_n: int) -> list:
    
    # sort the users top genres by using the number of genres and reversing it. And getting the top 3 genres
    # the lambda function is getting the pair of ('genre',count) and using the pair at index 1 to sort
    sorted_genres = sorted(favorite_genres.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # getting all of the users preferred genres in order
    preferred_genres = [genre for genre,count in sorted_genres]
    
    # list to store recommendations
    recommendations = []
    
    # looping through all movie titles and their detials
    for movie,details in movie_dict.items():
        if movie not in st.session_state.seen_movies:

            # get the genres and rating of the movie
            movie_genres = details[:-1]
            movie_rating = details[-1]
            
            # sum the number of each genre that is in the preferred genre list thats also in the movie list
            genre_overlap = sum(1 for genre in preferred_genres if genre in movie_genres)
            
            # check if they have any matching genres and if so append movie to the list (game_overlap is so we can see how strong of a match it is)
            if genre_overlap > 0:
                recommendations.append((movie, movie_rating, genre_overlap, movie_genres))
    
    # sort the reccomendations based on the genre overlap firstly and then secondly rating
    recommendations = sorted(recommendations, key=lambda x: (x[2], x[1]), reverse=True)
    
    # get the top n recommendations 
    top_recommendations = recommendations[:top_n]
    
    # modify the data to get rid of the genre_overlap section
    modified_recommendations = [(title, rating, genres) for title,rating,_,genres in top_recommendations]
    
    # turn it into a dataframe to display onto the screen
    df = pd.DataFrame(modified_recommendations, columns=['Title','Rating','Genres'])
        
    # return the resulting dataframe
    return df


#
#
# RUNTIME FUNTIONALITY
#
#


# give title and heading to users
st.title("Movie Recommendations")
st.write('### Input Info')


# initializing seen_movies and favorite_genres after user signs in
if 'seen_movies' not in st.session_state and 'favorite_genres' not in st.session_state:
    get_movies_update_genres()


# populating the multiselect for movies
selected_movies = st.multiselect('Select new movies you have seen', options=[movie for movie in movie_names if movie not in st.session_state.seen_movies])

# updating database, seen_movies, and favorite_genres when user clicks update button
if st.button('update'):
    for movie in selected_movies:
        if movie not in st.session_state.seen_movies:
            cursor.execute("INSERT INTO movies (USERNAME, MOVIE_TITLE) VALUES (?,?)", (username,movie))
            conn.commit()
            st.session_state.seen_movies.add(movie)
            
            for genre in movie_dict[movie][:-1]:
                st.session_state.favorite_genres[genre] = st.session_state.favorite_genres.get(genre,0) + 1

# closing the database connection
conn.close()

# adding space
st.markdown('***')

# let user choose the number of recommendations they want
recommendation_amount = st.number_input('Choose the number of recommendations', min_value=1, max_value=10)


# if the user presses the get recommendation button, display the database of recommendations
if st.button('Get recommendations'):
    movie_dataframe = recommend_movie(st.session_state.seen_movies,st.session_state.favorite_genres,movie_dict,recommendation_amount)
    st.dataframe(movie_dataframe)
    