from speakeasypy import Speakeasy, Chatroom
import json

import numpy as np
import rdflib
from typing import List
import time
import csv
import spacy
import pandas as pd
import html
from fuzzywuzzy import fuzz

from Movie_title import MovieTitleExtractor
from rating_recommender import RatingRecommender
from relation_extraction import MoviePropertyExtractor
from use_embeddings import Embeddings
from KG_query import KnowledgeGraph
from image_extraction import ImageExtraction
from crowd import Crowd


# add prefix
wd = rdflib.Namespace('http://www.wikidata.org/entity/')
wdt = rdflib.Namespace('http://www.wikidata.org/prop/direct/')
ddis = rdflib.Namespace('http://ddis.ch/atai/')
RDFS = rdflib.namespace.RDFS
SCHEMA = rdflib.Namespace('http://schema.org/')

# host_url
DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2

# initialize json items
with open('../preprocessed_file.json','r') as file:
    items = json.load(file)

# Introduce nlp model for NER and movies.csv for fuzz match
nlp = spacy.load('en_core_web_trf')
#movies_data = pd.read_csv('../movies.csv')

# load knowledge graph
graph = rdflib.Graph().parse(source='./14_graph.nt', format='turtle')

# json
#filename = '../images.json'

# load pipelines for ner, relation, embeddings , rating_recommender and imageExtraction
title_extractor = MovieTitleExtractor(nlp)
property_extractor = MoviePropertyExtractor()
embeddings = Embeddings()
rating_recommender = RatingRecommender("../movie_profiles_titles_modified.csv")
kg = KnowledgeGraph()
crowd = Crowd()

img_extractor = ImageExtraction()

# Load the embeddings and dictionaries
entity_emb = np.load('../ddis-graph-embeddings/entity_embeds.npy')
relation_emb = np.load('../ddis-graph-embeddings/relation_embeds.npy')
RDFS = rdflib.namespace.RDFS

with open('../ddis-graph-embeddings/entity_ids.del', 'r') as ifile:
    ent2id = {rdflib.term.URIRef(ent): int(idx) for idx, ent in csv.reader(ifile, delimiter='\t')}
    id2ent = {v: k for k, v in ent2id.items()}

with open('../ddis-graph-embeddings/relation_ids.del', 'r') as ifile:
    rel2id = {rdflib.term.URIRef(rel): int(idx) for idx, rel in csv.reader(ifile, delimiter='\t')}
    id2rel = {v: k for k, v in rel2id.items()}

ent2lbl = {ent: str(lbl) for ent, lbl in graph.subject_objects(RDFS.label)}
lbl2ent = {lbl: ent for ent, lbl in ent2lbl.items()}


