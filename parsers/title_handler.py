import os
from sentence_transformers import SentenceTransformer, util

project_root = os.path.abspath(os.path.join(os.path.realpath(__file__), '../../'))
model_dir = os.path.join(project_root, 'all-MiniLM-L6-v2_local')
if os.path.isdir(model_dir):
    model = SentenceTransformer(model_dir)
else:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.save(model_dir)

def smart_function(product_name, titles_dict):
    query_embedding = model.encode(product_name, convert_to_tensor=True)

    best_match_index = None
    best_score = -1

    for index, product_title in titles_dict.items():
        try:
            product_embedding = model.encode(product_title, convert_to_tensor=True)
            similarity_score = util.cos_sim(query_embedding, product_embedding).item()

            if similarity_score > best_score:
                best_score = similarity_score
                best_match_index = index
        except Exception as e:
            print(f"Ошибка при обработке товара '{product_title}': {e}")
            continue
    return best_match_index if best_score >= 0.5 else None