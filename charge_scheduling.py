from datetime import datetime, timedelta

"""This model implements a vehicle charge scheduling problem.

    Routing Constraints:
    - max moving time per vehicle <= 6h
    - max charging time per vehicle <= 2h
    - min charging time per vehicle >= 30m (soft)
    
    Base Constraints:
    - arrived time
    - ready time
    - vehicle charge to 50% = 20m
    - vehicle charge to 80% = 40m
    - vehicle charge to 100 = 75m
    - vehicle battery capacity = 60kWh
    -
"""
battery_capacity = input("Enter current amount of battery in percent: ")
car_arrived_time = input("Car arrived time to supercharging station in format H::M::S: ")

# time preconditions
# example = '13::55::26'
# time_object = datetime.strptime(example, '%H::%M::%S').time()
time_format = '%H::%M::%S'


def get_total_charging_time(current_battery_capacity_in_percent: int) -> int:  # in minutes
    multiplier_50 = 20 / 50
    multiplier_80 = 40 / 30
    multiplier_100 = 75 / 20

    if current_battery_capacity_in_percent < 50:
        result = (50 - current_battery_capacity_in_percent) * multiplier_50 + 40 + 75
    elif current_battery_capacity_in_percent < 80:
        result = (80 - current_battery_capacity_in_percent) * multiplier_80 + 75
    else:
        result = (100 - current_battery_capacity_in_percent) * multiplier_100

    return result


def main():
    charging_time = timedelta(minutes=get_total_charging_time(int(battery_capacity)))
    arrived_time = datetime.strptime(car_arrived_time, time_format)
    ready_time = arrived_time + charging_time

    print('Charging will be finished at', ready_time.time())


if __name__ == '__main__':
    main()
