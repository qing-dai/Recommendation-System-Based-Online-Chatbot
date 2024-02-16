import spacy
import spacy_transformers
import pandas as pd
from fuzzywuzzy import fuzz

# nlp = spacy.load('en_core_web_trf')
# nlp.enable_pipe("senter")  # Re-enable sentence segmentation if needed
movies_data = pd.read_csv('../movies.csv')
person_data = pd.read_csv('../person.csv')


class MovieTitleExtractor:
    '''
    Extract movies and person, support fuzzy search for both movies and persons
    '''
    def __init__(self, nlp):
        self.nlp = nlp

    def extract_entity(self, sentence):
        doc = self.nlp(sentence)
        movie = []
        for ent in doc.ents:
            if ent.label_ in ["WORK_OF_ART", 'DATE']:
                movie.append(ent)
        return movie

    def extract_per(self, sentence):
        doc = self.nlp(sentence)
        per = []
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                per.append(ent)
        return  per

    def fuzzy_input_movie(self, movies):
        movies_new = []
        for movie in movies:
            best_match = None
            best_score = 0
            for movie_0 in movies_data['Movie Name']:
                score = fuzz.ratio(movie, movie_0)
                if score > best_score:
                    best_score = score
                    best_match = movie_0
            movies_new.append(best_match)
        return movies_new


    def fuzzy_input_person(self, persons):
        person_new = []
        for person in persons:
            best_match = None
            best_score = 0
            for person_0 in person_data['Person_Name']:
                score = fuzz.ratio(person, person_0)
                if score > best_score:
                    best_score = score
                    best_match = person_0
            person_new.append(best_match)
        return person_new


# if __name__ == '__main__':
#     #sentence = "Who is the screenwriter of The Masked Gang: Cyprus?"
#     s1 = "When was 'The Godfather' released? "
#     #s1 = "Let me know what sandra Bullock and Julia Roberts looks like. "
#     #s2 = "Given that I like The Lion King, Pocahontas, and The Beauty and the Beast, can you recommend some movies?"
#  #   s3 = "Recommend movies like Nightmare on Elm Street, Friday the 13th, and Halloween."
#     me = MovieTitleExtractor(nlp)
#     res = me.extract_entity(s1)
#     #res = me.extract_per(s1)
#     print(res)
#     #persons = me.fuzzy_input_person(res)
#     #print(persons)
#     movie = me.fuzzy_input_movie(res)
#     print(movie)
