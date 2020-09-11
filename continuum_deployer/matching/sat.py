import click

from continuum_deployer.resources.resource_entity import ResourceEntity
from ortools.sat.python import cp_model


from continuum_deployer.matching.matcher import Matcher
from continuum_deployer.deployment import DeploymentEntity
from continuum_deployer.resources.resources import Resources, ResourceEntity


class SAT(Matcher):

    CPU_SCALE_FACTOR = 10e2

    def __init__(self,
                 deployment_entities: DeploymentEntity,
                 resources: Resources):
        super().__init__(deployment_entities, resources)
        self.model = cp_model.CpModel()

    @staticmethod
    def scale_cpu_values(entities, idle=False):
        result = list()
        for entity in entities:
            if idle:
                result.append(
                    int(entity.get_idle_cpu()*SAT.CPU_SCALE_FACTOR))
            else:
                result.append(int(entity.cpu*SAT.CPU_SCALE_FACTOR))
        return result

    @staticmethod
    def get_deployment_names(deployments):
        _result = []
        for deployment in deployments:
            _result.append(deployment.name)
        return _result

    def do_matching(self, deployment_entities, resources):

        _res_scaled_cpu = SAT.scale_cpu_values(resources, idle=True)
        _dep_scaled_cpu = SAT.scale_cpu_values(deployment_entities)

        iter_resources = range(len(_res_scaled_cpu))
        iter_deployment = range(len(_dep_scaled_cpu))

        # Variables
        x = []
        for i in iter_resources:
            t = []
            for j in iter_deployment:
                t.append(self.model.NewBoolVar('x[%i,%i]' % (i, j)))
            x.append(t)

        # Constraints

        # Each task is assigned to exactly one worker.
        [self.model.Add(sum(x[i][j] for i in iter_resources) == 1)
         for j in iter_deployment]

        # Each node is not overcommitted
        for i in iter_resources:
            self.model.Add(sum(_dep_scaled_cpu[j] * x[i][j]
                               for j in iter_deployment) <= _res_scaled_cpu[i])
            self.model.Add(sum(ent.memory * x[i][j]
                               for j, ent in enumerate(deployment_entities)) <= resources[i].get_idle_memory())

        # Objective: overall idle resources
        idle_cpu = self.model.NewIntVar(
            0, sum(_res_scaled_cpu[i] for i in iter_resources), 'idle_cpu')
        idle_ram = self.model.NewIntVar(
            0, sum(res.get_idle_memory() for i, res in enumerate(resources)), 'idle_ram')
        self.model.Add(idle_cpu == sum(_res_scaled_cpu[i] for i in iter_resources) - sum(
            x[i][j] * _dep_scaled_cpu[j] for j in iter_deployment for i in iter_resources))
        self.model.Add(idle_ram == sum(res.get_idle_memory() for i, res in enumerate(resources)) - sum(
            x[i][j] * dep.memory for j, dep in enumerate(deployment_entities) for i in iter_resources))

        self.model.Maximize(idle_cpu)
        self.model.Maximize(idle_ram)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL:
            print('Total idle resources = %i' % solver.ObjectiveValue())

            for i, res in enumerate(resources):
                for j, dep in enumerate(deployment_entities):
                    if solver.Value(x[i][j]) == 1:
                        res.add_deployment(dep)
        elif status == cp_model.INFEASIBLE:
            _names = SAT.get_deployment_names(deployment_entities)
            click.echo(click.style(
                '[Error] Deployments entity ({}) '
                'not schedulable with SAT solver in '
                'resource group due to infeasibility.'.format(_names), fg='red'), err=True)

        print(solver.ResponseStats())

    def match(self):
        super(SAT, self).match()
