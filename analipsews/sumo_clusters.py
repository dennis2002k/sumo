import traci
import webcolors
import xml.etree.ElementTree as ET
import math

class Cluster:
    def __init__(self, id, color: tuple, members=None):
        """Initialize a Claster with a color (R, G, B) and a list of members."""
        if not isinstance(color, tuple) or len(color) != 3:
            raise ValueError("Color must be a tuple with 3 values (R, G, B).")
        
        self.id = id
        self.color = color
        self.members = members if members is not None else []

    def add_member(self, member):
        self.members.append(member)

    def remove_member(self, member):
        if member in self.members:
            self.members.remove(member)

class Vehicle:
    def __init__(self, id=0, x=0, y=0, speed=0, angle=0):
        """
        Initialize a Vehicle object.
        :param position: The position of the vehicle (default is 0).
        :param speed: The speed of the vehicle (default is 0).
        """
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        

class Link:
    def __init__(self, car1, car2, timestep):
        self.car1 = car1
        self.car2 = car2
        self.timestep = timestep

def read_clusters(timestep):
    clusters = []
    with open(f"sumo/cars{timestep}0.sumo", "r") as file:
        for line in file:
            data = line.split()
            new_cluster = Cluster(data[0], webcolors.name_to_rgb(data[1]),members=data[2].split(","))
            clusters.append(new_cluster)
        return clusters

def read_links(timestep):
    links = []
    with open(f"../cars/cars{timestep}0.txt", "r") as file:
            lines = file.readlines()

    split_index = lines.index("\n") if "\n" in lines else len(lines)
    edges = [line.strip() for line in lines[split_index + 1:] if line.strip()]
    for edge in edges:
        new_edge = edge.split("-")
        links.append(Link(new_edge[0], new_edge[1], timestep))

    return links

def read_positions(curr_timestep, tree):
    root = tree.getroot()

    vehicles = []

    for timestep in root.findall('timestep'):
        if float(timestep.get("time")) > 100.0:
            break
        if float(timestep.get("time")) == curr_timestep: 
            for vehicle in timestep.findall('vehicle'):
                id = vehicle.get("id")
                x = vehicle.get("x")
                y = vehicle.get("y")
                speed = vehicle.get("speed")
                angle = vehicle.get("angle")
                # print("Timestep: ", timestep, "\n", id, x, y)
                vehicles.append(Vehicle(id, x, y, speed, angle))
    return vehicles

def clear_polys():
    # Clear all previous polygons before drawing new ones
    existing_polygons = traci.polygon.getIDList()
    for poly_id in existing_polygons:
        if "line_" in poly_id or "head_" in poly_id:  # Only remove our generated lines
            traci.polygon.remove(poly_id)

def draw_links(links, vehicles, timestep):
    
    for link in links:
        print(link.car1, link.car2)
        veh_a = next((v for v in vehicles if v.id == f"veh{link.car1}"), None)
        veh_b = next((v for v in vehicles if v.id == f"veh{link.car2}"), None)
        if veh_a == None or veh_b == None:
            continue
        pos_a = (float(veh_a.x), float(veh_a.y))
        pos_b = (float(veh_b.x), float(veh_b.y))

        line_poly = [pos_a, pos_b, (pos_b[0] + 0.1, pos_b[1] + 0.1), (pos_a[0] + 0.1, pos_a[1] + 0.1)]
                
        traci.polygon.add(polygonID=f"line_veh{link.car1}_veh{link.car2}_{timestep}", 
                            shape=line_poly, 
                            color=(255, 0, 0), 
                            layer=5, 
                            fill=True)

def rotate_point(px, py, cx, cy, angle):
    angle_rad = math.radians(angle)  # Convert angle to radians
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    # Rotate point (px, py) around (cx, cy)
    x_rot = cos_angle * (px - cx) - sin_angle * (py - cy) + cx
    y_rot = sin_angle * (px - cx) + cos_angle * (py - cy) + cy
    return x_rot, y_rot

def highlight_heads(clusters, vehicles, timestep):
    for cluster in clusters:
        veh_a = next((v for v in vehicles if v.id == f"veh{cluster.id}"), None)
        if veh_a == None:
            continue
        x = float(veh_a.x)
        y = float(veh_a.y)

        vehicle_size = (5.0, 2.0)
        position = (x, y)

        half_length = vehicle_size[0] / 2
        half_width = vehicle_size[1] / 2
    
    # Coordinates of the rectangle corners before rotation (local coordinates)
        corners = [
            (-vehicle_size[0], -half_width),  # Bottom-left corner
            (0, -half_width),   # Bottom-right corner
            (0, half_width),    # Top-right corner
            (-vehicle_size[0], half_width)    # Top-left corner
        ]

        rotated_corners = []
        for corner in corners:
            x, y = rotate_point(corner[0], corner[1], 0, 0, -float(veh_a.angle) + 90.0)  # Rotate around vehicle center
            rotated_corners.append((position[0] + x, position[1] + y))

        # Add or update the polygon around the vehicle
        polygon_id = f"head_{veh_a.id}_{timestep}"
        traci.polygon.add(polygon_id, rotated_corners, color=(255, 255, 0, 150), layer=5)  # Red, semi-transparent





traci.start(["sumo-gui", "-c", "osm.sumocfg"])
links = []
clusters = []
vehicles = []
tree = ET.parse('cars.xml')
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    timestep = traci.simulation.getTime()
    
    vehicles = read_positions(timestep, tree)
    if timestep % 5.0 == 0.0:
        links = read_links(timestep)
        clusters = read_clusters(timestep)
        for cluster in clusters:
            for member in cluster.members:
                traci.vehicle.setColor(f"veh{member}", (cluster.color))

    
    clear_polys() # Erase lines of previous timestep
    draw_links(links, vehicles, timestep)
    highlight_heads(clusters, vehicles, timestep)
    
    if timestep % 5.0 == 0.0:
        traci.gui.screenshot("View #0", f"screenshots/screenshot_{timestep}0.png")


    
    

traci.close()