import os
import csv


class BaseCar:
    def __init__(self, car_type, brand, photo_file_name, carrying):
        self.car_type = car_type
        self.photo_file_name = photo_file_name
        self.brand = brand
        self.carrying = carrying

    def get_photo_file_ext(self):
        return os.path.splitext(self.photo_file_name)[1]


class Car(BaseCar):
    def __init__(self, passenger_seats_count, **kwargs):
        super(Car, self).__init__(**kwargs)
        self.passenger_seats_count = passenger_seats_count


class Truck(BaseCar):
    def __init__(self, body_whl, **kwargs):
        super(Truck, self).__init__(**kwargs)

        truck_params = body_whl.split('x')

        body_length = float(0)
        body_height = float(0)
        body_width = float(0)

        if len(truck_params) == 3:
            body_length = float(truck_params[0])
            body_width = float(truck_params[1])
            body_height = float(truck_params[2])

        self.body_length = body_length
        self.body_width = body_width
        self.body_height = body_height

    def get_body_volume(self):
        return self.body_width * self.body_length * self.body_height


class SpecMachine(BaseCar):
    def __init__(self, extra, **kwargs):
        super(SpecMachine, self).__init__(**kwargs)
        self.extra = extra


class CarFactory:
    @staticmethod
    def create_car(car_type, *args):
        brand = args[1]
        carrying = args[5]

        if len(brand) == 0:
            raise ValueError('Required attribute brand is not defined')

        if len(carrying) == 0:
            raise ValueError('Required attribute carrying is not defined.')

        if car_type == 'car':
            passenger_seats_count = args[2]
            print(passenger_seats_count)
            if passenger_seats_count is None:
                raise ValueError('passenger_seats_count должно быть целым числом.')

            return Car(
                car_type=car_type,
                brand=brand,
                photo_file_name=args[3],
                carrying=carrying,
                passenger_seats_count=int(passenger_seats_count)
            )
        elif car_type == 'truck':
            return Truck(
                car_type=car_type,
                brand=args[1],
                photo_file_name=args[3],
                carrying=args[5],
                body_whl=args[4]
            )
        elif car_type == 'spec_machine':
            return SpecMachine(
                car_type=car_type,
                brand=args[1],
                photo_file_name=args[3],
                carrying=args[5],
                extra=args[6]
            )

        return None


def get_car_list(csv_filename):
    car_list = list()

    with open(csv_filename, encoding='utf-8') as csv_file:
        cars_reader = csv.reader(csv_file, delimiter=';')
        next(cars_reader)

        for row in cars_reader:
            if len(row):
                car_type = row[0]
                if len(car_type):
                    try:
                        car_instance = CarFactory.create_car(car_type, *row)
                        car_list.append(car_instance)
                    except ValueError as error:
                        print(error)
                    except NameError as name_error:
                        print(name_error)

    return car_list


if __name__ == '__main__':
    cars = get_car_list('./cars.csv')
    print(cars)