import random as rn

maps = [

    [['P', 'P', 'P', 'P', 'P'],
     ['P', 'I', 'P', 'P', 'P'],
     ['P', 'P', 'I', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P'], ],

    [['P', 'P', 'P', 'P', 'P'],
     ['P', 'I', 'P', 'P', 'P'],
     ['P', 'P', 'I', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P'],
     ['P', 'P', 'P', 'G', 'P'], ],

    [['P', 'P', 'P', 'I', 'P'],
     ['P', 'I', 'P', 'P', 'P'],
     ['P', 'P', 'I', 'P', 'P'],
     ['P', 'G', 'P', 'I', 'P'],
     ['P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'G', 'I', 'P'], ],

    [['P', 'P', 'P', 'P', 'P'],
     ['I', 'I', 'P', 'P', 'P'],
     ['P', 'G', 'I', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P'],
     ['P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P'], ],

    [['P', 'P', 'P', 'P', 'G'],
     ['P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'I', 'P', 'P'],
     ['P', 'P', 'I', 'I', 'P'],
     ['P', 'I', 'P', 'P', 'P'],
     ['G', 'P', 'P', 'I', 'P'], ],

    [['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'I', 'P'],
     ['P', 'I', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'I', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'I', 'P', 'P'],
     ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'I', 'I', 'I', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P'],
     ['P', 'P', 'P', 'I', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P']],
]


def generate_input(a_map, num_of_taxis: int):
    height = len(a_map)
    width = len(a_map[0])
    taxis = generate_taxis(a_map, height, width, num_of_taxis)
    passengers = generate_passengers(a_map, height, width)
    return {"map": a_map,
            "taxis": taxis,
            "passengers": passengers}


def generate_taxis(a_map, height, width, num_of_taxis: int):
    taxis = {}
    for i in range(num_of_taxis):
        while True:
            location = (rn.randint(0, height - 1), rn.randint(0, width - 1))
            if a_map[location[0]][location[1]] in ['P', 'G']:
                break
        fuel = rn.randint(height, height * 4)
        capacity = rn.randint(1, 3)
        taxis[f"taxi {i+1}"] = {"location": location,
                                "fuel": fuel,
                                "capacity": capacity
                                }
    return taxis


def generate_passengers(a_map, height, width):
    num_of_passengers = rn.randint((height + width) // 4, (height + width) // 3)
    passengers = {}
    names = rn.sample(
        ["Yossi", "Yael", "Dana", "Kobi", "Avi", "Noa", "John", "Dave", "Mohammad", "Sergei", "Nour", "Ali",
         "Janet", "Francois", "Greta", "Freyja", "Jacob", "Emma", "Meytal", "Oliver", "Roee", "Omer", "Omar",
         "Reema", "Gal", "Wolfgang", "Michael", "Efrat", "Iris", "Eitan", "Amir", "Khaled", "Jana", "Moshe",
         "Lian", "Irina", "Tamar", "Ayelet", "Uri", "Daniel"], num_of_passengers)
    for i in range(num_of_passengers):
        while True:
            location = (rn.randint(0, height - 1), rn.randint(0, width - 1))
            if a_map[location[0]][location[1]] in ['P', 'G']:
                break
        while True:
            destination = (rn.randint(0, height - 1), rn.randint(0, width - 1))
            if destination == location:
                continue
            if a_map[location[0]][location[1]] in ['P', 'G']:
                break
        passengers[names[i]] = {"location": location,
                                "destination": destination}
    return passengers



if __name__ == '__main__':
    one_taxi_inputs = []
    for a_map in maps:
        one_taxi_inputs.append(generate_input(a_map, 1))
    for element in one_taxi_inputs[0].items():
        print(element)



