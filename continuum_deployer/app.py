from continuum_deployer.helm import Helm

def main():

    stream = open('./charts/redis/redis.yaml', 'r')

    helm = Helm()
    helm.parse(stream)
    helm.printDeploymetsJson()

if __name__ == "__main__":
    # execute only if run as a script
    main()
