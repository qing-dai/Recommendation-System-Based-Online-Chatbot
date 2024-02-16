import os
import rdflib
import use_embeddings
from collections import Counter


class KnowledgeGraph:
    def __init__(self):
        pass

    def movie_product_company(self, graph, entities):
        # if 2/3 of the movies are made from one company, then return it!
        all_companies = []
        for entity in entities:
            entity_id = use_embeddings.Embeddings().find_entity_id(entity, graph)
            query_template = f'''
            prefix wdt: <http://www.wikidata.org/prop/direct/>
            prefix wd: <http://www.wikidata.org/entity/>

            SELECT ?entLabel WHERE {{
                wd:{entity_id} wdt:P272 ?ent .
                ?ent rdfs:label ?entLabel .
            }}'''

            product_company = graph.query(query_template)
            output = [str(s) for s, in product_company]
            print(output)
            if output:  # Check if output is not empty
                all_companies.append(output[0])
        if all_companies:
            print(f"All companies are {all_companies}")
            company_counts = Counter(all_companies)
            most_common_company, count = company_counts.most_common(1)[0]
            percentage = (count / len(entities)) * 100
            if percentage >= 66:
                return most_common_company
        return None

    def graph_query(self, entity, relation_id, graph):
        # assume only on entity in the entity list
        if not entity:
            return None
        else:
            entity = entity[0]
        # create query templates for these movie titles
        query_template_1 = f'''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>
        SELECT ?lbl WHERE {{
            ?ent rdfs:label "{entity}"@en .
            ?ent wdt:P31 wd:Q11424 .
            ?ent wdt:{relation_id} ?obj .
            ?obj rdfs:label ?lbl .
        }}
      '''

        query_template_2 = f'''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>
        SELECT ?obj WHERE {{
            ?ent rdfs:label "{entity}"@en .
            ?ent wdt:P31 wd:Q11424 .
            ?ent wdt:{relation_id} ?obj .
        }}
      '''

        query_res_1 = graph.query(query_template_1)
        query_res_2 = graph.query(query_template_2)

        output_1 = [str(s) for s, in query_res_1]
        output_2 = [str(s) for s, in query_res_2]
        # print(f"According to query1, {output_1}")
        # print(f"According to query2, {output_2}")
        if output_1:
            return output_1
        return output_2
