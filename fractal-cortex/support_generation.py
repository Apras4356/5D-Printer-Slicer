import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from slicing_functions import fix_polygon_or_multipolygon_ring_orientation, safe_unary_union

def get_overhangs_for_layer(current_layer_polys, layer_below_polys, overhang_threshold):
    """
    Find areas of the current layer that are not supported by the layer below.
    """
    current_area = safe_unary_union(current_layer_polys)
    if current_area.is_empty:
        return current_area
        
    below_area = safe_unary_union(layer_below_polys)
    if below_area.is_empty:
        return current_area
        
    # Dilate the area below by the threshold to allow safe overhangs without supports
    supported_area = below_area.buffer(overhang_threshold, join_style=2)
    
    overhang = current_area.difference(supported_area)
    return overhang

def generate_support_volumes(innerMostPolygonsList, overhang_threshold):
    """
    Returns a list of support polygons for each layer.
    """
    num_layers = len(innerMostPolygonsList)
    support_areas = [[] for _ in range(num_layers)]
    
    # We accumulate support requests from top to bottom
    accumulated_support = None
    
    # We stop at 1 because layer 0 is the bed (supports touch the bed)
    for layer in range(num_layers - 1, 0, -1):
        # 1. Detect new overhangs on this layer
        overhangs = get_overhangs_for_layer(
            innerMostPolygonsList[layer],
            innerMostPolygonsList[layer - 1],
            overhang_threshold
        )
        
        # 2. Subtract the physical part footprint from the descending support column (from higher layers)
        if accumulated_support is not None and not accumulated_support.is_empty:
            current_layer_solid = safe_unary_union(innerMostPolygonsList[layer])
            accumulated_support = accumulated_support.difference(current_layer_solid.buffer(0.2)) # 0.2mm clearance

        # 3. Add the newly detected overhangs to our accumulated downward-projecting support volume
        if not overhangs.is_empty:
            if accumulated_support is None:
                accumulated_support = overhangs
            else:
                accumulated_support = accumulated_support.union(overhangs)
                
        # 4. Generate footprint for the layer below
        if accumulated_support is not None and not accumulated_support.is_empty:
            layer_below_solid = safe_unary_union(innerMostPolygonsList[layer - 1])
            support_footprint = accumulated_support.difference(layer_below_solid.buffer(0.2))
            
            if not support_footprint.is_empty:
                support_areas[layer - 1].append(support_footprint)
                
    return support_areas
