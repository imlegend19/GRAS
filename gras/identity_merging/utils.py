def wfi_levenshtein(string_1, string_2):
    """
    Calculates the Levenshtein distance between two strings. This version uses an iterative version of the
    Wagner-Fischer algorithm.
    
    :param string_1: String 1
    :type string_1: str
    
    :param string_2: String 2
    :type string_2: str
    
    :return Levenshtein distance between two string_1 & string_2
    :rtype: float
    
    Usage::
        >>> wfi_levenshtein('kitten', 'sitting')
        0.57
        >>> wfi_levenshtein('kitten', 'kitten')
        1
        >>> wfi_levenshtein('', '')
        0
    """
    if string_1 == string_2:
        return 1
    
    len_1 = len(string_1)
    len_2 = len(string_2)
    
    if len_1 == 0:
        return len_2
    
    if len_2 == 0:
        return len_1
    
    if len_1 > len_2:
        string_2, string_1 = string_1, string_2
        len_2, len_1 = len_1, len_2
    
    d0 = [i for i in range(len_2 + 1)]
    d1 = [j for j in range(len_2 + 1)]
    
    for i in range(len_1):
        d1[0] = i + 1
        for j in range(len_2):
            cost = d0[j]
            
            if string_1[i] != string_2[j]:
                # substitution
                cost += 1
                
                # insertion
                x_cost = d1[j] + 1
                if x_cost < cost:
                    cost = x_cost
                
                # deletion
                y_cost = d0[j + 1] + 1
                if y_cost < cost:
                    cost = y_cost
            
            d1[j + 1] = cost
        
        d0, d1 = d1, d0
    
    return round(1 - d0[-1] / max(len_1, len_2), 2)


def damerau_levenshtein(string_1, string_2):
    """
    Calculates the Damerau-Levenshtein distance between two strings. In addition to insertions, deletions and
    substitutions, Damerau-Levenshtein considers adjacent transpositions. This version is based on an iterative
    version of the Wagner-Fischer algorithm.
    
    Usage::
        >>> damerau_levenshtein('kitten', 'sitting')
        0.57
        >>> damerau_levenshtein('kitten', 'kittne')
        0.83
        >>> damerau_levenshtein('', '')
        0
    """
    if string_1 is None or string_2 is None:
        return 0
    
    if string_1 == string_2:
        return 1
    
    len_1 = len(string_1)
    len_2 = len(string_2)
    
    if len_1 == 0:
        return len_2
    
    if len_2 == 0:
        return len_1
    
    if len_1 > len_2:
        string_2, string_1 = string_1, string_2
        len_2, len_1 = len_1, len_2
    
    d0 = [i for i in range(len_2 + 1)]
    d1 = [j for j in range(len_2 + 1)]
    prev = d0[:]
    
    s1 = string_1
    s2 = string_2
    
    for i in range(len_1):
        d1[0] = i + 1
        for j in range(len_2):
            cost = d0[j]
            
            if s1[i] != s2[j]:
                # substitution
                cost += 1
                
                # insertion
                x_cost = d1[j] + 1
                if x_cost < cost:
                    cost = x_cost
                
                # deletion
                y_cost = d0[j + 1] + 1
                if y_cost < cost:
                    cost = y_cost
                
                # transposition
                if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                    transposition_cost = prev[j - 1] + 1
                    if transposition_cost < cost:
                        cost = transposition_cost
            d1[j + 1] = cost
        
        prev, d0, d1 = d0, d1, prev
    
    return round(1 - d0[-1] / max(len_1, len_2), 2)


def monge_elkan(string_1, string_2, method=damerau_levenshtein):
    """
    Calculates the Monge-Elkan distance for 2 strings.
    :param string_1:
    :param string_2:
    :param method:
    :return:
    """
    if string_1 is None or string_2 is None:
        return 0
    
    if string_1 == string_2:
        return 1
    
    distance = 0
    for w1 in string_1.split():
        max_score = 0
        for w2 in string_2.split():
            max_score = max(max_score, method(w1, w2))
        distance += max_score
    
    return distance / len(string_1.split())


def dice_coefficient(a, b):
    """dice coefficient 2nt / (na + nb)."""
    if not len(a) or not len(b):
        return 0.0
    
    if len(a) == 1:
        a = a + u'.'
    
    if len(b) == 1:
        b = b + u'.'
    
    a_bigram_list = []
    for i in range(len(a) - 1):
        a_bigram_list.append(a[i:i + 2])
    
    b_bigram_list = []
    for i in range(len(b) - 1):
        b_bigram_list.append(b[i:i + 2])
    
    a_bigrams = set(a_bigram_list)
    b_bigrams = set(b_bigram_list)
    overlap = len(a_bigrams & b_bigrams)
    
    dice_coeff = overlap * 2.0 / (len(a_bigrams) + len(b_bigrams))
    return dice_coeff


if __name__ == '__main__':
    print(dice_coefficient('mahen', 'mahendra'))
