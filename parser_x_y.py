import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt
import math
import sys
import os

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class Vehicle:
    def __init__(self, id=0, x=0, speed=0, y=0):
        """
        Initialize a Vehicle object.
        :param position: The position of the vehicle (default is 0).
        :param speed: The speed of the vehicle (default is 0).
        """
        self.id = id
        self.x = x
        self.speed = speed
        self.y = y
class Link:
    def __init__(self, car1, car2, timestep):
        self.car1 = car1
        self.car2 = car2
        self.timestep = timestep

def get_max_num_vehicles(config_file):
    tree = ET.parse(config_file)
    root = tree.getroot()
    

    max_vehicles = root.find("max-num-vehicles")
    if max_vehicles is not None:
        return int(max_vehicles.get("value"))  # Convert to integer
    
    return None  # Return None if not found


sumo_folder = sys.argv[1]
# Parse the XML file
tree = ET.parse(f'{sumo_folder}/cars.xml')
root = tree.getroot()
links = []
max_vehicles = get_max_num_vehicles(f"{sumo_folder}/osm.sumocfg")
# Create folder only if it doesn't exist
os.makedirs(f"cars/cars{max_vehicles}", exist_ok=True)

# Iterate through the XML elements
for timestep in root.findall('timestep'):
    if (float(timestep.get("time")) <= 100 and float(timestep.get("time")) % 5.00 == 0.00):    
        with open(f"graphs/graph{timestep.get("time")}.txt", "w") as file, open(f"cars/cars{max_vehicles}/cars{timestep.get("time")}.txt", "w") as cars:
            vehicles = timestep.findall('vehicle')
            # file.write(f"\nTime: {timestep.get("time")}\n\n")
            for i in range(0, len(vehicles)):
                orig_x = float(vehicles[i].get("x"))
                orig_y = float(vehicles[i].get("y"))
                velocity = float(vehicles[i].get("speed")) * math.cos(float(vehicles[i].get("angle")))
                car1 = Vehicle(id = vehicles[i].get('id')[3:], x=float(vehicles[i].get("x")), speed=round(velocity, 2), y=float(vehicles[i].get("y")))
                cars.write(f"{car1.id} {car1.x} {car1.y} {car1.speed}\n")
                for j in range(i + 1, len(vehicles)):
                    neighbor_x = float(vehicles[j].get("x"))
                    neighbor_y = float(vehicles[j].get("y"))

                    distance = euclidean_distance(orig_x, orig_y, neighbor_x, neighbor_y)
                    
                    if distance < 100.0:
                        # add edge on graph between node v1 and v2
                        velocity = float(vehicles[j].get("speed")) * math.cos(float(vehicles[j].get("angle")))
                        car2 = Vehicle(id = vehicles[j].get('id')[3:], x=float(vehicles[j].get("x")), speed=round(velocity, 2), y=float(vehicles[j].get("y")))
                        # file.write(f"{car1.id}-{car2.id}\n")
                        link = Link(car1.id, car2.id, timestep)
                        links.append(link)
                        
                    
                    # for v1 in lane.findall('vehicle'):
                    #     for v2 in lane.findall('vehicle'):
                    #         if abs(float(v1.get("pos")) - float(v2.get("pos"))) <= 250 and v1.get('id') != v2.get('id'):
                    #             # add edge on graph between node v1 and v2
                    #             car1 = Vehicle(id = v1.get('id'), pos=float(v1.get("pos")), speed=float(v1.get("speed")), edge=edge.get("id"))
                    #             car2 = Vehicle(id = v2.get('id'), pos=float(v2.get("pos")), speed=float(v2.get("speed")), edge=edge.get("id"))

               #             G.add_edge(car1, car2)

for timestep in root.findall('timestep'):
    if (float(timestep.get("time")) <= 100 and float(timestep.get("time")) % 5.00 == 0.00):  
        with open(f"cars/cars{max_vehicles}/cars{timestep.get("time")}.txt", "a") as cars:
            cars.write("\n")
            # print("length is :", len(links))
            for link in links:
                if link.timestep == timestep:
                    cars.write(f"{link.car1}-{link.car2}\n")

# Print nodes
# print("Nodes:", len(list(G.nodes)))


# Print edges
# print("Edges:", list(G.edges))
# print("\n")
