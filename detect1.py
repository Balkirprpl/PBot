import spacy

nlp = spacy.load("en_core_web_md")

def scan_comments(comment_similarity_array):
    # ------------------------------
    #   Calculating txt similarity
    # ------------------------------
    z = 1.0
    l = len(comment_similarity_array)
    for i1 in range(l):
        for i2 in range(i1 + 1, l):
            c1 = comment_similarity_array[i1]
            c2 = comment_similarity_array[i2]
            z *= compare_text(c1, c2)

    return z


def compare_text(text1, text2):
        similarity = nlp(text1).similarity(nlp(text2))
        return similarity