class Agent:
    def __init__(self, username, password):
        self.username = username
        # Initialize the Speakeasy Python framework and login.
        self.speakeasy = Speakeasy(host=DEFAULT_HOST_URL, username=username, password=password)
        self.speakeasy.login()  # This framework will help you log out automatically when the program terminates.

    def detect_recommendation_question(self, input_string):
        # Convert the input string to lowercase for case-insensitive matching
        input_string = input_string.lower()
        word_list = ['advise', 'suggest', 'recommend', 'recommendation','similar']
        # Check if any word in the word_list is in the input_string
        for word in word_list:
            if word in input_string:
                return True
        return False

    def str2lbl(self, entity_str):
        entity_uri = wd[entity_str.replace("wd:", "")]
        label = ent2lbl.get(entity_uri)
        return label


    def detect_image_question(self, input_string):
        input_string = input_string.lower()
        word_list = ['look like', 'looks like', 'image', 'photo', 'picture', 'pictures', 'photos', 'images']
        for word in word_list:
            if word in input_string:
                return True
        return False

    def detect_movie_question(self, input_string):
        # Convert the input string to lowercase for case-insensitive matching
        input_string = input_string.lower()
        word_list = ["film", 'movie', 'movies', 'films']
        # Check if any word in the word_list is in the input_string
        for word in word_list:
            if word in input_string:
                return True
        return False

    def get_list_output(self, list: list):
        res = ''
        if len(list) == 1:
            final_res = f"{list[0]}"
        else:
            for index in range(len(list)):
                if index < len(list) - 2:
                    res += list[index] + ', '
                elif index == len(list) - 2:
                    res += list[index]
                else:
                    res += ' and ' + list[index]
            final_res = f"{res}"
        return final_res

    def get_final_output(self, answer: dict):
        if "crowd" in answer.keys():
            output = answer["crowd"]
            return output
        elif "recommendation" in answer.keys():
            output = answer["recommendation"]
            return output
        elif 'crowd' not in answer.keys() and 'KG' in answer.keys():
            output = self.get_list_output(answer['KG'])
            final_output = "I think it is " + output + '.'
            final_output = html.escape(final_output)
            final_output = final_output.encode('ascii', 'xmlcharrefreplace')
            return final_output.decode('ascii')
        elif 'crowd' not in answer.keys() and 'KG' not in answer.keys() and 'embeddings' in answer.keys():
            output = self.get_list_output(answer['embeddings'])
            final_output = "According to embeddings, the answer is " + output + '.'
            final_output = html.escape(final_output)
            final_output = final_output.encode('ascii', 'xmlcharrefreplace')
            return final_output.decode('ascii')
        else:
            final_output = "Sorry, can't get your answer. In case it's my fault," \
                           " I just respond to questions about movies from WIKIDATA." \
                           " I know a lot about movies, and can recommend you one. :)" \
                           " Please make sure spelling and the movie title is correct," \
                           " e.g. Who is the director of Good Will Hunting?"
            return final_output

    def listen(self):
        global movies_rem
        while True:
            # only check active chatrooms (i.e., remaining_time > 0) if active=True.
            rooms: List[Chatroom] = self.speakeasy.get_rooms(active=True)
            for room in rooms:
                if not room.initiated:
                    # send a welcome message if room is not initiated
                    room.post_messages(f'Hello! This is a welcome message from {room.my_alias}.')
                    room.initiated = True
                # Retrieve messages from this chat room.
                # If only_partner=True, it filters out messages sent by the current bot.
                # If only_new=True, it filters out messages that have already been marked as processed.
                for message in room.get_messages(only_partner=True, only_new=True):
                    print(
                        f"\t- Chatroom {room.room_id} "
                        f"- new message #{message.ordinal}: '{message.message}' "
                        f"- {self.get_time()}"
                    )

                    # Send a message to the corresponding chat room using the post_messages method of the room object.
                    room.post_messages(f"Received your message: '{message.message}' ")

                    input = message.message.strip()
                    # check if the input question type
                    recommendation_question = self.detect_recommendation_question(input)
                    print(f"recommendation_question {recommendation_question}")
                    image_question = self.detect_image_question(input)
                    print(f"image_question {image_question}")

                    # deal with the natural language prompt
                    # Movie title extraction
                    movies0 = title_extractor.extract_entity(input)
                    movies_true = title_extractor.fuzzy_input_movie(movies0)

                    # Person extraction
                    person0 = title_extractor.extract_per(input)
                    person_true = title_extractor.fuzzy_input_person(person0)

                    # relation extraction
                    relation_word = property_extractor.get_relation_word(input, movies_true)
                    property_id = property_extractor.get_property_id(relation_word)

                    my_params = {
                        'graph': graph,
                        'entity': movies_true,
                        'property_id': property_id,
                        'ent2id': ent2id,
                        'rel2id': rel2id,
                        'entity_emb': entity_emb,
                        'relation_emb': relation_emb,
                        'id2ent': id2ent,
                        'ent2lbl': ent2lbl
                    }

                    my_params_genre = {
                        'graph': graph,
                        'entity': movies_true,
                        'property_id': "P136",
                        'ent2id': ent2id,
                        'rel2id': rel2id,
                        'entity_emb': entity_emb,
                        'relation_emb': relation_emb,
                        'id2ent': id2ent,
                        'ent2lbl': ent2lbl
                    }

                    if image_question:
                        print("trigger image")
                        image_answer = img_extractor.get_image(person0, graph,items, person_true)
                        if not image_answer:
                            room.post_messages("No image is found.")
                        else:
                            for image in image_answer:
                                room.post_messages(image)
                    else:
                        answer = {}
                        if recommendation_question:
                            print("trigger recommendation")
                            # use embeddings to look for genre, e.g. ['drama', 'horror film']
                            movie_genre = embeddings.find_similar_predicate(my_params_genre)
                            # use embeddings to look for content similar movies, e.g.
                            # ['Texas Chainsaw 3D', 'Final Destination 3', 'The First Purge']
                            content_similar_movies = embeddings.find_similar_movie(my_params)
                            # use kg to look for product companies, e.g. None or "Disney", type is string
                            movie_company = kg.movie_product_company(graph, movies_true)
                            # use rating recommender to find ratings, e.g. {'Hamlet': 9.133333333, 'Othello': 8.285714286}
                            ratings = rating_recommender.find_ratings(movies_true)
                            # use rating recommender to find similar movies, e.g. {'Hamlet': ('The Color Purple', 9.1), 'Othello': ('Red Dust', 8.428571429)}
                            rating_similar_movies = rating_recommender.find_similar_movies(movies_true)
                            if movies_true:
                                movies_rem = "Based on the movie content, we recommend movies: \n" + self.get_list_output(
                                    content_similar_movies) + ".\n"
                                if movie_genre:
                                    genre_output = "The movie genre is " + self.get_list_output(movie_genre) + ".\n\n"
                                    movies_rem = genre_output + movies_rem
                                if movie_company:
                                    if len(movies_true) == 1:
                                        company = "The movie is from company of " + movie_company + ".\n\n"
                                    else:
                                        company = "The movies are from company of " + movie_company + ".\n\n"
                                    movies_rem = company + movies_rem
                                if ratings:
                                    if len(ratings.items()) == len(movies_true):
                                        ratings_output = "Rating found! :) The rating is " + str(ratings) + '.\n'
                                    else:
                                        ratings_output = "Rating of some movie is found! :) The rating is " + str(
                                            ratings) + '.\n'
                                    ratings_rem = "Based on the rating, we recommend you movie(s) with similar rating: \n" + str(
                                        rating_similar_movies) + ".\n\n"
                                    movies_rem = ratings_output + ratings_rem + movies_rem

                            else:
                                if self.detect_movie_question(input):
                                    # if prompt is asking for movies without specific movies
                                    movies_rem = "We want to recommend you some high rating movies, like 'Castle in the Sky','The Sopranos' and 'Apocalypse Now', you might" \
                                             " want to start from them: ;)"
                                else:
                                    movies_rem = "Do you want us to recommend a movie? Or do you have a specific movie in mind? Tell us, we can find a similar one for you. :)"

                            answer["recommendation"] = movies_rem
                        else:
                            # find property answer from KG, e.g. ['Murat Aslan']
                            kg_property_answer = kg.graph_query(movies_true, property_id, graph)
                            # find predicate answer from embeddings, e.g. ['drama', 'horror film']
                            emb_property_answer = embeddings.find_similar_predicate(my_params)
                            if crowd.get_crowd(movies_true,property_id):
                                crowd_answer0, irt_score, sup_votes, rej_votes = crowd.get_crowd(movies_true,
                                                                                                 property_id)
                                if 'Q' in crowd_answer0:
                                    crowd_answer0 = 'wd:' + str(crowd_answer0)
                                    crowd_answer0 = self.str2lbl(crowd_answer0)
                                crowd_answer_final = f"Crowd ,the answer is {crowd_answer0},Inter-rate agreement is {irt_score},\
                                                   The answer distribution for this specific task was {sup_votes} support votes,{rej_votes} reject votes!"
                                answer["crowd"] = crowd_answer_final
                            elif kg_property_answer:
                                answer['KG'] = kg_property_answer
                            elif emb_property_answer:
                                emb_res = [emb_property_answer[0]]
                                answer['embeddings'] = emb_res

                        final_output = self.get_final_output(answer)
                        room.post_messages(final_output)

                    # Mark the message as processed, so it will be filtered out when retrieving new messages.
                    room.mark_as_processed(message)

                # Retrieve reactions from this chat room.
                # If only_new=True, it filters out reactions that have already been marked as processed.
                for reaction in room.get_reactions(only_new=True):
                    print(
                        f"\t- Chatroom {room.room_id} "
                        f"- new reaction #{reaction.message_ordinal}: '{reaction.type}' "
                        f"- {self.get_time()}")

                    room.post_messages(f"Received your reaction: '{reaction.type}' ")
                    room.mark_as_processed(reaction)

            time.sleep(listen_freq)

    @staticmethod
    def get_time():
        return time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime())


if __name__ == '__main__':
    demo_bot = Agent("melt-moderato-aroma_bot", "12OfTKdlTifqcA")
    demo_bot.listen()
