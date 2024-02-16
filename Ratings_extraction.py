import pandas as pd

# load the csv file
df = pd.read_csv('../user-comments.csv')

# Function to map ratings to new categories
def map_rating_to_category(rating):
    if rating in [1, 2]:
        return 1
    elif rating in [3, 4]:
        return 2
    elif rating in [5, 6]:
        return 3
    elif rating in [7, 8]:
        return 4
    elif rating in [9, 10]:
        return 5

# Apply the function to the Rating column
df['Rating_Category'] = df['rating'].apply(map_rating_to_category)

# calculate average rating
average_ratings = df.groupby('qid')['rating'].mean()

# calculate rating distribution
rating_counts = df.groupby(['qid','Rating_Category']).size().unstack(fill_value=0)
rating_distribution = rating_counts.div(rating_counts.sum(axis=1),axis=0)

# Combine average ratings and rating distribution into a single DataFrame
movie_profiles = pd.concat([average_ratings, rating_distribution], axis=1)
print(movie_profiles.shape[1])  # This prints the number of columns in movie_profiles

movie_profiles.columns = ['Average_Rating'] + [f'Category_{i}' for i in range(1, 5)]

# Save the movie profiles to a new CSV file
movie_profiles.to_csv('../movie_profiles.csv')

def get_movie_title(entity_id, graph):
    query_template = f'''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>
        SELECT ?movieTitle WHERE {{
            wd:{entity_id} rdfs:label ?movieTitle .
        }}
    '''
    result = graph.query(query_template)
    title = [str(row) for row, in result]
    return title[0] if title else None

# Load the CSV file
df = pd.read_csv('../movie_profiles.csv')

#####Transform qid to movie titles
df['qid'] = df['qid'].apply(lambda x: x.split('/')[-1])  # Extract entity ID from the URI
df['Movie_Title'] = df['qid'].apply(lambda qid: get_movie_title(qid, graph))


# Save the updated DataFrame
df.to_csv('../movie_profiles_with_titles.csv')

# Transform 'qid' to 'Movie_Title' and set it as the first column
df['Movie_Title'] = df['qid'].apply(lambda x: get_movie_title(x.split('/')[-1], graph))
df.drop('qid', axis=1, inplace=True)  # Drop the original 'qid' column
df = df[['Movie_Title'] + [col for col in df.columns if col != 'Movie_Title']]  # Reorder the columns

# Save the updated DataFrame
df.to_csv('../movie_profiles_titles.csv')
