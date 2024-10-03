import pandas as pd
import json
from sklearn.neighbors import NearestNeighbors
from collections import defaultdict
pd.options.mode.chained_assignment = None  # default='warn'
import streamlit as st

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


# setting up a dictionary to hold each movies information
movie_dict = {}

# for each movie want to store each genre and also its average rating
# will store in a dictionary where the last index in the list is the vote_average so can index using movie_dict[title][-1]


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


st.write()
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

# test out the function
#print(movie_dict)
#update_seen_movies('Avatar')
#update_seen_movies('Spectre')
#print(favorite_genres)


#If we give 5 recommended movies to the user perhaps, make the first three strongly matched on the 



def recommend_movie(seen_movies: set, favorite_genres: dict, movie_dict: dict, top_n: int) -> list:
    
    # sort the users top genres by using the number of genres and reversing it. And getting the top 3 genres
    # the lambda function is getting the pair of ('genre',count) and using the pair at index 1 to sort
    sorted_genres = sorted(favorite_genres.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # getting the top 3 preferred genres
    preferred_genres = [genre for genre,count in sorted_genres]
    
    
    # store the recommendations
    recommendations = []
    for movie,details in movie_dict.items():
        if movie not in seen_movies:
            # make sure movie hasnt been seen
            # get the genres and rating of the movie
            movie_genres = details[:-1]
            movie_rating = details[-1]
            
            
            # see if this movie matches the users preferred genres
            # use a point system to see how well of a match it actually is
            genre_overlap = sum(1 for genre in preferred_genres if genre in movie_genres)
            
            if genre_overlap > 0:
                recommendations.append((movie, movie_rating, genre_overlap, movie_genres))
    
    # sort the reccomendations based on the genre overlap firstly and then secondly rating
    recommendations = sorted(recommendations, key=lambda x: (x[2], x[1]), reverse=True)
    
    # return the top n recommendations
    return recommendations[:top_n]

#print(recommend_movie(seen_movies,favorite_genres,movie_dict,5))
            


# main function for GUI usage
def main():
    st.title("Movie Recommendations")

if __name__ == "__main__":
    main()