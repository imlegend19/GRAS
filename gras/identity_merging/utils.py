import numpy as np


def normalised_levenshtein(s1, s2):
    """
    Calculate the Levenshtein distance (or Edit distance) of 2 strings. This is an efficient iterative
    implementation of the algorithm.
    
    :param s1: s1 string
    :type s1: str
    
    :param s2: s2 string
    :type s2: str
    
    :return: 1 - distance(s1, s2) / max(len(s1), len(s2))
    :rtype: float
    """
    
    if s1 == s2:
        return 1
    
    if len(s1) == 0 or len(s2) == 0:
        return 0
    
    m, n = len(s1), len(s2)
    
    v1 = np.zeros(n + 1)
    v2 = np.zeros(n + 1)
    
    for i in range(n + 1):
        v1[i] = i
    
    for i in range(m):
        v2[0] = i + 1
        for j in range(n):
            deletion_cost = v1[j + 1] + 1
            insertion_cost = v2[j] + 1
            
            if s1[i] == s2[j]:
                substitution_cost = v1[j]
            else:
                substitution_cost = v1[j] + 1
            
            v2[j + 1] = min(deletion_cost, insertion_cost, substitution_cost)
        
        v1, v2 = v2, v1
    
    return 1 - v1[n] / max(n, m)


def jaro_winkler(s1, s2, scaling=0.1):
    m, n = len(s1), len(s2)
    shorter, longer = s1, s2
    
    if m > n:
        shorter, longer = longer, shorter
    
    mc1 = _get_matching_characters(shorter, longer)
    mc2 = _get_matching_characters(longer, shorter)
    
    if len(mc1) == 0 or len(mc2) == 0:
        score = 0
    else:
        score = (float(len(mc1)) / len(shorter) + float(len(mc2)) / len(longer) +
                 float(len(mc1) - _transpositions(mc1, mc2)) / len(mc1)) / 3.0
    
    index_ = None
    
    if s1 == s2:
        index_ = -1
    elif not s1 or not s2:
        index_ = 0
    else:
        max_len = min(m, n)
        for i in range(max_len):
            if not s1[i] == s2[i]:
                index_ = i
                break
        
        if not index_:
            index_ = max_len
    
    if index_ == -1:
        cl = s1
    elif index_ == 0:
        cl = ''
    else:
        cl = s1[:index_]
    
    cl = min(len(cl), 4)
    return round((score + (scaling * cl * (1 - score))) * 100) / 100


def _transpositions(s1, s2):
    return np.floor(len([(f, s) for f, s in zip(s1, s2) if not f == s]) / 2.0)


def _get_matching_characters(s1, s2):
    common = []
    limit = np.floor(min(len(s1), len(s2)) / 2)
    
    for i, l in enumerate(s1):
        left, right = int(max(0, i - limit)), int(min(i + limit + 1, len(s2)))
        if l in s2[left:right]:
            common.append(l)
            s2 = s2[:s2.index(l)] + '*' + s2[s2.index(l) + 1:]
    
    return ''.join(common)
