#!/usr/bin/env python3
"""
Enhanced STL Modification Script with Better Positioning
Creates precise Samsung Galaxy S20 cutout with improved boolean operations
"""

import trimesh
import numpy as np
import os

def analyze_mesh_at_position(mesh, center_x, center_y, search_radius=80):
    """
    Analyze the mesh geometry at a specific position to determine proper cutout depth
    """
    print(f"Analyzing mesh geometry at position ({center_x:.1f}, {center_y:.1f})...")
    
    # Get all vertices
    vertices = mesh.vertices
    
    # Find vertices near the target position
    distances = np.sqrt((vertices[:, 0] - center_x)**2 + (vertices[:, 1] - center_y)**2)
    nearby_vertices = vertices[distances < search_radius]
    
    if len(nearby_vertices) == 0:
        print(f"  No vertices found near position")
        return None
    
    print(f"  Found {len(nearby_vertices)} vertices near target position")
    
    # Analyze Z distribution
    z_coords = nearby_vertices[:, 2]
    z_min, z_max = z_coords.min(), z_coords.max()
    z_mean = z_coords.mean()
    
    print(f"  Z-range: {z_min:.1f} to {z_max:.1f} mm")
    print(f"  Z-mean: {z_mean:.1f} mm")
    
    # Find the surface level (likely the top surface for cutout)
    z_hist, z_bins = np.histogram(z_coords, bins=50)
    peak_bin = np.argmax(z_hist)
    surface_level = z_bins[peak_bin]
    
    print(f"  Estimated surface level: {surface_level:.1f} mm")
    
    return {
        'z_min': z_min,
        'z_max': z_max,
        'z_mean': z_mean,
        'surface_level': surface_level,
        'vertex_count': len(nearby_vertices)
    }

def create_precise_cutout(width, height, depth, corner_radius, center, surface_level=None):
    """
    Create a precise cutout positioned relative to the surface
    """
    print(f"Creating cutout: {width:.1f}×{height:.1f}×{depth:.1f} mm at {center}")
    
    # Adjust center Z position based on surface analysis
    if surface_level is not None:
        # Position cutout to start from surface level and cut downward
        cutout_center = [center[0], center[1], surface_level - depth/2]
        print(f"  Adjusted Z center based on surface: {cutout_center[2]:.1f} mm")
    else:
        cutout_center = center
    
    # Create main rectangular box
    main_box = trimesh.creation.box(extents=[width, height, depth])
    
    if corner_radius > 0:
        # Create rounded corners by combining box with cylinders
        half_w = width/2 - corner_radius
        half_h = height/2 - corner_radius
        
        # Corner positions relative to box center
        corners = [
            [half_w, half_h, 0],
            [-half_w, half_h, 0],
            [-half_w, -half_h, 0],
            [half_w, -half_h, 0]
        ]
        
        # Create corner cylinders
        corner_cylinders = []
        for corner_pos in corners:
            cyl = trimesh.creation.cylinder(
                radius=corner_radius,
                height=depth,
                sections=32  # High resolution for smooth corners
            )
            cyl.apply_translation(corner_pos)
            corner_cylinders.append(cyl)
        
        # Create connecting rectangles
        # Top and bottom strips
        top_strip = trimesh.creation.box(extents=[width - 2*corner_radius, 2*corner_radius, depth])
        top_strip.apply_translation([0, half_h + corner_radius, 0])
        
        bottom_strip = trimesh.creation.box(extents=[width - 2*corner_radius, 2*corner_radius, depth])
        bottom_strip.apply_translation([0, -half_h - corner_radius, 0])
        
        # Left and right strips  
        left_strip = trimesh.creation.box(extents=[2*corner_radius, height - 2*corner_radius, depth])
        left_strip.apply_translation([-half_w - corner_radius, 0, 0])
        
        right_strip = trimesh.creation.box(extents=[2*corner_radius, height - 2*corner_radius, depth])
        right_strip.apply_translation([half_w + corner_radius, 0, 0])
        
        # Combine all parts
        all_parts = [main_box] + corner_cylinders + [top_strip, bottom_strip, left_strip, right_strip]
        
        # Union all parts to create rounded rectangle
        cutout = all_parts[0]
        for part in all_parts[1:]:
            cutout = cutout.union(part)
            
    else:
        cutout = main_box
    
    # Position the cutout at the target location
    cutout.apply_translation(cutout_center)
    
    return cutout

