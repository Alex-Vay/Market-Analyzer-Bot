import difflib


def smart_function(product_name, titles_dict):
    best_match_index = 0
    best_ratio = 0
    for index, product_title in titles_dict.items():
        try:
            sm = difflib.SequenceMatcher(None, product_name.lower(), product_title.lower())
            similarity_ratio = sm.ratio()
            if similarity_ratio > best_ratio:
                best_ratio = similarity_ratio
                best_match_index = index
        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")
            continue
    return best_match_index if best_ratio >= 0.15 else None
