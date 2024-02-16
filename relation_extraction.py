import spacy
from Movie_title import MovieTitleExtractor
# nlp = spacy.load('en_core_web_trf')
# title_extractor = MovieTitleExtractor(nlp)
#movies_data = pd.read_csv('../movies.csv')


class MoviePropertyExtractor:
    def __init__(self):
        # Film property possibilities
        # The truth one entity may have several URI really influence our outcome , thus , we use a dictionary
        self.crowd_entity = {
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
        self.crowd_relation = {
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

        self.film_property_possibility = {
            'director': {'direct', 'make', 'create', 'director'},
            'cast member': {'actor', 'actress', 'cast','cast member'},
            'genre': {'type', 'kind', 'genre'},
            'publication date': {'release', 'date', 'airdate', 'publication', 'launch', 'broadcast','publication date'},
            'producer': {'producer'},
            'executive producer': {'showrunner','executive producer'},
            'screenwriter': {'scriptwriter', 'screenwriter', 'screenplay', 'teleplay', 'writer', 'script', 'scenarist',
                             'write'},
            'based on': {'base on', 'story', 'base','based on'},
            'country of origin': {'origin', 'country','country of origin'},
            'filming location': {'flocation', 'location','filming location'},
            'director of photography': {'cinematographer', 'DOP', 'dop','director of photography'},
            'film editor': {'editor','film editor'},
            'production designer': {'designer','production designer'},
            'box office': {'box', 'office', 'funding','box office'},
            'cost': {'budget', 'cost'},
            'nominated for': {'nomination', 'award', 'finalist', 'shortlist', 'selection','nominated for'},
            'costume designer': {'costume', 'designer','costume designer'},
            'official website': {'website', 'site','official website'},
            'narrative website': {'nlocation','narrative website'},
            'production company': {'company','production','production company'},
            'review score': {'user', 'review', 'score', 'rate'},
            'MPA film rating': {'rating', 'classification'},
            'award received': {'award', 'honor', 'decoration','award received'},
            "indirect subclass": {"indirect subclass","subclass"},
            "distributed by": {"distributed by"},
            "voice actor": {"voice actor"},
            "JMK film rating": {"JMK film rating"},
            "film crew member": {"film crew member"},
            "armament": {"armament"},
            "art director": {"art director"},
            "allegiance": {"allegiance"},
            "place of burial": {"place of burial"},
            "location": {"location"},
            "place of death": {"place of death"},
            "country of citizenship":{"country of citizenship"},
            "languages spoken, written or signed": {"languages spoken, written or signed"},
        }

        # Film property values
        self.film_property = {
            "director": "P57",
            "cast member": "P161",
            "genre": "P136",
            "publication date": "P577",
            "producer": "P162",
            "executive producer": "P1431",
            "screenwriter": "P58",
            'based on': 'P144',
            'country of origin': 'P495',
            "filming location": "P915",
            "original language of film or TV show": "P364",
            "director of photography": "P344",
            'film editor': "P1040",
            'production designer': "P2554",
            "box office": 'P2142',
            'cost': "P2130",
            'nominated for': 'P1411',
            'costume designer': 'P2515',
            'official website': 'P856',
            'review score': 'P444',
            'MPA film rating': 'P1657',
            'award received': 'P166',
            'production company': 'P272',
            "indirect subclass": "ddis:indirectSubclassOf",
            "distributed by": "wdt:P750",
            "voice actor": "wdt:P725",
            "JMK film rating": "wdt:P3650",
            "film crew member": "wdt:P3092",
            "armament": "wdt:P520",
            "art director": "wdt:P3174",
            "allegiance": "wdt:P945",
            "place of burial": "wdt:P119",
            "location": "wdt:P276",
            "place of death": "wdt:P20",
            "country of citizenship": "wdt:P27",
            "languages spoken, written or signed": "wdt:P1412",
        }

        # Load the NLP model
        self.nlp = spacy.load("en_core_web_sm")

    def get_relation_word(self, sentence, movie_title):
        """exclude words which could be in the movie titles"""
        voc_list = [movie for movie in movie_title]
        voc_list.append("movie")
        voc_list.append("film")
        print(voc_list)

        print(voc_list)
        doc = self.nlp(sentence)
        relation_word = []
        docs = [(l.pos_,l.text) for l in doc]
        print(docs)

        for crowd_entity in self.crowd_entity.keys():
            if crowd_entity == voc_list[0]:
               for crowd_relation in self.crowd_relation.keys():
                   if crowd_relation in sentence:
                       return crowd_relation

        for token in doc:
            if token.pos_ in ['NOUN', 'VERB']:
                if token.text not in voc_list:
                    relation_word.append(token.lemma_)
        if relation_word:
            print(relation_word)
            return relation_word[0]
        return None

    def get_property_id(self, relation_word):
        # return the property id, if not, return None!
        for key, synonyms in self.film_property_possibility.items():
            if relation_word in synonyms:
                return self.film_property[key]
        return None


# if __name__ == '__main__':
#     #sentence = "Who is the screenwriter of The Masked Gang: Cyprus?"
#
#     s1 ="which is the indirect subclass of fictional princess"
#     movies = title_extractor.extract_entity(s1)
#     movie_true = title_extractor.fuzzy_input_movie(movies)
#     #s1 = "Let me know what sandra Bullock and Julia Roberts looks like. "
#     #s2 = "Given that I like The Lion King, Pocahontas, and The Beauty and the Beast, can you recommend some movies?"
#     #s3 = "Recommend movies like Nightmare on Elm Street, Friday the 13th, and Halloween."
#     mp = MoviePropertyExtractor()
#     #res = me.extract_entity(s1)
#     relation = mp.get_relation_word(s1,movie_true)
#     print(relation)
#     relation_id = mp.get_property_id(relation)
#     print(relation_id)
#     # id = mp.get_property_id(relation)
#     # print(id)