def validate_cutout_intersection(original_mesh, cutout_mesh):
    """
    Validate that the cutout actually intersects with the original mesh
    """
    # Check if bounding boxes overlap
    orig_bounds = original_mesh.bounds
    cutout_bounds = cutout_mesh.bounds
    
    print(f"Validating cutout intersection...")
    print(f"  Original bounds: {orig_bounds[0]} to {orig_bounds[1]}")
    print(f"  Cutout bounds: {cutout_bounds[0]} to {cutout_bounds[1]}")
    
    # Check overlap in each dimension
    overlap_x = (cutout_bounds[0][0] < orig_bounds[1][0]) and (cutout_bounds[1][0] > orig_bounds[0][0])
    overlap_y = (cutout_bounds[0][1] < orig_bounds[1][1]) and (cutout_bounds[1][1] > orig_bounds[0][1])
    overlap_z = (cutout_bounds[0][2] < orig_bounds[1][2]) and (cutout_bounds[1][2] > orig_bounds[0][2])
    
    print(f"  Overlap - X: {overlap_x}, Y: {overlap_y}, Z: {overlap_z}")
    
    if not (overlap_x and overlap_y and overlap_z):
        print("  ⚠ Warning: Cutout may not intersect with original mesh!")
        return False
    
    # Calculate intersection volume estimate
    intersection_bounds = [
        [max(orig_bounds[0][0], cutout_bounds[0][0]),
         max(orig_bounds[0][1], cutout_bounds[0][1]),
         max(orig_bounds[0][2], cutout_bounds[0][2])],
        [min(orig_bounds[1][0], cutout_bounds[1][0]),
         min(orig_bounds[1][1], cutout_bounds[1][1]),
         min(orig_bounds[1][2], cutout_bounds[1][2])]
    ]
    
    intersection_volume = np.prod(np.array(intersection_bounds[1]) - np.array(intersection_bounds[0]))
    print(f"  Estimated intersection volume: {intersection_volume:,.0f} mm³")
    
    return True

