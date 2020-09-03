from __future__ import print_function
from ortools.sat.python import cp_model


def main():
    # Instantiate a cp model.
    node_cpu = [2, 3, 5, 1]

    task_cpu = [2, 3, 2, 2, 1]

    num_nodes = len(node_cpu)
    num_tasks = len(task_cpu)

    all_nodes = range(num_nodes)
    all_tasks = range(num_tasks)

    model = cp_model.CpModel()
    # Variables
    x = []
    for i in all_nodes:
        t = []
        for j in all_tasks:
            t.append(model.NewBoolVar('x[%i,%i]' % (i, j)))
        x.append(t)

    # Constraints

    # Each task is assigned to exactly one worker.
    [model.Add(sum(x[i][j] for i in all_nodes) == 1) for j in all_tasks]

    # Each node is not overcommitted
    for i in all_nodes:
        model.Add(sum(task_cpu[j] * x[i][j]
                      for j in all_tasks) <= node_cpu[i])

    # Objective: overall idle resources
    idle_cpu = model.NewIntVar(
        0, sum(node_cpu[i] for i in all_nodes), 'idle_cpu')
    model.Add(idle_cpu == sum(node_cpu[i] for i in all_nodes) - sum(x[i][j] * task_cpu[j]
                                                                    for j in all_tasks for i in all_nodes))
    model.Maximize(idle_cpu)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Total idle resources = %i' % solver.ObjectiveValue())
        print()
        for i in all_nodes:
            print('Worker ', i, ':')
            for j in all_tasks:
                if solver.Value(x[i][j]) == 1:
                    print('- task ', j)
            print()

        print()

    print(solver.ResponseStats())


if __name__ == '__main__':
    main()
