import compas
import compas_rhino

# simple functions for assigning constraints
from help import get_values
from help import get_index
from help import edge_constraints
from help import map_value_to_all_edges


from compas.datastructures import Network
from compas.utilities import XFunc
from compas_rhino.helpers import NetworkArtist

network= Network.from_json('octagon.json')

vertices = network.get_vertices_attributes('xyz')
edges    = list(network.edges())
fixed    = list(network.vertices_where({'is_fixed': True}))
# q_bnd=18.25  , q_valley=16.25 , q_ridge=13.75 , q_rest=1.0
q        = network.get_edges_attribute('q')

# edges to assign length constraint (bnd, ridge and valley)
lengths = network.edges_where({'l': True})
# edges to assign force constraint (rest)
forces = network.edges_where ({'f': True})


# FDM with iterative computation of q
# LU decomposition for solving lin. system
# procedure ends by reaching the num. of steps
# lengths from the first iteration step
nc0, f0, q0 = XFunc('iter.multistepFDM')(vertices, edges, fixed, q, steps=1)
ll0=XFunc('iter.list_of_element_lengths')(edges, nc0)

# assignment of constraints
# length constraints as lengths from the first iteration step for bnd, ridge and valley cables
indexl = get_index(edges, lengths)
edgvl = get_values(indexl, ll0)
length_constraints = edge_constraints(indexl,edgvl)

# force constraints as S=1.0 for the rest of the bars
indexf = get_index(edges, forces)
fs = map_value_to_all_edges(forces, 1.0)
force_constraints = edge_constraints(indexf, fs)

##FDM with iterative computation of q - tolerances added for the termination of the outer loop
##LU decomposition for solving lin. system
##tolerance for force tol_f = 1.e-4, tolerance for length tol_l = 1.e-3
#nc_lu, f_lu, q_lu = XFunc('iter.multistepFDM_wtol')(vertices, edges, fixed, q, fcs=force_constraints, lcs=length_constraints, tol_f=1.e-4, tol_l=1.e-3, steps=10000)
#l_lu = XFunc('iter.list_of_element_lengths')(edges, nc_lu)
# 
# 
##FDM with iterative computation of q - tolerances added for the termination of the outer loop
##CG for solving lin. system - not taking into account result from the previous step (latest=False)
##set tolerance for inner loop i_tol = 5e-07
#nc_cg1, f_cg1, q_cg1 = XFunc('iter.multistepFDM_wtol_cg') (vertices, edges, fixed, q, fcs=force_constraints, lcs=length_constraints, tol_f=1.e-4, tol_l=1.e-3, i_tol=5e-07,latest=False, steps=10000)
#l_cg1 = XFunc('iter.list_of_element_lengths')(edges, nc_cg1)
# 
##FDM with iterative computation of q - tolerances added for the termination of the outer loop
##CG for solving lin. system - taking into account result from the previous step
#nc_cg2, f_cg2, q_cg2 = XFunc('iter.multistepFDM_wtol_cg') (vertices, edges, fixed, q, fcs=force_constraints, lcs=length_constraints, tol_f=1.e-4, tol_l=1.e-3, i_tol=5e-07, steps=10000, latest=False)
#l_cg2 = XFunc('iter.list_of_element_lengths')(edges, nc_cg2)
# 
## Inexact iterative FDM
## dumping 0.025
nc_in, f_in, q_in = XFunc('iter.multistepFDM_inexact')(vertices, edges, fixed, q, fcs=force_constraints, lcs=length_constraints, tol_f=1.e-4, tol_l=1.e-3, i_tol_min=5e-07, damping=0.025, steps=10000)
l_in = XFunc('iter.list_of_element_lengths')(edges, nc_in)

res = [nc_in, l_in, f_in]
xyz = res[0]

for key, attr in network.vertices(True):
    attr['x'] = xyz[key][0]
    attr['y'] = xyz[key][1]
    attr['z'] = xyz[key][2]

artist = NetworkArtist(network)

artist.clear()

artist.draw_vertices()
artist.draw_edges()

artist.redraw()

