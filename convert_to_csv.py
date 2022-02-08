import geopandas
from gerrychain import Graph, GeographicPartition
from write_partition import write_to_csv
import pickle
from reusable_data import get_county_subgraphs, get_id_to_county, get_county_populations, get_county_to_id
from partition_functions import get_county_nodes

muni_file = r'C:\Users\charl\Box\Internships\Gerry Chain 2\Algorithm\Ensembles\Testing\MUNI_2_2571.shp'
data_muni = geopandas.read_file(muni_file)

vtd_graph = pickle.load(open("vtd_graph.dump", "rb"))
muni_graph = Graph.from_geodataframe(data_muni)

muni_partition = GeographicPartition(muni_graph, assignment = "assignment")
vtd_partition = GeographicPartition(vtd_graph, assignment = "assignment")

pop_col = 'P0010001'
muni_to_id = get_county_to_id(muni_graph, "MUNI")
id_to_muni = get_id_to_county(muni_to_id)
muni_populations = get_county_populations(muni_graph, id_to_muni, 
    pop_col)
munis = list(muni_populations.keys())
muni_subgraphs = get_county_subgraphs(vtd_graph, munis, "MUNI")

for node in muni_partition.graph.nodes():
    district = muni_partition.assignment[node]
    nodes = get_county_nodes(muni_subgraphs[id_to_muni[node]], district)
    vtd_partition = vtd_partition.flip(nodes)

write_to_csv(vtd_partition, "GEOID20", "assignment", "Testing", "demo10")
