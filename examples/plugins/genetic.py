from continuum_deployer.solving.solver import Solver


class Genetic(Solver):

    def do_matching(self, deployment_entities, resources):
        raise NotImplementedError
