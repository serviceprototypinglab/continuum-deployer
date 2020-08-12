from helm import Helm

def main():

    # document = """
    # a: 1
    # b:
    #     c: 3
    #     d: 4
    # """

    stream = open('./misc/grafana-templated.yaml', 'r')

    helm = Helm()
    helm.parse(stream)

if __name__ == "__main__":
    # execute only if run as a script
    main()
