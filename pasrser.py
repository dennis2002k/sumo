import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt

class Vehicle:
    def __init__(self, id=0, pos=0, speed=0, edge=0):
        """
        Initialize a Vehicle object.
        :param position: The position of the vehicle (default is 0).
        :param speed: The speed of the vehicle (default is 0).
        """
        self.id = id
        self.pos = pos
        self.speed = speed
        self.edge = edge

G = nx.Graph()
# Parse the XML file
tree = ET.parse('cars.xml')
root = tree.getroot()

# Iterate through the XML elements
for timestep in root.findall('timestep'):
    if (float(timestep.get("time")) <= 40.00):
        for edge in timestep.findall("edge"):
            for lane in edge.findall("lane"):
                vehicles = lane.findall('vehicle')
                for i in range(0, len(vehicles)):
                    for j in range(i + 1, len(vehicles)):
                        if abs(float(vehicles[i].get("pos")) - float(vehicles[j].get("pos"))) <= 250 and vehicles[i].get('id') != vehicles[j].get('id'):
                            # add edge on graph between node v1 and v2
                            car1 = Vehicle(id = vehicles[i].get('id'), pos=float(vehicles[i].get("pos")), speed=float(vehicles[i].get("speed")), edge=edge.get("id"))
                            car2 = Vehicle(id = vehicles[j].get('id'), pos=float(vehicles[j].get("pos")), speed=float(vehicles[j].get("speed")), edge=edge.get("id"))
                            G.add_edge(car1, car2)


                # for v1 in lane.findall('vehicle'):
                #     for v2 in lane.findall('vehicle'):
                #         if abs(float(v1.get("pos")) - float(v2.get("pos"))) <= 250 and v1.get('id') != v2.get('id'):
                #             # add edge on graph between node v1 and v2
                #             car1 = Vehicle(id = v1.get('id'), pos=float(v1.get("pos")), speed=float(v1.get("speed")), edge=edge.get("id"))
                #             car2 = Vehicle(id = v2.get('id'), pos=float(v2.get("pos")), speed=float(v2.get("speed")), edge=edge.get("id"))
                #             G.add_edge(car1, car2)


# Print nodes
# print("Nodes:", len(list(G.nodes)))
print("\n")
for node in G.nodes:
    print("Car in edge: ", node.edge, "with position: ", node.pos, " speed: ", node.speed, "and id: ", node.id , "\n")

# Print edges
# print("Edges:", list(G.edges))
# print("\n")
