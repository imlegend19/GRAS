import csv
from collections import Counter, namedtuple

import numpy as np
from numpy import nan

CONTRIBUTOR_TEMPLATE = namedtuple("Contributor", ["name", "first_name", "last_name", "prefix", "domain"])


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
        nan
    """
    if string_1 == string_2:
        return 1

    len_1 = len(string_1)
    len_2 = len(string_2)

    if len_1 == 0 or len_2 == 0:
        return nan

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
        nan
    """
    if string_1 is None or string_2 is None:
        return nan

    if not string_1.strip() or not string_2.strip():
        return nan

    if string_1 == string_2:
        return 1

    len_1 = len(string_1)
    len_2 = len(string_2)

    if len_1 == 0 or len_2 == 0:
        return nan

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
    if string_1 is None or string_2 is None or len(string_1.split()) == 0:
        return nan

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


def read_csv(path):
    ext = []

    file = open(path)
    reader = csv.reader(file)
    for row in reader:
        ext.append(row[0])

    file.close()

    return ext


def frequency_score(o1, o2, dic):
    try:
        if dic[o1] != 0 and dic[o2] != 0:
            den = np.log10(dic[o1] * dic[o2])
            if den == 0:
                return 1
            else:
                return 1 / den
        else:
            return -1
    except KeyError:
        return -1


def gen_count_dict(users):
    prefixes, domains, firsts, lasts = [], [], [], []

    for u in users:
        if u.prefix:
            prefixes.append(u.prefix)

        if u.domain:
            domains.append(u.domain_ref)

        if u.first_name:
            firsts.append(u.first_name)

        if u.last_name:
            lasts.append(u.last_name)

    prefix_count = dict(Counter(prefixes))
    domain_count = dict(Counter(domains))
    first_count = dict(Counter(firsts))
    last_count = dict(Counter(lasts))

    return prefix_count, domain_count, first_count, last_count


def gen_feature_vector(c1, c2, prefix_count, first_count, last_count, domain_count, label=None):
    """
    Generates a feature vector for 2 aliases

    :param c1: Contributor 1
    :type c1: Alias
    :param c2: Contributor 2
    :type c2: Alias
    :param prefix_count: Prefix count dictionary
    :type prefix_count: dict
    :param first_count: First name count dictionary
    :type first_count: dict
    :param last_count: Last Name count dictionary
    :type last_count: dict
    :param domain_count: Domain count dictionary
    :type domain_count: dict
    :param label: 0 or 1 whether the contributors are same or not
    :type label: int

    :return: Feature Vector
    :rtype: list
    """

    fv = [
        damerau_levenshtein(c1.login, c2.login),
        damerau_levenshtein(c1.name, c2.name),
        damerau_levenshtein(c1.first_name, c2.first_name),
        damerau_levenshtein(c1.last_name, c2.last_name),
        damerau_levenshtein(c1.prefix, c2.prefix),
        damerau_levenshtein(c1.domain, c2.domain),
        damerau_levenshtein(c1.login, c2.name),
        damerau_levenshtein(c1.name, c2.login),
        damerau_levenshtein(c1.first_name, c2.last_name),
        damerau_levenshtein(c1.last_name, c2.first_name),
        damerau_levenshtein(c1.login, c2.prefix),
        damerau_levenshtein(c1.prefix, c2.login),
        damerau_levenshtein(c1.domain_ref, c2.name),
        damerau_levenshtein(c1.name, c2.domain_ref),
        damerau_levenshtein(c1.domain_ref, c2.login),
        damerau_levenshtein(c1.login, c2.domain_ref),
        frequency_score(c1.first_name, c2.first_name, first_count),
        frequency_score(c2.last_name, c2.last_name, last_count),
        frequency_score(c1.prefix, c2.prefix, prefix_count),
        frequency_score(c1.domain, c2.domain, domain_count)
    ]

    if label:
        fv.append(label)

    return fv
