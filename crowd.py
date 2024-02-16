import pandas as pd
import numpy as np
from use_embeddings import Embeddings as emb
import rdflib

wd = rdflib.Namespace('http://www.wikidata.org/entity/')
wdt = rdflib.Namespace('http://www.wikidata.org/prop/direct/')
ddis = rdflib.Namespace('http://ddis.ch/atai/')
RDFS = rdflib.namespace.RDFS
SCHEMA = rdflib.Namespace('http://schema.org/')

#define a crowd class
class Crowd:
    def __init__(self):
        #to initialize a crowd , we need to input the filtered data into the memory
        self.data = pd.read_csv("../processed_crowd")
        self.dict_irt = {
            '7QT': 0.236,
            '8QT': 0.040,
            '9QT': 0.263
        }

        # The truth one entity may have several URI really influence our outcome , thus , we use a dictionary
        self.dict_entity = {
            "Mulan": "wd:Q1893555",
            "E.T. the Extra-Terrestrial": "wd:Q11621",
            "Peaceful Warrior": "wd:Q603545",
            "God Help the Girl": "wd:Q16911843",
            "Finding Nemo": "wd:Q132863",
            "The Browning Version": "wd:Q1628022",
            "The Party's Just Beginning": "wd:Q48313910",
            "The Princess and the Frog": "wd:Q171300",
            "The Twilight Saga: Eclipse": "wd:Q217010",
            "The Candidate": "wd:Q4993462",
            "Nightjohn": "wd:Q7033842",
            "station building": "wd:Q1339195",
            "film organization": "wd:Q104649845",
            "fictional princess": "wd:Q61928601",
            "comics": "wd:Q1004",
            "children's book": "wd:Q8275050",
            "literary pentalogy": "wd:Q17710986",
            "supervillain team": "wd:Q16101952",
            "neighbourhood of Helsinki": "wd:Q15715406",
            "disputed territory": "wd:Q15239622",
            "Silver Bear": "wd:Q708135",
            "Kaboom": "wd:Q1720855",
            "Like Crazy": "wd:Q598752",
            "In the Line of Fire": "wd:Q427386",
            "Scent of a Woman": "wd:Q321561",
            "Tom Meets Zizou": "wd:Q1410031",
            "Guardians of the Galaxy Vol. 2": "wd:Q20001199",
            "Kung Fu Panda 3": "wd:Q15055043",
            "Magic Carpet Ride": "wd:Q639070",
            "Sex, Death and Bowling": "wd:Q23999890",
            "RoboCop 3": "wd:Q841233",
            "Behind the Candelabra": "wd:Q2893887",
            "The Girl in the Spider's Web": "wd:Q19803136",
            "Martial Arts of Shaolin": "wd:Q1039395",
            "Gandhi": "wd:Q202211",
            "The Adventures of Tom Sawyer": "wd:Q326914",
            "Bloody Mama": "wd:Q885281",
            "Being with Juli Ashton": "wd:Q814781",
            "Lillian Lehman": "wd:Q6548158",
            "Conan the Barbarian": "wd:Q1123629",
            "Les Misérables": "wd:Q1780602",
            "Eskimo": "wd:Q610633",
            "A Happy Event": "wd:Q2188914",
            "Free Willy 3: The Rescue": "wd:Q1032889",
            "Iron Man 3": "wd:Q209538",
            "Top Gun: Maverick": "wd:Q31202708",
            "Normal": "wd:Q2576243",
            "Delta Farce": "wd:Q4335275",
            "Medea": "wd:Q931557",
            "The Hell of '63": "wd:Q2235250",
            "Naruto the Movie: Guardians of the Crescent Moon Kingdom": "wd:Q696646",
            "Masaichi Nagata": "wd:Q6782400",
            "Günter Grass": "wd:Q6538",
            "Mandarin Chinese": "wd:Q9192",
            "Miranda Frigon": "wd:Q10623856",
            "X-Men: First Class": "wd:Q223596",
            "A Night at the Opera": "wd:Q943992",
        }

        # same reason above
        self.dict_relation = {
        "box office":"wdt:P2142",
        "publication date":"wdt:P577",
        "indirect subclass": "ddis:indirectSubclassOf",
        "cast member":"wdt:P161",
        "country of origin": "wdt:P495",
        "distributed by":"wdt:P750",
        "genre":"wdt:P136",
        "cast member":"wdt:P161",
        "director of photography":"wdt:P344",
        "voice actor":"wdt:P725",
        "production designer":"wdt:P2554",
        "screenwriter":"wdt:P58",
        "JMK film rating":"wdt:P3650",
        "film crew member":"wdt:P3092",
        "original language of film or TV show":"wdt:P364",
        "armament":"wdt:P520",
        "art director":"wdt:P3174",
        "allegiance":"wdt:P945",
        "place of burial":"wdt:P119",
        "location":"wdt:P276",
        "place of death":"wdt:P20",
        "executive producer":"wdt:P1431",
        "country of citizenship":"wdt:P27",
        "production company":"wdt:P272",
        "languages spoken, written or signed":"wdt:P1412",
        }

    #this method take labels as input, output answer
    def get_crowd(self,entity,relation):
        try:
          for ent in entity:
              entity_id = self.dict_entity.get(ent)
              break
          if relation == "ddis:indirectSubclassOf":
              relation = relation
          else:
              relation = f"wdt:{relation}"
          result = self.crowd_answer(entity_id,relation)
        except Exception as e:
            return None
        #print(relation_id)
        #print(entity_id)
        return result

    #this method take URIs as input , return a string
    def crowd_answer(self,sub, pre):
        # IRT score is pre-calculated ,the calculating codes are in file "get_IRA".To save time ,i use a dict here
        question = self.data.loc[(self.data.Input1ID == sub) & (self.data.Input2ID == pre)]
        if question.empty:
            return None
        # get value in the dict
        irt_score = self.dict_irt[f"{question['HITTypeId'].iloc[0]}"]

        answer_counts = question['AnswerLabel'].value_counts()
        #get the number of support votes and reject votes
        sup_votes = answer_counts.get('CORRECT', 0)
        rej_votes = answer_counts.get('INCORRECT', 0)
        # get an answer , default is the Input3ID
        answer = question['Input3ID'].iloc[0]

        #if more reject , check if there is an correct answer in FixPosition
        if((rej_votes>sup_votes) and (any(question['FixPosition']))):
            non_empty_fix_position = question.loc[~question['FixPosition'].isnull(), 'FixPosition']
            if not non_empty_fix_position.empty:
              if non_empty_fix_position.iloc[0]=="Subject":
                 answer = question['Input3ID'].iloc[0]
              elif non_empty_fix_position.iloc[0]=="Object":
                 non_empty_fix_value = question.loc[~question['FixPosition'].isnull(), 'FixValue']
                 answer = non_empty_fix_value.iloc[0]
                 #if asnwer is nan , undo the operation
                 if pd.isna(answer):
                     answer = question['Input3ID'].iloc[0]
            else:
                answer = answer
        #answer = self.str2lbl(answer)
        #result = f"Crowd ,the answer is {answer},Inter-rate agreement is {irt_score},The answer distribution for this specific task was {sup_votes} support votes,{rej_votes} reject votes!"
        #return result
        return answer , irt_score , sup_votes, rej_votes


# C = Crowd()
# an = C.get_crowd(["comics"],"ddis:indirectSubclassOf")
# a = C.crowd_answer("wd:Q1004","ddis:indirectSubclassOf")
# print(an)
# print(a)
