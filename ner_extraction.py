import jellyfish
import string


class MovieTitleExtractor:
    def __init__(self, pipe):
        self.pipe = pipe

    def get_movie_title_from_question(self, sentence):
        results = self.pipe(sentence)
        movie_title_tokens = [token['word'] for token in results if 'TITLE' in token['entity']]
        movie_title = ' '.join(movie_title_tokens).replace('Ġ', '').replace('âĢĵ', '–').strip()
        res_len = len(movie_title.split())
        corrected_movie_title = movie_title
        for j in range(len(sentence.split()) - res_len + 3):
            result = sentence.split()[j:j + res_len - 1]
            result = " ".join(result)
            dist = jellyfish.damerau_levenshtein_distance(result, movie_title)
            if dist <= 3:
                corrected_movie_title = result.strip(string.punctuation)
        return corrected_movie_title.replace('-', '–')
