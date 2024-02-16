import ijson
import json


def preprocess_and_save(filename, output_filename):
    single_cast_items = []

    with open(filename, 'r') as file:
        for item in ijson.items(file, 'item'):
            cast = item.get('cast', [])
            if len(cast) == 1:
                single_cast_items.append(item)

    with open(output_filename, 'w') as outfile:
        json.dump(single_cast_items, outfile)


# Preprocess and save the items with single cast member to a new file
preprocess_and_save('../images.json', '../preprocessed_file.json')




