#!/usr/bin/env python3
"""
STL Modification Script for NucDeck Front Cover
Creates precise Samsung Galaxy S20 cutout with boolean operations
"""

import trimesh
import numpy as np
import os
from scipy.spatial.transform import Rotation

def create_rounded_rectangle_cutout(width, height, depth, corner_radius=1.0, center=(0, 0, 0)):
    """
    Create a rounded rectangle cutout mesh for boolean subtraction
    
    Parameters:
    - width: X dimension (152mm for S20)
    - height: Y dimension (70mm for S20) 
    - depth: Z dimension (full shell depth)
    - corner_radius: radius for filleted corners (1mm)
    - center: center position (x, y, z)
    """
    
    # Create the main rectangle
    box = trimesh.creation.box(extents=[width, height, depth])
    
    # Create corner cylinders for filleting
    if corner_radius > 0:
        # Calculate corner positions
        half_w = width / 2 - corner_radius
        half_h = height / 2 - corner_radius
        
        corners = [
            [half_w, half_h, 0],      # +X, +Y
            [-half_w, half_h, 0],     # -X, +Y
            [-half_w, -half_h, 0],    # -X, -Y
            [half_w, -half_h, 0]      # +X, -Y
        ]
        
        # Create rounded corners
        corner_meshes = []
        for corner_pos in corners:
            # Create cylinder for corner
            cylinder = trimesh.creation.cylinder(
                radius=corner_radius,
                height=depth,
                sections=16  # Smooth corners
            )
            cylinder.apply_translation(corner_pos)
            corner_meshes.append(cylinder)
        
        # Create rectangles to connect corners
        # Horizontal rectangles (top and bottom)
        top_rect = trimesh.creation.box(extents=[width - 2*corner_radius, 2*corner_radius, depth])
        top_rect.apply_translation([0, half_h + corner_radius, 0])
        
        bottom_rect = trimesh.creation.box(extents=[width - 2*corner_radius, 2*corner_radius, depth])
        bottom_rect.apply_translation([0, -half_h - corner_radius, 0])
        
        # Vertical rectangles (left and right)
        left_rect = trimesh.creation.box(extents=[2*corner_radius, height - 2*corner_radius, depth])
        left_rect.apply_translation([-half_w - corner_radius, 0, 0])
        
        right_rect = trimesh.creation.box(extents=[2*corner_radius, height - 2*corner_radius, depth])
        right_rect.apply_translation([half_w + corner_radius, 0, 0])
        
        # Combine all parts
        cutout_parts = [box] + corner_meshes + [top_rect, bottom_rect, left_rect, right_rect]
        cutout = trimesh.util.concatenate(cutout_parts)
        cutout = cutout.convex_hull  # Ensure clean union
    else:
        cutout = box
    
    # Position at the specified center
    cutout.apply_translation(center)
    
    return cutout

def analyze_existing_cutout(mesh, search_center, search_radius=50):
    """
    Analyze existing cutouts near the specified center position
    """
    print(f"Analyzing existing cutouts near ({search_center[0]:.1f}, {search_center[1]:.1f})...")
    
    # Sample points on the mesh surface
    surface_points = mesh.sample(5000)
    
    # Find points near the search center
    distances_to_center = np.linalg.norm(
        surface_points[:, :2] - np.array(search_center[:2]), axis=1
    )
    
    near_center_points = surface_points[distances_to_center < search_radius]
    
    if len(near_center_points) > 0:
        # Analyze Z-levels of points near center
        z_coords = near_center_points[:, 2]
        print(f"  Found {len(near_center_points)} surface points near center")
        print(f"  Z-range at center: {z_coords.min():.1f} to {z_coords.max():.1f} mm")
        
        # Check for potential existing cutout (gap in Z-levels)
        z_hist, z_bins = np.histogram(z_coords, bins=20)
        gap_threshold = len(near_center_points) * 0.1  # 10% threshold
        
        gaps = z_hist < gap_threshold
        if np.any(gaps):
            print(f"  Potential existing cutout detected (gaps in Z-distribution)")
            gap_z_levels = z_bins[:-1][gaps]
            print(f"  Gap Z-levels: {gap_z_levels}")
            return True, z_coords.min(), z_coords.max()
    
    return False, None, None

def repair_mesh(mesh):
    """
    Repair common mesh issues after boolean operations
    """
    print("Repairing mesh...")
    
    # Remove duplicate vertices
    mesh.remove_duplicate_faces()
    mesh.remove_degenerate_faces()
    mesh.remove_unreferenced_vertices()
    
    # Fill holes if any
    if not mesh.is_watertight:
        print("  Mesh is not watertight, attempting repair...")
        mesh.fill_holes()
    
    # Check and fix normals
    if not mesh.is_winding_consistent:
        print("  Fixing inconsistent winding...")
        mesh.fix_normals()
    
    # Merge close vertices
    mesh.merge_vertices()
    
    print(f"  Repair complete. Watertight: {mesh.is_watertight}")
    return mesh

