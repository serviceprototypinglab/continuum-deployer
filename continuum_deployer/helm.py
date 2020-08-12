import yaml

class Helm:
    
    def __init__(self):
        pass

    def parse(self, document):
        docs = yaml.load_all(document)

        for doc in docs:
            if doc['kind'] == "Deployment":
                print(yaml.dump(doc))
