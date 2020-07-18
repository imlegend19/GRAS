from bs4 import BeautifulSoup
import json


def parse_description(desc):
    class_name = desc.find("pre").find("span").string
    doc = desc.find_all("div", attrs={"class": "block"})[0].text.replace("\n", " ").strip()

    return class_name, doc


def parse_details(det):
    method_details = det.find("section").find("ul").find("li")

    methods = {}
    for method in method_details.find_all("ul", attrs={"class": "blockList"}):
        name = method.find("h4").string
        doc = method.find_all("div", attrs={"class": "block"})[0].text.replace("\n", " ")

        methods[name] = " ".join(doc.split()).strip()

    return methods


def parse_javadoc(path):
    javadoc = open(path).read()
    soup = BeautifulSoup(javadoc, "lxml")

    content = soup.find(role="main").find_all("div", attrs={"class": "contentContainer"})[0]

    description = content.find_all("div", attrs={"class": "description"})[0]
    details = content.find_all("div", attrs={"class": "details"})[0]

    name, desc = parse_description(description)
    methods = json.dumps(parse_details(details), indent=4)

    return name, {
        "desc": desc,
        "methods": methods
    }


def parse_jar(path):
    ...

if __name__ == '__main__':
    parse_javadoc("/home/mahen/PycharmProjects/GRAS/tests/data/java/javadoc/ApplicationArguments.html")