def modify_front_cover_enhanced():
    """
    Enhanced front cover modification with better positioning
    """
    # File paths
    input_file = "/workspaces/scad/Housing - STL/Housing Front.STL"
    output_file = "/workspaces/scad/output/FrontCover_Modified_S20Cutout_v2.stl"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("Enhanced NucDeck Front Cover Modification")
    print("=" * 60)
    
    # Load original mesh
    print(f"Loading: {input_file}")
    original_mesh = trimesh.load(input_file)
    
    print(f"Original mesh:")
    print(f"  Vertices: {len(original_mesh.vertices):,}")
    print(f"  Faces: {len(original_mesh.faces):,}")
    print(f"  Volume: {original_mesh.volume:,.0f} mm³")
    print(f"  Bounds: {original_mesh.bounds[0]} to {original_mesh.bounds[1]}")
    
    # Cutout parameters
    phone_width = 152.0   # Samsung S20 width
    phone_height = 70.0   # Samsung S20 height  
    tolerance = 0.5       # mm tolerance
    corner_radius = 1.0   # mm corner fillet
    
    cutout_width = phone_width + 2 * tolerance
    cutout_height = phone_height + 2 * tolerance
    
    # Center position (from analysis)
    center_x = 147.0
    center_y = 9.5
    
    print(f"\nCutout specifications:")
    print(f"  Phone: {phone_width} × {phone_height} mm")
    print(f"  Cutout: {cutout_width} × {cutout_height} mm")
    print(f"  Tolerance: ±{tolerance} mm")
    print(f"  Corner radius: {corner_radius} mm")
    print(f"  Position: ({center_x}, {center_y})")
    
    # Analyze mesh at target position
    geometry_info = analyze_mesh_at_position(original_mesh, center_x, center_y)
    
    if geometry_info is None:
        print("Could not analyze mesh geometry at target position")
        return False
    
    # Determine cutout depth and position
    mesh_bounds = original_mesh.bounds
    total_depth = mesh_bounds[1][2] - mesh_bounds[0][2]  # Full Z height
    cutout_depth = total_depth + 5  # Ensure complete cut-through
    
    # Use surface level for Z positioning
    surface_z = geometry_info['surface_level']
    cutout_center_z = surface_z - cutout_depth/2
    
    print(f"\nCutout positioning:")
    print(f"  Surface level: {surface_z:.1f} mm")
    print(f"  Cutout depth: {cutout_depth:.1f} mm")
    print(f"  Cutout center Z: {cutout_center_z:.1f} mm")
    
    # Create cutout mesh
    cutout_center = [center_x, center_y, cutout_center_z]
    cutout_mesh = create_precise_cutout(
        width=cutout_width,
        height=cutout_height,
        depth=cutout_depth,
        corner_radius=corner_radius,
        center=cutout_center,
        surface_level=surface_z
    )
    
    print(f"\nCutout mesh:")
    print(f"  Vertices: {len(cutout_mesh.vertices):,}")
    print(f"  Faces: {len(cutout_mesh.faces):,}")
    print(f"  Volume: {cutout_mesh.volume:,.0f} mm³")
    
    # Validate intersection
    if not validate_cutout_intersection(original_mesh, cutout_mesh):
        print("Intersection validation failed - adjusting cutout position...")
        # Try adjusting Z position
        cutout_center_z = geometry_info['z_mean']
        cutout_center = [center_x, center_y, cutout_center_z]
        cutout_mesh = create_precise_cutout(
            width=cutout_width,
            height=cutout_height, 
            depth=cutout_depth,
            corner_radius=corner_radius,
            center=cutout_center
        )
    
    # Perform boolean difference
    print(f"\nPerforming boolean subtraction...")
    try:
        result_mesh = original_mesh.difference(cutout_mesh)
        
        if result_mesh is None or len(result_mesh.vertices) == 0:
            print("Boolean operation returned empty result")
            return False
        
        volume_removed = original_mesh.volume - result_mesh.volume
        print(f"Boolean operation successful!")
        print(f"  Result vertices: {len(result_mesh.vertices):,}")
        print(f"  Result faces: {len(result_mesh.faces):,}")
        print(f"  Volume removed: {volume_removed:,.0f} mm³")
        
        if volume_removed < 1000:  # Less than 1 cm³ removed
            print("  ⚠ Warning: Very little volume removed - cutout may not be effective")
        
    except Exception as e:
        print(f"Boolean operation failed: {e}")
        return False
    
    # Clean up the mesh
    print(f"\nCleaning up result mesh...")
    result_mesh.remove_duplicate_faces()
    result_mesh.merge_vertices()
    
    if not result_mesh.is_watertight:
        print("  Attempting to repair non-watertight mesh...")
        result_mesh.fill_holes()
    
    print(f"  Final mesh watertight: {result_mesh.is_watertight}")
    
    # Export result
    print(f"\nExporting to: {output_file}")
    result_mesh.export(output_file)
    
    # Verify export
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✓ Export successful! File size: {file_size:,} bytes")
        
        # Test reload
        test_mesh = trimesh.load(output_file)
        print(f"  Verification: {len(test_mesh.vertices):,} vertices, {len(test_mesh.faces):,} faces")
        return True
    else:
        print("❌ Export failed!")
        return False

if __name__ == "__main__":
    success = modify_front_cover_enhanced()
    
    if success:
        print(f"\n{'='*60}")
        print(f"✅ ENHANCED MODIFICATION COMPLETE!")
        print(f"{'='*60}")
        print(f"Output file: output/FrontCover_Modified_S20Cutout_v2.stl")
        print(f"\nRecommended next steps:")
        print(f"1. Open the STL in a 3D viewer to verify the cutout")
        print(f"2. Check that the cutout is properly positioned")
        print(f"3. Verify that corners are properly filleted")
        print(f"4. Test print a small section if needed")
    else:
        print(f"\n❌ MODIFICATION FAILED - check error messages above")
