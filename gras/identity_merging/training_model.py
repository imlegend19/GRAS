import csv
import re

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier

from gras.identity_merging.identity_miner import Alias
from gras.identity_merging.utils import CONTRIBUTOR_TEMPLATE, gen_count_dict, gen_feature_vector, read_csv


def generate_train_data():
    file = open("data/ground_truth.csv", "r")

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

        extensions = read_csv(path="data/domain_ext.csv")

        alias_1 = Alias(
            contributor_id=None,
            login=login_1,
            name=name_1,
            email=email_1,
            location=None,
            is_anonymous=1 if login_1 is None else 0,
            extensions=extensions
        )

        alias_2 = Alias(
            contributor_id=None,
            login=login_2,
            name=name_2,
            email=email_2,
            location=None,
            is_anonymous=1 if login_2 is None else 0,
            extensions=extensions
        )

        users.add(CONTRIBUTOR_TEMPLATE(name=alias_1.original_name, first_name=alias_1.first_name,
                                       last_name=alias_1.last_name, prefix=alias_1.prefix, domain=alias_1.domain))
        users.add(CONTRIBUTOR_TEMPLATE(name=alias_2.original_name, first_name=alias_2.first_name,
                                       last_name=alias_2.last_name, prefix=alias_2.prefix, domain=alias_2.domain))

        pairs.append((alias_1, alias_2, result))

    file.close()

    prefix_count, domain_count, first_count, last_count = gen_count_dict(users)

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
        fv = gen_feature_vector(c1=c1, c2=c2, label=label, prefix_count=prefix_count, first_count=first_count,
                                last_count=last_count, domain_count=domain_count)

        data.append(fv)

    df = pd.DataFrame(data=np.asarray(data), columns=columns)
    df.to_csv("train.csv", index=False)


def build_model():
    data = np.genfromtxt('data/train.csv', delimiter=',', skip_header=True, filling_values=-1)
    columns = np.loadtxt('data/train.csv', delimiter=',', max_rows=1, dtype=np.str).tolist()[:-1]

    y = data[:, -1]
    data = np.delete(data, -1, axis=1)

    df = pd.DataFrame(data, columns=columns)

    model = RandomForestClassifier(criterion='entropy', random_state=0, n_estimators=100)
    model.fit(df, y)

    dump(model, 'data/rf-model.pkl')


if __name__ == '__main__':
    build_model()
