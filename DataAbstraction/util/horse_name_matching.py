import difflib


def get_longest_common_substring(s1, s2):
    seq_matcher = difflib.SequenceMatcher(None, s1, s2)
    match = seq_matcher.find_longest_match(0, len(s1), 0, len(s2))

    if match.size == 0:
        return ""

    common_substring = s1[match.a:match.a + match.size]
    return common_substring
