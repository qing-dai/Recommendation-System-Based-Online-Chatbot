from use_embeddings import Embeddings as emb

import ijson
import rdflib


# graph = rdflib.Graph().parse(source='./14_graph.nt', format='turtle')


class ImageExtraction:
    def __init__(self):
        pass

    def get_imdb_id(self, entity, graph):
        # get entity_id for entity like "Halle Berry"
        entity_id = emb().find_entity_id(entity, graph)

        # get imdb_id for above entity_id, i.e. 'nm0000932'
        image_query = f'''
          prefix wdt: <http://www.wikidata.org/prop/direct/>
          prefix wd: <http://www.wikidata.org/entity/>
          SELECT ?image WHERE {{
            wd:{entity_id} wdt:P345 ?image .
          }}
        '''

        img_res = graph.query(image_query)
        for row, in img_res:
            return str(row)

    def get_image(self, person0: list, graph, items, person_true: list):
        """
        Get images for Persons, e.g. ["Halle Berry", "Julia Roberts"],
        especially we can respond to several persons in a question.

        person0: original person name list
        person_true: person name list after fuzzy search
        """
        if not person_true:
            return None

        imdb_id = [self.get_imdb_id(entity, graph) for entity in person_true]
        print(imdb_id)
        img_result = {id: None for id in imdb_id}  # Initialize result dictionary

        # assume items (json file) will be initiated as global variable
        for item in items:
            cast_id = item['cast'][0]
            for i, id in enumerate(imdb_id):
                if id in cast_id:
                    img = item.get('img', '').replace('.jpg', '') if item.get('img', '').endswith(
                        '.jpg') else item.get('img', '')
                    img_result[id] = f"image:{img}"
                    break  # Break if image found for one ID

        # Filling the result list with images or no-image-found messages
        final_result = []
        for id, img in img_result.items():
            person = person0[imdb_id.index(id)]
            final_result.append(img if img else f"No image is found for {person}")

        return final_result

# if __name__ == '__main__':
#     filename = '../preprocessed_file.json'
#     entity = ["Richard Marquand"]
#     img_extractor = ImageExtraction(filename)
#     res = img_extractor.get_image(entity, graph)
#     print(res)
