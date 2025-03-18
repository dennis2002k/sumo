import traci

# Start SUMO with TraCI
sumo_binary = "sumo"  # Use "sumo" for non-GUI mode
sumo_cmd = [sumo_binary, "-c", "analipsews/osm.sumocfg", "--emission-output", "cars.xml"]

traci.start(sumo_cmd)

# Run simulation 100 steps
for step in range(100):
    traci.simulationStep()
# Close SUMO
traci.close()
print("Simulation ended after 100 steps.")
