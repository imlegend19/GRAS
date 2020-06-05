import numpy as np
import pandas as pd
from collections import namedtuple, Counter
import csv
import re
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

from gras.identity_merging.identity_miner import Alias
from gras.identity_merging.utils import damerau_levenshtein as dl, get_domain_extensions


def frequency_score(o1, o2, dic):
    try:
        if dic[o1] != 0 and dic[o2] != 0:
            den = np.log10(dic[o1] * dic[o2])
            if den == 0:
                return 1
            else:
                return 1 / den
        else:
            return '?'
    except KeyError:
        return '?'


def generate_train_data():
    file = open("data/ground_truth.csv", "r")

    cont = namedtuple("Cont", ["name", "first_name", "last_name", "prefix", "domain"])

    pairs = []
    users = set()

    reader = csv.reader(file)
    for row in reader:
        if reader.line_num == 1:
            continue

        row = [int(x) if x.isdigit() else x if x else None for x in row]
        login_1, name_email_1, login_2, name_email_2, result = row

        pattern = re.compile(r'(?<=<)(.*?)(?=>)')

        name_1 = name_email_1.split('<')[0]
        email_1 = pattern.search(name_email_1).group(0)

        if email_1 == "None":
            email_1 = None

        name_2 = name_email_2.split('<')[0]
        email_2 = pattern.search(name_email_2).group(0)

        if email_2 == "None":
            email_2 = None

        extensions = get_domain_extensions(path="data/domain_ext.csv")

        alias_1 = Alias(
            id_=None,
            login=login_1,
            name=name_1,
            email=email_1,
            location=None,
            is_anonymous=1 if login_1 is None else 0,
            extensions=extensions
        )

        alias_2 = Alias(
            id_=None,
            login=login_2,
            name=name_2,
            email=email_2,
            location=None,
            is_anonymous=1 if login_2 is None else 0,
            extensions=extensions
        )

        users.add(cont(name=alias_1.original_name, first_name=alias_1.first_name, last_name=alias_1.last_name,
                       prefix=alias_1.prefix, domain=alias_1.domain))
        users.add(cont(name=alias_2.original_name, first_name=alias_2.first_name, last_name=alias_2.last_name,
                       prefix=alias_2.prefix, domain=alias_2.domain))

        pairs.append((alias_1, alias_2, result))

    file.close()

    prefixes, domains, firsts, lasts = [], [], [], []

    for u in users:
        prefixes.append(u.prefix)
        domains.append(u.domain)
        firsts.append(u.first_name)
        lasts.append(u.last_name)

    prefix_count = dict(Counter(prefixes))
    domain_count = dict(Counter(domains))
    first_count = dict(Counter(firsts))
    last_count = dict(Counter(lasts))

    data = []

    columns = [
        "login-login",
        "name-name",
        "first-first",
        "last-last",
        "prefix-prefix",
        "domain-domain",
        "login-name",
        "name-login",
        "first-last",
        "last-first",
        "login-prefix",
        "prefix-login",
        "domref-name",
        "name-domref",
        "domref-login",
        "login-domref",
        "first-freq-score",
        "last-freq-score",
        "prefix-freq-score",
        "domain-freq-score",
        "label"
    ]

    for p in pairs:
        c1, c2, label = p
        fv = [
            dl(c1.login, c2.login),
            dl(c1.name, c2.name),
            dl(c1.first_name, c2.first_name),
            dl(c1.last_name, c2.last_name),
            dl(c1.prefix, c2.prefix),
            dl(c1.domain, c2.domain),
            dl(c1.login, c2.name),
            dl(c1.name, c2.login),
            dl(c1.first_name, c2.last_name),
            dl(c1.last_name, c2.first_name),
            dl(c1.login, c2.prefix),
            dl(c1.prefix, c2.login),
            dl(c1.domain_ref, c2.name),
            dl(c1.name, c2.domain_ref),
            dl(c1.domain_ref, c2.login),
            dl(c1.login, c2.domain_ref),
            frequency_score(c1.first_name, c2.first_name, first_count),
            frequency_score(c2.last_name, c2.last_name, last_count),
            frequency_score(c1.prefix, c2.prefix, prefix_count),
            frequency_score(c1.domain, c2.domain, domain_count),
            label
        ]

        data.append(fv)

    df = pd.DataFrame(data=np.asarray(data), columns=columns)
    df.to_csv("train.csv", index=False)


def build_model():
    data = np.genfromtxt('train.csv', delimiter=',', skip_header=True, filling_values=0)
    columns = np.loadtxt('train.csv', delimiter=',', max_rows=1, dtype=np.str).tolist()[:-1]

    y = data[:, -1]
    data = np.delete(data, -1, axis=1)

    df = pd.DataFrame(data, columns=columns)
    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2)

    print(X_train.shape, y_train.shape)
    print(X_test.shape, y_test.shape)

    model = DecisionTreeClassifier(criterion='entropy', splitter='best', random_state=0)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(model.score(X_test, y_test))


if __name__ == '__main__':
    build_model()
