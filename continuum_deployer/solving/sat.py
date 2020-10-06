import click

from continuum_deployer.resources.resource_entity import ResourceEntity
from ortools.sat.python import cp_model


from continuum_deployer.solving.solver import Solver
from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.resources.resources import Resources, ResourceEntity
from continuum_deployer.utils.config import Config, Setting, SettingValue


class SAT(Solver):

    CPU_SCALE_FACTOR = 10e2

    def __init__(self,
                 deployment_entities: DeploymentEntity,
                 resources: Resources):
        super().__init__(deployment_entities, resources)

    @staticmethod
    def scale_cpu_values(entities, idle=False):
        """Helper function that scales cpu values to integers.
        Necessary for the digestion trough the CP-SAT solver.

        :param entities: list of entities with cpu values that should be scaled
        :type entities: list
        :param idle: flag to decided if entities idle cpu should be scaled, defaults to False
        :type idle: bool, optional
        :return: list of scaled cpu values
        :rtype: list
        """
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

    def _gen_config(self):
        return Config([
            Setting('target', [
                SettingValue(
                    'max_idle_cpu', description='SAT solver tries to maximize idle cpu resources', default=True),
                SettingValue(
                    'max_idle_memory', description='SAT solver tries to maximize idle memory resources'),
                SettingValue(
                    'min_idle_cpu', description='SAT solver tries to minimize idle cpu resources'),
                SettingValue(
                    'min_idle_memory', description='SAT solver tries to minimize idle memory resources'),
                SettingValue(
                    'min_idle_resources', description='SAT solver tries to minimize idle resources (cpu+memory)'),
                SettingValue(
                    'max_idle_resources', description='SAT solver tries to maximize idle resources (cpu+memory)'),
            ])
        ])

    def do_matching(self, deployment_entities, resources):
        """Actual solver implementation. Uses constraint programming to find an optimal solution
        for the deployment placing task.

        :param deployment_entities: list of :class:`continuum_deployer.resources.deployment.DeploymentEntity` objects to place
        :type deployment_entities: list
        :param resources: list of :class:`continuum_deployer.resources.resource_entity.ResourceEntity` object to fill with deployments
        :type resources: list
        """

        _model = cp_model.CpModel()

        _res_scaled_cpu = SAT.scale_cpu_values(resources, idle=True)
        _dep_scaled_cpu = SAT.scale_cpu_values(deployment_entities)

        iter_resources = range(len(_res_scaled_cpu))
        iter_deployment = range(len(_dep_scaled_cpu))

        # Variables
        x = []
        for i in iter_resources:
            t = []
            for j in iter_deployment:
                t.append(_model.NewBoolVar('x[%i,%i]' % (i, j)))
            x.append(t)

        # Constraints

        # Each task is assigned to exactly one worker.
        [_model.Add(sum(x[i][j] for i in iter_resources) == 1)
         for j in iter_deployment]

        # Each node is not overcommitted
        for i in iter_resources:
            _model.Add(sum(_dep_scaled_cpu[j] * x[i][j]
                           for j in iter_deployment) <= _res_scaled_cpu[i])
            _model.Add(sum(ent.memory * x[i][j]
                           for j, ent in enumerate(deployment_entities)) <= resources[i].get_idle_memory())

        # Objective: overall idle resources
        idle_cpu = _model.NewIntVar(
            0, sum(_res_scaled_cpu[i] for i in iter_resources), 'idle_cpu')
        idle_ram = _model.NewIntVar(
            0, sum(res.get_idle_memory() for i, res in enumerate(resources)), 'idle_ram')
        _model.Add(idle_cpu == sum(_res_scaled_cpu[i] for i in iter_resources) - sum(
            x[i][j] * _dep_scaled_cpu[j] for j in iter_deployment for i in iter_resources))
        _model.Add(idle_ram == sum(res.get_idle_memory() for i, res in enumerate(resources)) - sum(
            x[i][j] * dep.memory for j, dep in enumerate(deployment_entities) for i in iter_resources))

        # read config and set optimization target
        _target = self.config.get_setting('target').get_value().value
        if _target == 'max_idle_cpu':
            _model.Maximize(idle_cpu)
        elif _target == 'max_idle_memory':
            _model.Maximize(idle_ram)
        elif _target == 'min_idle_cpu':
            _model.Minimize(idle_cpu)
        elif _target == 'min_idle_memory':
            _model.Minimize(idle_ram)
        elif _target == 'min_idle_resources':
            _model.Minimize(idle_ram)
            _model.Minimize(idle_cpu)
        elif _target == 'max_idle_resources':
            _model.Maximize(idle_ram)
            _model.Maximize(idle_cpu)

        solver = cp_model.CpSolver()
        status = solver.Solve(_model)

        if status == cp_model.OPTIMAL:
            for i, res in enumerate(resources):
                for j, dep in enumerate(deployment_entities):
                    if solver.Value(x[i][j]) == 1:
                        res.add_deployment(dep)
        elif status == cp_model.INFEASIBLE:
            self.placement_errors = deployment_entities

        print(solver.ResponseStats())

    def match(self):
        super(SAT, self).match()
