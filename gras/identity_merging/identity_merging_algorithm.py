import csv
import string

import numpy as np
import pandas as pd

from gras.identity_merging.utils import normalised_levenshtein

TERMS = ["jr", "junior", "senior", "sr", "2nd", "ii", "iii", "iv", "v", "vi", "dr", "mr", "mrs", "ms", "phd", "prof",
         "professor", "miss", "mx", "sir", "mme", "msgr", "md", "server", "fake", "none", "null", "anonymous",
         "support", "admin", "unknown", "root", "nobody", "ubuntu", "(no author)", "system", "<blank>", "user"]


class Contributor:
    def __init__(self, name_email):
        print(name_email)

        self.name = self.__normalise_str(name_email.split('<')[0].strip()).lower()
        self.first = self.__normalise_str(self.name.split()[0]).lower()
        self.last = self.__normalise_str(self.name.split()[-1]).lower()
        email = name_email[name_email.index('<') + 1:name_email.index('>')]
        self.prefix = self.__normalise_str(email.split('@')[0]).lower()

    @staticmethod
    def __normalise_str(str_):
        str_ = str_.strip().lower()
        str_ = str_.translate(str.maketrans("", "", string.punctuation)).replace("\\'", "")
        return " ".join([x for x in str_.split() if x not in TERMS]).strip()


class IMA:
    def __init__(self, path):
        self.path = path
        self.process()

    def process(self):
        """
        name-name
        max-title = max(first-first, last-last)
        max-inverse = max(first-last, last-first)
        prefix-prefix
        max-prefix = max(first-prefix, prefix-first, last-prefix, prefix-last, name-prefix, prefix-name)
        domain-domain
        """
        columns = ['author 1', 'author 2', 'name-name', 'max-title', 'max-inverse', 'prefix-prefix', 'max-prefix',
                   'average', 'ima-result', 'result']
        table = []

        predicted = []
        actual = []

        with open(self.path, 'r') as fp:
            reader = csv.reader(fp)
            for row in reader:
                row[-1] = int(row[-1])
                data = []

                c1 = Contributor(name_email=row[0])
                c2 = Contributor(name_email=row[1])

                data.append(row[0])
                data.append(row[1])

                data.append(normalised_levenshtein(c1.name, c2.name))
                data.append(sum([normalised_levenshtein(c1.first, c2.first),
                                 normalised_levenshtein(c1.last, c2.last)]) / 2)
                data.append(sum([normalised_levenshtein(c1.first, c2.last),
                                 normalised_levenshtein(c1.last, c2.first)]) / 2)
                data.append(normalised_levenshtein(c1.prefix, c2.prefix))
                data.append(max(normalised_levenshtein(c1.first, c2.prefix),
                                normalised_levenshtein(c1.prefix, c2.first),
                                normalised_levenshtein(c1.last, c2.prefix),
                                normalised_levenshtein(c1.prefix, c2.last),
                                normalised_levenshtein(c1.name, c2.prefix),
                                normalised_levenshtein(c1.prefix, c2.name)))

                lst = [x for x in data[2:] if x is not None]
                average = sum(lst) / len(lst)

                data.append(average)

                if average > 0.5:
                    data.append(1)
                else:
                    data.append(0)

                predicted.append(data[-1])
                actual.append(row[-1])

                data.append(row[-1])
                table.append(data)

        df = pd.DataFrame(np.asarray(table), columns=columns)
        df.to_csv('result.csv', index=False)

        self.evaluate(predicted, actual)

    @staticmethod
    def evaluate(predicted, actual):
        tp, tn, fp, fn = 0, 0, 0, 0

        for i in range(len(predicted)):
            if predicted[i] == actual[i] == 0:
                tn += 1
            elif predicted[i] == actual[i] == 1:
                tp += 1
            elif predicted[i] == 1 and actual[i] == 0:
                fp += 1
            else:
                fn += 1

        print("PRECISION:", tp / (tp + fp))
        print("RECALL:", tp / (tp + fn))
        print("ACCURACY:", (tp + tn) / len(actual))


if __name__ == '__main__':
    IMA('test_data.csv')
