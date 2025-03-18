import traci
import webcolors

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


def read_clusters(timestep):
    clusters = []
    with open(f"sumo/cars{timestep}0.sumo", "r") as file:
        for line in file:
            data = line.split()
            new_cluster = Cluster(data[0], webcolors.name_to_rgb(data[1]),members=data[2].split(","))
            clusters.append(new_cluster)
        return clusters


traci.start(["sumo-gui", "-c", "osm.sumocfg"])

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()


    
    timestep = traci.simulation.getTime()
    if timestep % 5.0 == 0.0:
        clusters = read_clusters(timestep)
        for cluster in clusters:
            x, y = traci.vehicle.getPosition(f"veh{cluster.id}")

            # Add or update the shape around the vehicle
             # Define a small rectangle around the vehicle
            polygon_points = [
                (x - 2, y - 2),  # Bottom-left
                (x + 2, y - 2),  # Bottom-right
                (x + 2, y + 2),  # Top-right
                (x - 2, y + 2)   # Top-left
            ]

            # Add or update the polygon around the vehicle
            traci.polygon.add(cluster.id, polygon_points, color=(255, 0, 0, 150), layer=0)
            for member in cluster.members:
                traci.vehicle.setColor(f"veh{member}", (cluster.color))

traci.close()