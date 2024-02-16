# Movie Query Bot

## Overview

The Movie Query Bot is designed to efficiently process natural language prompts related to movies listed in Wikidata. It specializes in handling two types of queries:

1. **Closed Queries**: For direct questions like "Who is the director of Star Wars: Episode VI - Return of the Jedi?"
2. **Open Queries**: For broader requests such as "Recommend movies like Halloween".

Users are encouraged to ensure correct spelling and precise movie titles or person names from Wikidata for optimal query results. 

## How It Works

The bot operates through a multi-step pipeline to process and respond to user queries:

### 1. Entity and Relation Extraction

- **Entity Extraction**: Identifies movie titles and person names within the user input.
  - `movies0 = title_extractor.extract_entity(input)` for extracting movie titles.
  - `person0 = title_extractor.extract_per(input)` for extracting person names.
- **Fuzzy Matching**: Ensures accuracy by verifying and correcting titles or names through fuzzy matching.
  - `movies_true = title_extractor.fuzzy_input_process(movies0)`
  - `person_true = title_extractor.fuzzy_input_person(person0)`
- **Relation Extraction**: Determines the nature of the query (e.g., director, producer) and maps it to a corresponding property ID.
  - `relation_word = property_extractor.get_relation_word(input, movies_true)`
  - `property_id = property_extractor.get_property_id(relation_word)`

### 2. Question Type Classification

Based on specific keywords within the query, the bot classifies the question into one of the following categories:

- **Recommendation**: Uses keywords like 'advise', 'suggest', etc.
- **Multimedia**: Focuses on requests for images or pictures.
- **Closed Questions**: Processes standard queries where movie titles and property IDs are identified.
- **Default**: For queries that don't match any of the above types, a default response prompts for correct input.

### 3. Question Answering

Depending on the question type, the bot employs different strategies to find and deliver answers:

- **Multimedia Questions**: Retrieves pictures of persons using their IMDB ID.
- **Recommendation Questions**: Utilizes entity embeddings to find similar movies.
- **Crowdsourcing Questions**: Gives priority to answers from crowdsourced data when available.
- **KG Questions**: Uses the Knowledge Graph for answers not available through crowdsourcing.
- **Embedding Questions**: Resorts to embeddings for answers not found in the Knowledge Graph or crowdsourcing.

### 4. Formulating Output

The output prioritizes multimedia and recommendation queries. For other queries, the bot selects the most relevant source of answer in the following order: crowdsourcing, Knowledge Graph, and embeddings. If no answer is available from these sources, a default response is provided.

##  Unique Features and Innovations

### Advanced Natural Language Processing

- **Utilizing Spacy for NER**: Our bot leverages the Spacy 'en_core_web_trf' transformer model for named entity recognition (NER), offering superior performance over the previously used Huggingface Bert model. This advancement allows for the accurate identification of multiple movie titles within a single sentence.

### Efficient Data Management

- **Building Movie Title Database**: We've extracted all movie titles from a knowledge graph to create a comprehensive `movies.csv` database. This database, sized at 459KB, streamlines our data processing efforts.

    ```sparql
    SELECT DISTINCT ?lbl WHERE {
      ?movie wdt:P31/wdt:P279* wd:Q11424 .
      ?movie rdfs:label ?lbl .
    }
    ```

- **Accurate Movie Title Extraction**: Employing the `fuzz.ratio` function, we enhance the accuracy of movie title matching between user input and our database, laying a critical foundation for further processing.

- **Building Person Database**: Similarly, a `person.csv` database was developed to efficiently manage person names extracted from knowledge graphs, sized at 1.4MB.

- **Accurate Person Name Extraction**: Utilizing `fuzz.ratio`, we ensure the precise identification of person names, enhancing the bot's resilience to incorrect inputs.

### Enhanced Recommendation Systems

- **Embedding-based Similarity Search**: By leveraging an extensive entity embedding matrix, our bot performs content-based filtering with remarkable accuracy, effectively recommending movies within specific genres or themes.

- **Item-based Recommendation System**: Utilizing an item-based approach, we analyze movie profiles and ratings distributions to offer recommendations that closely match user preferences.

### Performance Optimization

- **Building a New JSON File**: To overcome the challenges posed by the large original JSON file, we created a streamlined version (`preprocessed_file.json`, sized at 250.3MB) that significantly reduces image retrieval times, enhancing user experience.

##  Libraries and Techniques

Our project incorporates a range of external libraries and techniques to achieve its objectives:

- **json**: For parsing and handling JSON data.
- **Numpy**: Supports large, multi-dimensional arrays and matrices, enhancing mathematical operations.
- **Rdflib**: Facilitates working with RDF, supporting schema evolution without requiring changes to data consumers.
- **typing**: Improves code readability and error checking through type hints.
- **time**: Offers functions for managing time-related tasks.
- **csv**: Implements classes for reading and writing tabular data in CSV format.
- **spacy**: Powers advanced NLP tasks, utilizing the `en_core_web_trf` model for NER.
- **pandas**: Provides robust data analysis and manipulation tools.
- **html**: Handles HTML data through escaping and unescaping HTML entities.
- **fuzzywuzzy**: Enables string matching and comparison.
- **statsmodels**: Used for calculating inter-rater agreement scores in crowdsourced data.
- **Counter**: Counts hashable objects, acting as a dictionary for elements and their counts.
- **jellyfish**: Facilitates approximate and phonetic matching of strings.
- **sklearn**: Includes comprehensive tools for model fitting, data preprocessing, model selection, evaluation, and experimentation with built-in datasets.

These tools and techniques collectively empower our bot to deliver accurate and relevant responses to user queries, showcasing our commitment to leveraging cutting-edge technology for enhancing user experience.



