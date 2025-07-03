#!/usr/bin/env python3
"""
Comprehensive STL Analysis for Component Placement
Focus on practical measurements for NucDeck assembly
"""

import trimesh
import numpy as np
import os

def comprehensive_analysis(filepath):
    """
    Perform comprehensive analysis focusing on practical design needs
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    mesh = trimesh.load(filepath)
    filename = os.path.basename(filepath)
    
    print(f"\n{'='*60}")
    print(f"ANALYSIS: {filename}")
    print(f"{'='*60}")
    
    # Basic properties
    print(f"Mesh Properties:")
    print(f"  Vertices: {len(mesh.vertices):,}")
    print(f"  Faces: {len(mesh.faces):,}")
    print(f"  Volume: {mesh.volume:,.0f} mm³")
    print(f"  Surface Area: {mesh.area:,.0f} mm²")
    print(f"  Watertight: {mesh.is_watertight}")
    
    # Dimensional analysis
    bounds = mesh.bounds
    dimensions = bounds[1] - bounds[0]
    
    print(f"\nDimensional Analysis:")
    print(f"  Bounding Box Min: ({bounds[0][0]:.1f}, {bounds[0][1]:.1f}, {bounds[0][2]:.1f}) mm")
    print(f"  Bounding Box Max: ({bounds[1][0]:.1f}, {bounds[1][1]:.1f}, {bounds[1][2]:.1f}) mm")
    print(f"  Overall Dimensions (X×Y×Z): {dimensions[0]:.1f} × {dimensions[1]:.1f} × {dimensions[2]:.1f} mm")
    print(f"  Width (X): {dimensions[0]:.1f} mm")
    print(f"  Depth (Y): {dimensions[1]:.1f} mm") 
    print(f"  Height (Z): {dimensions[2]:.1f} mm")
    
    # Center points
    geometric_center = (bounds[0] + bounds[1]) / 2
    print(f"  Geometric Center: ({geometric_center[0]:.1f}, {geometric_center[1]:.1f}, {geometric_center[2]:.1f}) mm")
    
    # Complexity analysis
    convex_hull = mesh.convex_hull
    volume_ratio = mesh.volume / convex_hull.volume if convex_hull.volume > 0 else 0
    
    print(f"\nComplexity Analysis:")
    print(f"  Volume/ConvexHull Ratio: {volume_ratio:.3f}")
    if volume_ratio < 0.3:
        print(f"  -> Highly complex with major internal cavities")
    elif volume_ratio < 0.7:
        print(f"  -> Moderately complex with some internal features")
    else:
        print(f"  -> Relatively simple geometry")
    
    # Face orientation analysis
    face_normals = mesh.face_normals
    face_areas = mesh.area_faces
    
    # Categorize faces by orientation
    horizontal_up = np.sum((face_normals[:, 2] > 0.8) & (face_areas > 1.0))  # Facing up
    horizontal_down = np.sum((face_normals[:, 2] < -0.8) & (face_areas > 1.0))  # Facing down
    vertical_faces = np.sum((np.abs(face_normals[:, 2]) < 0.3) & (face_areas > 1.0))  # Vertical
    
    print(f"\nSurface Analysis:")
    print(f"  Large upward faces: {horizontal_up} (potential mounting surfaces)")
    print(f"  Large downward faces: {horizontal_down} (potential recesses)")
    print(f"  Large vertical faces: {vertical_faces} (walls/sides)")
    
    # Find large flat areas (potential component mounting zones)
    large_flat_areas = []
    for i, (normal, area) in enumerate(zip(face_normals, face_areas)):
        if area > 100:  # Areas larger than 100 mm²
            face_center = mesh.triangles_center[i]
            large_flat_areas.append({
                'index': i,
                'center': face_center,
                'area': area,
                'normal': normal,
                'orientation': 'horizontal_up' if normal[2] > 0.8 else 
                              'horizontal_down' if normal[2] < -0.8 else 'vertical'
            })
    
    print(f"\nLarge Flat Areas (>100mm²): {len(large_flat_areas)}")
    for i, area in enumerate(sorted(large_flat_areas, key=lambda x: x['area'], reverse=True)[:5]):
        print(f"  Area {i+1}: {area['area']:.0f}mm² at ({area['center'][0]:.1f}, {area['center'][1]:.1f}, {area['center'][2]:.1f}) - {area['orientation']}")
    
    # Analyze potential mounting locations
    vertices = mesh.vertices
    
    # Find Z-levels with many vertices (indicating detail/features)
    z_coords = vertices[:, 2]
    unique_z = np.round(z_coords, 1)
    z_counts = np.bincount((unique_z * 10).astype(int) - int(unique_z.min() * 10))
    
    print(f"\nZ-Level Analysis:")
    print(f"  Z range: {z_coords.min():.1f} to {z_coords.max():.1f} mm")
    print(f"  Most detailed levels (likely feature locations):")
    
    top_z_indices = np.argsort(z_counts)[-5:]
    for idx in reversed(top_z_indices):
        z_level = (idx + int(z_coords.min() * 10)) / 10
        vertex_count = z_counts[idx]
        if vertex_count > 10:  # Only show levels with significant detail
            print(f"    Z={z_level:.1f}mm: {vertex_count} vertices")
    
    return {
        'filename': filename,
        'dimensions': dimensions,
        'bounds': bounds,
        'volume': mesh.volume,
        'geometric_center': geometric_center,
        'volume_ratio': volume_ratio,
        'large_flat_areas': large_flat_areas
    }

def component_placement_analysis(front_data, back_data):
    """
    Analyze component placement possibilities based on mesh data
    """
    print(f"\n{'='*60}")
    print(f"COMPONENT PLACEMENT ANALYSIS")
    print(f"{'='*60}")
    
    if not front_data or not back_data:
        return
    
    # Overall assembly envelope
    front_dims = front_data['dimensions']
    back_dims = back_data['dimensions']
    
    print(f"Assembly Envelope:")
    print(f"  Front: {front_dims[0]:.1f} × {front_dims[1]:.1f} × {front_dims[2]:.1f} mm")
    print(f"  Back:  {back_dims[0]:.1f} × {back_dims[1]:.1f} × {back_dims[2]:.1f} mm")
    
    # Assume parts mate along Y-axis (depth)
    total_depth = front_dims[1] + back_dims[1]
    max_width = max(front_dims[0], back_dims[0])
    max_height = max(front_dims[2], back_dims[2])
    
    print(f"  Combined Assembly: {max_width:.1f} × {total_depth:.1f} × {max_height:.1f} mm")
    
    # Component requirements from README
    components = {
        'Samsung S20': {'size': [152, 70, 9], 'location': 'front_center'},
        'Battery 8000mAh': {'size': [90, 60, 12], 'location': 'back_cavity'},
        'TP4056 Charger': {'size': [23, 16, 5], 'location': 'back_electronics'},
        'PD Trigger Module': {'size': [23.3, 11.9, 4], 'location': 'back_electronics'},
        'Battery Indicator': {'size': [43.5, 20, 5], 'location': 'back_visible'},
        'Power Switch': {'size': [16, 16, 35], 'location': 'top_access'},  # 16mm bezel, 35mm depth
        'Left Joystick': {'size': [32, 32, 18], 'location': 'front_left'},
        'Right Joystick': {'size': [32, 32, 18], 'location': 'front_right'}
    }
    
    print(f"\nComponent Fit Analysis:")
    
    # Check if phone fits in front cover
    phone = components['Samsung S20']['size']
    phone_clearance = [phone[0] + 2, phone[1] + 2, phone[2] + 1]  # Add clearance
    
    if (phone_clearance[0] < front_dims[0] * 0.8 and 
        phone_clearance[1] < front_dims[1] and 
        phone_clearance[2] < front_dims[2] * 0.8):
        print(f"  ✓ Samsung S20 fits in front cover")
        # Calculate phone position (centered)
        phone_center_x = front_data['geometric_center'][0]
        phone_center_z = front_data['geometric_center'][2]
        print(f"    Suggested position: X={phone_center_x:.1f}, Z={phone_center_z:.1f}")
    else:
        print(f"  ✗ Samsung S20 may not fit - need larger cutout")
    
    # Check battery fit in back cover
    battery = components['Battery 8000mAh']['size']
    battery_clearance = [battery[0] + 2, battery[1] + 2, battery[2] + 1]
    
    if (battery_clearance[0] < back_dims[0] and 
        battery_clearance[1] < back_dims[1] and 
        battery_clearance[2] < back_dims[2]):
        print(f"  ✓ Battery fits in back cover")
    else:
        print(f"  ⚠ Battery tight fit - verify internal cavity size")
    
    # Joystick placement
    joystick_diameter = 32
    grip_width = (front_dims[0] - phone[0]) / 2  # Available grip area width
    
    print(f"\nJoystick Placement:")
    print(f"  Available grip width each side: {grip_width:.1f} mm")
    if grip_width > joystick_diameter:
        print(f"  ✓ Joysticks fit in grip areas")
        left_x = phone_center_x - (phone[0]/2 + grip_width/2)
        right_x = phone_center_x + (phone[0]/2 + grip_width/2)
        joystick_y = front_dims[1] * 0.8  # Near front edge
        print(f"    Left joystick: X={left_x:.1f}, Y={joystick_y:.1f}")
        print(f"    Right joystick: X={right_x:.1f}, Y={joystick_y:.1f}")
    else:
        print(f"  ⚠ Joysticks may not fit - need wider design")
    
    # Electronics bay analysis
    print(f"\nElectronics Placement:")
    small_electronics = ['TP4056 Charger', 'PD Trigger Module', 'Battery Indicator']
    total_electronics_area = sum(comp['size'][0] * comp['size'][1] for name, comp in components.items() if name in small_electronics)
    
    available_area = back_dims[0] * back_dims[1] - (battery[0] * battery[1])
    print(f"  Available electronics area: {available_area:.0f} mm²")
    print(f"  Required electronics area: {total_electronics_area:.0f} mm²")
    
    if available_area > total_electronics_area * 1.5:  # 50% margin
        print(f"  ✓ Sufficient space for electronics")
    else:
        print(f"  ⚠ Tight fit for electronics - optimize layout")

def main():
    # File paths
    housing_dir = "/workspaces/scad/Housing - STL"
    front_file = os.path.join(housing_dir, "Housing Front.STL")
    back_file = os.path.join(housing_dir, "Back Cover 7th Gen Intel NUC.STL")
    
    print("NUCDECK STL ANALYSIS FOR COMPONENT PLACEMENT")
    print("="*60)
    
    # Analyze both files
    front_data = comprehensive_analysis(front_file)
    back_data = comprehensive_analysis(back_file)
    
    # Component placement analysis
    component_placement_analysis(front_data, back_data)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY & RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if front_data and back_data:
        print(f"Shell Characteristics:")
        print(f"• Front cover: Wide design (294mm) with grip extensions")
        print(f"• Back cover: Narrower (137mm) focusing on main device area")  
        print(f"• Both parts are thin (19mm) - need efficient internal layout")
        print(f"• Complex internal geometry suggests existing mounting features")
        
        print(f"\nNext Steps for Component Integration:")
        print(f"1. Create phone pocket cutout in front cover center")
        print(f"2. Design battery compartment in back cover")
        print(f"3. Add joystick mounting holes in grip areas")
        print(f"4. Plan electronics bay layout in remaining back cover space")
        print(f"5. Add button cutouts around phone area")
        print(f"6. Design cable routing channels")

if __name__ == "__main__":
    main()
