import osmnx as ox
from geopy.geocoders import Nominatim

def get_route_length_km(address):

    geo = Nominatim(user_agent="fttp_real")
    loc = geo.geocode(address)

    if not loc:
        return 2.0

    point = (loc.latitude, loc.longitude)

    G = ox.graph_from_point(point, dist=2000, network_type="drive")

    nodes = list(G.nodes)

    start = nodes[0]
    end = nodes[-1]

    route = ox.shortest_path(G, start, end, weight="length")

    length = 0
    for i in range(len(route)-1):
        edge = G[route[i]][route[i+1]][0]
        length += edge["length"]

    return round(length/1000,2)