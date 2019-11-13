from __future__ import print_function
from ortools.sat.python import cp_model



class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, charge_schedules, num_vehicles, num_hours, num_chargers, sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._charge_schedules = charge_schedules
        self._num_vehicles = num_vehicles
        self._num_hours = num_hours
        self._num_chargers = num_chargers
        self._solutions = set(sols)
        self._solution_count = 0

    def on_solution_callback(self):
        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            for d in range(self._num_hours):
                print('Hour %i' % d)
                for n in range(self._num_vehicles):
                    is_working = False
                    for s in range(self._num_chargers):
                        if self.Value(self._charge_schedules[(n, d, s)]):
                            is_working = True
                            print('  Vehicle %i charges at charge station %i' % (n, s))
                    if not is_working:
                        print('  Vehicle {} procrastinates'.format(n))
            print()
        self._solution_count += 1

    def solution_count(self):
        return self._solution_count




def main():
    # Data.
    num_vehicles = 4
    num_chargers = 3
    num_hours = 24

    all_vehicles = range(num_vehicles)
    all_chargers = range(num_chargers)
    all_hours = range(num_hours)
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    charge_schedules = {}
    for v in all_vehicles:
        for h in all_hours:
            for c in all_chargers:
                charge_schedules[(v, h, c)] = model.NewBoolVar('charge_n%id%is%i' % (v, h, c))

    # Each charger is assigned to exactly one vehicle in the schedule period.
    for h in all_hours:
        for c in all_chargers:
            model.Add(sum(charge_schedules[(v, h, c)] for v in all_vehicles) == 1)

    # Each vehicle charges at most ones per hour.
    for v in all_vehicles:
        for h in all_hours:
            model.Add(sum(charge_schedules[(v, h, c)] for c in all_chargers) <= 1)

    # min_charger_per_vehicle is the largest integer such that every charger
    # can be assigned at least that many vehicles. If the number of vehicle doesn't
    # divide the total number of shifts over the schedule period,
    # some vehicles have to go to next charger, for a total of
    # min_charger_per_vehicle + 1.
    min_charger_per_vehicle = (num_chargers * num_hours) // num_vehicles
    max_charger_per_vehicle = min_charger_per_vehicle
    for n in all_vehicles:
        num_shifts_worked = sum(
            charge_schedules[(n, d, s)] for d in all_hours for s in all_chargers)
        model.Add(min_charger_per_vehicle <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_charger_per_vehicle)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # Display the first five solutions.
    a_few_solutions = range(5)
    solution_printer = NursesPartialSolutionPrinter(
        charge_schedules, num_vehicles, num_hours, num_chargers, a_few_solutions)
    solver.SearchForAllSolutions(model, solution_printer)

    # Statistics.
    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())


if __name__ == '__main__':
    main()
