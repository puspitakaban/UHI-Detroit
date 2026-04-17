import osmnx as ox

G = ox.graph_from_place("Detroit, Michigan, USA", network_type="drive")
nodes, edges = ox.graph_to_gdfs(G)

edges.to_file("detroit_roads.gpkg", driver="GPKG")
nodes.to_file("detroit_nodes.gpkg", driver="GPKG")

print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")