def modify_front_cover():
    """
    Main function to modify the front cover with S20 cutout
    """
    # File paths
    housing_dir = "/workspaces/scad/Housing - STL"
    input_file = os.path.join(housing_dir, "Housing Front.STL")
    output_file = "/workspaces/scad/output/FrontCover_Modified_S20Cutout.stl"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("NucDeck Front Cover Modification for Samsung Galaxy S20")
    print("=" * 60)
    
    # Load the original mesh
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return False
    
    print(f"Loading original front cover: {input_file}")
    original_mesh = trimesh.load(input_file)
    
    print(f"Original mesh info:")
    print(f"  Vertices: {len(original_mesh.vertices):,}")
    print(f"  Faces: {len(original_mesh.faces):,}")
    print(f"  Volume: {original_mesh.volume:,.0f} mm³")
    print(f"  Watertight: {original_mesh.is_watertight}")
    
    # Define cutout parameters (from requirements)
    cutout_width = 152.0  # mm (S20 width)
    cutout_height = 70.0  # mm (S20 height) 
    cutout_center = [147.0, 9.5, 57.5]  # From previous analysis
    corner_radius = 1.0   # mm fillet radius
    tolerance = 0.5       # mm tolerance buffer
    
    # Add tolerance to cutout dimensions
    actual_cutout_width = cutout_width + 2 * tolerance
    actual_cutout_height = cutout_height + 2 * tolerance
    
    print(f"\nCutout specifications:")
    print(f"  Phone size: {cutout_width} × {cutout_height} mm")
    print(f"  Cutout size (with tolerance): {actual_cutout_width} × {actual_cutout_height} mm")
    print(f"  Center position: ({cutout_center[0]:.1f}, {cutout_center[1]:.1f}, {cutout_center[2]:.1f})")
    print(f"  Corner radius: {corner_radius} mm")
    print(f"  Tolerance: ±{tolerance} mm")
    
    # Analyze existing cutouts
    has_existing, z_min, z_max = analyze_existing_cutout(
        original_mesh, cutout_center, search_radius=80
    )
    
    # Determine cutout depth
    bounds = original_mesh.bounds
    shell_depth = bounds[1][1] - bounds[0][1]  # Y dimension
    cutout_depth = shell_depth + 10  # Ensure complete cut-through
    
    print(f"\nShell analysis:")
    print(f"  Shell depth (Y): {shell_depth:.1f} mm")
    print(f"  Cutout depth: {cutout_depth:.1f} mm")
    
    # Create the cutout geometry
    print(f"\nCreating rounded rectangle cutout...")
    cutout_mesh = create_rounded_rectangle_cutout(
        width=actual_cutout_width,
        height=actual_cutout_height, 
        depth=cutout_depth,
        corner_radius=corner_radius,
        center=cutout_center
    )
    
    print(f"Cutout mesh created:")
    print(f"  Vertices: {len(cutout_mesh.vertices):,}")
    print(f"  Faces: {len(cutout_mesh.faces):,}")
    print(f"  Volume: {cutout_mesh.volume:,.0f} mm³")
    
    # Perform boolean subtraction
    print(f"\nPerforming boolean subtraction...")
    try:
        modified_mesh = original_mesh.difference(cutout_mesh)
        
        if modified_mesh is None or len(modified_mesh.vertices) == 0:
            print("Error: Boolean operation failed - empty result")
            return False
            
        print(f"Boolean operation successful!")
        print(f"  Result vertices: {len(modified_mesh.vertices):,}")
        print(f"  Result faces: {len(modified_mesh.faces):,}")
        print(f"  Volume removed: {original_mesh.volume - modified_mesh.volume:,.0f} mm³")
        
    except Exception as e:
        print(f"Error during boolean operation: {e}")
        return False
    
    # Repair the mesh
    modified_mesh = repair_mesh(modified_mesh)
    
    # Validate the result
    print(f"\nValidating result mesh:")
    print(f"  Watertight: {modified_mesh.is_watertight}")
    print(f"  Winding consistent: {modified_mesh.is_winding_consistent}")
    print(f"  Final volume: {modified_mesh.volume:,.0f} mm³")
    
    # Export the modified mesh
    print(f"\nExporting modified mesh to: {output_file}")
    try:
        modified_mesh.export(output_file)
        print(f"✓ Export successful!")
        
        # Verify the exported file
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"  File size: {file_size:,} bytes")
            
            # Test reload to verify integrity
            test_mesh = trimesh.load(output_file)
            print(f"  Verification: {len(test_mesh.vertices):,} vertices, {len(test_mesh.faces):,} faces")
            
        return True
        
    except Exception as e:
        print(f"Error during export: {e}")
        return False

def create_cutout_template():
    """
    Create a separate STL file showing just the cutout shape for verification
    """
    print(f"\nCreating cutout template for verification...")
    
    template_file = "/workspaces/scad/output/S20_Cutout_Template.stl"
    
    # Create the cutout shape
    cutout_mesh = create_rounded_rectangle_cutout(
        width=152.0 + 1.0,  # Phone width + tolerance
        height=70.0 + 1.0,  # Phone height + tolerance
        depth=10.0,         # Just for visualization
        corner_radius=1.0,
        center=[0, 0, 0]    # Centered at origin for template
    )
    
    # Export template
    cutout_mesh.export(template_file)
    print(f"✓ Cutout template saved: {template_file}")
    
    return template_file

if __name__ == "__main__":
    # Create output directory
    os.makedirs("/workspaces/scad/output", exist_ok=True)
    
    # Perform the modification
    success = modify_front_cover()
    
    if success:
        # Create template for verification
        create_cutout_template()
        
        print(f"\n{'='*60}")
        print(f"MODIFICATION COMPLETE!")
        print(f"{'='*60}")
        print(f"✓ Modified front cover: output/FrontCover_Modified_S20Cutout.stl")
        print(f"✓ Cutout template: output/S20_Cutout_Template.stl")
        print(f"\nNext steps:")
        print(f"1. Load the modified STL in your CAD software")
        print(f"2. Verify cutout dimensions and position")
        print(f"3. Test fit with Samsung Galaxy S20 mockup")
        print(f"4. Proceed with 3D printing or further modifications")
        
    else:
        print(f"\n❌ MODIFICATION FAILED")
        print(f"Check error messages above and try again")
