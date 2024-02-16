import pandas as pd
from scipy.spatial.distance import cosine


class RatingRecommender:
    def __init__(self, csv_file_path):
        '''
        An movie_based (item_based) system recommender
        '''
        self.movie_profiles = pd.read_csv(csv_file_path)
        self.movie_profiles.set_index('Movie_Title', inplace=True)

    @staticmethod
    def cosine_similarity(vec1, vec2):
        return 1 - cosine(vec1, vec2)

    def find_ratings(self, movies):
        # only find movies with ratings
        ratings = {}
        for movie in movies:
            if movie in self.movie_profiles.index:
                # Extract the average rating
                average_rating = self.movie_profiles.loc[movie, 'Average_Rating']
                ratings[movie] = average_rating
            #else:
             #   ratings[movie] = None
        return ratings

    def find_similar_movies(self, movies):
        similar_movies = {}
        for movie in movies:
            if movie in self.movie_profiles.index:
                # Extract the numeric columns for similarity calculation
                numeric_columns = self.movie_profiles.columns.drop('Average_Rating')
                selected_movie_profile = self.movie_profiles.loc[movie][numeric_columns].astype(float)

                # Calculate similarity with each movie in the dataset, excluding the selected movie
                similarities = self.movie_profiles[numeric_columns].astype(float).apply(
                    lambda row: self.cosine_similarity(selected_movie_profile, row), axis=1)
                similarities.drop(movie, inplace=True)

                # Find the movie with the highest similarity
                most_similar_movie = similarities.idxmax()
                similar_movie_rating = self.movie_profiles.loc[most_similar_movie, 'Average_Rating']
                similar_movies[movie] = (most_similar_movie, similar_movie_rating)
            #else:
                #similar_movies[movie] = (None, None)
        return similar_movies
