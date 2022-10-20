__CATEGORY_ENCODINGS = {}
__CATEGORY_ENCODING_COUNTERS = {}


def get_category_encoding(category_variable: str, category_name: str):
    if category_variable not in __CATEGORY_ENCODINGS:
        __CATEGORY_ENCODINGS[category_variable] = {category_name: 0}
        __CATEGORY_ENCODING_COUNTERS[category_variable] = 1

    if category_name not in __CATEGORY_ENCODINGS[category_variable]:
        __CATEGORY_ENCODINGS[category_variable][category_name] = __CATEGORY_ENCODING_COUNTERS[category_variable]
        __CATEGORY_ENCODING_COUNTERS[category_variable] += 1

    return __CATEGORY_ENCODINGS[category_variable][category_name]
