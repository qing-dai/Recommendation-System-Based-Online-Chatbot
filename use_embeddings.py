from sklearn.metrics import pairwise_distances
import rdflib
import numpy as np


class Embeddings:
    def __init__(self):
        """
        A content-filter recommender
        """
        self.WD = rdflib.Namespace('http://www.wikidata.org/entity/')
        self.WDT = rdflib.Namespace('http://www.wikidata.org/prop/direct/')

    def find_entity_id(self, entity, graph):

        query_template = f'''
          prefix wdt: <http://www.wikidata.org/prop/direct/>
          prefix wd: <http://www.wikidata.org/entity/>

          SELECT ?ent WHERE {{
              ?ent rdfs:label "{entity}"@en .
          }}'''

        # check if entity is empty
        if entity:
            entity_id = graph.query(query_template)
            output = [str(s) for s, in entity_id]
            # check if output is empty
            if output:
                return output[0].replace(self.WD, '')
            else:
                return None
        else:
            return None

    def find_similar_predicate(self, params_dict, top_n=2):
        # introduce global variables from params_dict
        graph = params_dict['graph']
        entities = params_dict['entity']
        property_id = params_dict['property_id']
        ent2id = params_dict['ent2id']
        rel2id = params_dict['rel2id']
        entity_emb = params_dict['entity_emb']
        relation_emb = params_dict['relation_emb']
        id2ent = params_dict['id2ent']
        ent2lbl = params_dict['ent2lbl']

        # get entity id
        # scale the function to take care of a list of entities
        ids = []
        for entity in entities:
            # find entity id, like WD.Q7750525
            entity_id = self.find_entity_id(entity, graph)
            emb_entity_id = self.WD[entity_id]
            if emb_entity_id not in ent2id:
                continue
            else:
                ids.append(emb_entity_id)

        # get relation id, like WDT.P57
        relation_id = self.WDT[property_id]
        # if no relation nor entity found in the embeddings, then return None
        if relation_id not in rel2id:
            return None
        if not ids:
            return None
        else:
            # Get embeddings for entity and relation
            head = np.mean([entity_emb[ent2id[idd]] for idd in ids], 0)
            pred = relation_emb[rel2id[relation_id]]

            # Compute resultant embedding
            lhs = head + pred

            # Compute distance to all other entities
            dist = pairwise_distances(lhs.reshape(1, -1), entity_emb).reshape(-1)

            # Get top N entities
            most_likely = dist.argsort()[:top_n]

            # Retrieve and return these entities
            #id_label_score = [(id2ent[idx][len(self.WD):], ent2lbl[id2ent[idx]], dist[idx]) for idx in most_likely]
            # return label only
            return [ent2lbl[id2ent[idx]] for idx in most_likely]


    def find_similar_movie(self, params_dict):
        # introduce global variables from params_dict
        graph = params_dict['graph']
        entities = params_dict['entity']
        entity_emb = params_dict['entity_emb']
        ent2id = params_dict['ent2id']
        ent2lbl = params_dict['ent2lbl']
        id2ent = params_dict['id2ent']

        ids = []
        for entity in entities:
            entity_id = self.find_entity_id(entity, graph)
            emb_entity_id = self.WD[entity_id]
            if emb_entity_id not in ent2id:
                continue
            else:
                ids.append(emb_entity_id)
        #print(ids)
        if ids:
            # averaging input movies embeddings
            mean_emb = np.mean([entity_emb[ent2id[idd]] for idd in ids], 0)
            dist = pairwise_distances(mean_emb.reshape(1, -1), entity_emb).reshape(-1)
            # find most plausible entities to the average of the input movies embeddings
            most_likely = dist.argsort()
            res = []
            for idx in most_likely[:15]:
                # make sure the similar movies not the same with the given movies
                if ent2lbl.get(id2ent[idx]) and ent2lbl[id2ent[idx]] not in entities:
                    res.append(ent2lbl[id2ent[idx]])
            return res[:3]
        return None
