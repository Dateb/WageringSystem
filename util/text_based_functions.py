import difflib


def get_name_similarity(name_a: str, name_b: str) -> float:
    longest_common_substring = get_longest_common_substring(name_a, name_b)
    longer_string_length = max(len(name_a), len(name_b))

    common_substring_fraction = len(longest_common_substring) / longer_string_length

    return common_substring_fraction


def get_longest_common_substring(s1, s2):
    seq_matcher = difflib.SequenceMatcher(None, s1, s2)
    match = seq_matcher.find_longest_match(0, len(s1), 0, len(s2))

    if match.size == 0:
        return ""

    common_substring = s1[match.a:match.a + match.size]
    return common_substring


if __name__ == '__main__':
    name_a = "Christophe-Patrice"
    name_b = "Christophe"

    similarity_score = get_name_similarity(name_a, name_b)

    print(f"sim({name_a}, {name_b}) = {similarity_score}")
