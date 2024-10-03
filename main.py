import pandas as pd
import json
from sklearn.neighbors import NearestNeighbors
from collections import defaultdict
pd.options.mode.chained_assignment = None  # default='warn'
import streamlit as st
st.set_page_config(initial_sidebar_state='collapsed')

#st.write('Hello World')

# SETTING UP DATABASE FOR USE

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


# setting up a dictionary to hold each movies genres as well as rating
movie_dict = {}


# use iterrows to get specific information about each movie (cant index the row otherwise)
for i,row in df.iterrows():
    
    current_movie_title = row['title']
    
    # first store all of the genres in the dict
    movie_dict[current_movie_title] = row['genre']
    
    # then store the rating at the end of the array
    movie_dict[current_movie_title].append(row['rating'])




# IMPLEMENTING RECOMMENDATION ALGORITHM

#RECOMMENDATION ALGO IDEA

#- keep track of what movies the user has seen (can use a new dictionary or even just a list and can then index the dictionary)
#- based off of the movies they have seen should take their top 3 genres and recommend movies that have those genres (most first)
#- If there is a tie, take the movie with the highest rating
#- make sure we dont recommend a movie they have already seen


# will need to use a database to hold each users seen movies and favorite genres. Will use SQLite


# itially user will have to sign in and then will retreive their seen movies as well as their favorite genres


# create a set to hold the titles of movies that the user has seen (so they arent recommended again)
seen_movies = set()

# create a dictionary that keeps each genre and the amount of movies the user has seen with that genre
favorite_genres = dict()


# function that updates the seen_movies set and favorite_genres dict. Takes in a string of the movie title
def update_seen_movies(title: str) -> None:
    
    # add the movie to the seen_movies set
    seen_movies.add(title)
    
    # get all genres for the current title (the indexing ensures we dont get the last element which is the rating)
    for genre in movie_dict[title][:-1]:
        
        # increment the count of the current genre if it exists, if not set it to 0 and then increment
        favorite_genres[genre] = favorite_genres.get(genre, 0) + 1
    
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
        
        # check if movie hasnt already been seen
        if movie not in seen_movies:

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
    
    # convert the genres list to a string for better readability WILL DO LATER
    
    # return the resulting dataframe
    return df



# give title and heading to users
st.title("Movie Recommendations")
st.write('### Input Data')

# set up two columns for the inputs
col1, col2 = st.columns(2)

# get the user to choose the genres they enjoy
genres = col1.multiselect("Genres", ['Action', 'Fantasy','Science Fiction','Crime','Thriller','Action'])

# take genre list and place them into a dictionary (this is so recommendation algorithm still works properly)
genre_dict = dict()
for genre in genres:
    genre_dict[genre] = 1
    

# let user choose the number of recommendations they want
recommendation_amount = col2.number_input('Choose the number of recommendations', min_value=1, max_value=10)


# if the user presses the get recommendation button, display the database of recommendations
if st.button('Get recommendations'):
    movie_dataframe = recommend_movie(seen_movies,genre_dict,movie_dict,recommendation_amount)
    st.dataframe(movie_dataframe)
    