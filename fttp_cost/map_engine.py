import osmnx as ox
import networkx as nx

def get_route_with_map(from_loc, to_loc):

    try:
        # Get coordinates
        start = ox.geocode(from_loc)
        end = ox.geocode(to_loc)

        # Create graph around midpoint
        mid_point = ((start[0]+end[0])/2, (start[1]+end[1])/2)
        G = ox.graph_from_point(mid_point, dist=10000, network_type='drive')

        # Find nearest nodes
        orig_node = ox.distance.nearest_nodes(G, start[1], start[0])
        dest_node = ox.distance.nearest_nodes(G, end[1], end[0])

        # Shortest path
        try:
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        except:
            return {"error": "Route not found"}

        # Calculate distance
        length = 0
        route_coords = []

        for i in range(len(route)-1):
            edge = G[route[i]][route[i+1]][0]
            length += edge['length']

            node = G.nodes[route[i]]
            route_coords.append((node['y'], node['x']))

        distance_km = round(length / 1000, 2)

        return {
            "distance_km": distance_km,
            "route_coords": route_coords,
            "start": start,
            "end": end
        }

    except Exception as e:
        return {"error": str(e)}