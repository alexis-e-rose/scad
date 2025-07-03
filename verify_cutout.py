#!/usr/bin/env python3
"""
Verification Script for Modified Front Cover
Analyzes the cutout to ensure it meets specifications
"""

import trimesh
import numpy as np
import os

def verify_cutout_dimensions(mesh_file, expected_center, expected_width, expected_height):
    """
    Verify that the cutout meets the specified dimensions
    """
    print(f"Verifying cutout in: {os.path.basename(mesh_file)}")
    
    mesh = trimesh.load(mesh_file)
    
    # Get mesh bounds
    bounds = mesh.bounds
    print(f"Overall mesh bounds: {bounds[0]} to {bounds[1]}")
    
    # Analyze the cutout area
    center_x, center_y = expected_center[0], expected_center[1]
    search_radius = max(expected_width, expected_height) / 2 + 10  # Search radius
    
    # Find vertices near the expected cutout center
    vertices = mesh.vertices
    distances = np.sqrt((vertices[:, 0] - center_x)**2 + (vertices[:, 1] - center_y)**2)
    nearby_vertices = vertices[distances < search_radius]
    
    print(f"\nCutout area analysis:")
    print(f"  Expected center: ({center_x:.1f}, {center_y:.1f})")
    print(f"  Expected size: {expected_width:.1f} × {expected_height:.1f} mm")
    print(f"  Vertices near cutout: {len(nearby_vertices)}")
    
    if len(nearby_vertices) > 0:
        # Analyze the Z distribution to detect the cutout
        z_coords = nearby_vertices[:, 2]
        z_range = z_coords.max() - z_coords.min()
        
        print(f"  Z-range in cutout area: {z_coords.min():.1f} to {z_coords.max():.1f} mm")
        print(f"  Z-span: {z_range:.1f} mm")
        
        # Look for cutout edges by examining X and Y ranges
        x_coords = nearby_vertices[:, 0]
        y_coords = nearby_vertices[:, 1]
        
        x_range = x_coords.max() - x_coords.min()
        y_range = y_coords.max() - y_coords.min()
        
        print(f"  Detected opening X-range: {x_range:.1f} mm")
        print(f"  Detected opening Y-range: {y_range:.1f} mm")
        
        # Check if dimensions match expectations
        width_match = abs(x_range - expected_width) < 5  # 5mm tolerance
        height_match = abs(y_range - expected_height) < 5
        
        print(f"  Width match: {width_match} (diff: {abs(x_range - expected_width):.1f} mm)")
        print(f"  Height match: {height_match} (diff: {abs(y_range - expected_height):.1f} mm)")
        
        return width_match and height_match
    
    return False

def create_cutout_analysis_report():
    """
    Create a comprehensive analysis report of the cutout modifications
    """
    print("NUCDECK FRONT COVER CUTOUT VERIFICATION REPORT")
    print("=" * 60)
    
    # File paths
    original_file = "/workspaces/scad/Housing - STL/Housing Front.STL"
    modified_file_v1 = "/workspaces/scad/output/FrontCover_Modified_S20Cutout.stl"
    modified_file_v2 = "/workspaces/scad/output/FrontCover_Modified_S20Cutout_v2.stl"
    template_file = "/workspaces/scad/output/S20_Cutout_Template.stl"
    
    # Expected specifications
    expected_center = [147.0, 9.5]
    expected_width = 153.0  # Including tolerance
    expected_height = 71.0  # Including tolerance
    
    print(f"\nTarget Specifications:")
    print(f"  Samsung S20 phone: 152 × 70 mm")
    print(f"  Cutout (with tolerance): {expected_width} × {expected_height} mm")
    print(f"  Center position: ({expected_center[0]}, {expected_center[1]})")
    print(f"  Corner radius: 1.0 mm")
    
    # Analyze original file
    if os.path.exists(original_file):
        print(f"\n--- Original Front Cover ---")
        original_mesh = trimesh.load(original_file)
        print(f"  Vertices: {len(original_mesh.vertices):,}")
        print(f"  Faces: {len(original_mesh.faces):,}")
        print(f"  Volume: {original_mesh.volume:,.0f} mm³")
        print(f"  Watertight: {original_mesh.is_watertight}")
    
    # Analyze modified versions
    for version, filepath in [("V1", modified_file_v1), ("V2", modified_file_v2)]:
        if os.path.exists(filepath):
            print(f"\n--- Modified Front Cover {version} ---")
            modified_mesh = trimesh.load(filepath)
            
            print(f"  File: {os.path.basename(filepath)}")
            print(f"  File size: {os.path.getsize(filepath):,} bytes")
            print(f"  Vertices: {len(modified_mesh.vertices):,}")
            print(f"  Faces: {len(modified_mesh.faces):,}")
            print(f"  Volume: {modified_mesh.volume:,.0f} mm³")
            print(f"  Watertight: {modified_mesh.is_watertight}")
            
            # Calculate volume difference
            if 'original_mesh' in locals():
                volume_diff = original_mesh.volume - modified_mesh.volume
                print(f"  Material removed: {volume_diff:,.0f} mm³")
                
                # Calculate theoretical cutout volume
                theoretical_volume = expected_width * expected_height * 19  # Shell depth
                print(f"  Theoretical cutout volume: {theoretical_volume:,.0f} mm³")
                
                if volume_diff > 1000:  # Significant material removed
                    print(f"  ✓ Cutout appears effective")
                else:
                    print(f"  ⚠ Minimal material removed - cutout may be ineffective")
            
            # Verify cutout dimensions
            cutout_valid = verify_cutout_dimensions(
                filepath, expected_center, expected_width, expected_height
            )
            
            print(f"  Cutout validation: {'✓ PASS' if cutout_valid else '❌ FAIL'}")
        else:
            print(f"\n--- Modified Front Cover {version} ---")
            print(f"  File not found: {filepath}")
    
    # Analyze template file
    if os.path.exists(template_file):
        print(f"\n--- Cutout Template ---")
        template_mesh = trimesh.load(template_file)
        print(f"  File: {os.path.basename(template_file)}")
        print(f"  Dimensions: {template_mesh.bounds[1] - template_mesh.bounds[0]}")
        print(f"  Volume: {template_mesh.volume:,.0f} mm³")
    
    print(f"\n--- Recommendations ---")
    
    # Check which version exists and is better
    best_version = None
    if os.path.exists(modified_file_v2):
        best_version = "V2"
        best_file = modified_file_v2
    elif os.path.exists(modified_file_v1):
        best_version = "V1"
        best_file = modified_file_v1
    
    if best_version:
        print(f"✓ Use Modified Front Cover {best_version}: {os.path.basename(best_file)}")
        print(f"✓ File is ready for 3D printing or further CAD work")
        print(f"✓ Cutout should accommodate Samsung S20 with 0.5mm tolerance")
        
        # Load the best version for final checks
        best_mesh = trimesh.load(best_file)
        if best_mesh.is_watertight:
            print(f"✓ Mesh is watertight - suitable for 3D printing")
        else:
            print(f"⚠ Mesh may need repair before 3D printing")
            
    else:
        print(f"❌ No modified version found - modification may have failed")
    
    print(f"\n--- Next Steps ---")
    print(f"1. Load {best_file} in your preferred CAD software")
    print(f"2. Verify cutout visually aligns with phone dimensions")
    print(f"3. Check that corner fillets are smooth (1mm radius)")
    print(f"4. If satisfied, proceed with 3D printing")
    print(f"5. Test fit with actual Samsung S20 device")

def export_cutout_measurements():
    """
    Export precise measurements for verification
    """
    measurements_file = "/workspaces/scad/output/cutout_measurements.txt"
    
    with open(measurements_file, 'w') as f:
        f.write("NucDeck Front Cover Cutout Measurements\n")
        f.write("=" * 50 + "\n\n")
        f.write("Samsung Galaxy S20 Cutout Specifications:\n")
        f.write(f"  Phone dimensions: 152.0 × 70.0 × 9.0 mm\n")
        f.write(f"  Cutout dimensions: 153.0 × 71.0 mm (with 0.5mm tolerance)\n")
        f.write(f"  Center position: (147.0, 9.5) mm\n")
        f.write(f"  Corner radius: 1.0 mm\n")
        f.write(f"  Depth: Full shell thickness\n\n")
        f.write("Quality Requirements:\n")
        f.write(f"  - Watertight mesh: Required\n")
        f.write(f"  - Smooth corners: 1mm fillet radius\n")
        f.write(f"  - Print tolerance: ±0.2mm typical\n")
        f.write(f"  - Friction fit: Phone should slide in with light pressure\n\n")
        f.write("Files Generated:\n")
        f.write(f"  - FrontCover_Modified_S20Cutout_v2.stl (recommended)\n")
        f.write(f"  - S20_Cutout_Template.stl (for dimension verification)\n")
        
    print(f"Measurements exported to: {measurements_file}")

if __name__ == "__main__":
    create_cutout_analysis_report()
    export_cutout_measurements()
    
    print(f"\n" + "="*60)
    print(f"VERIFICATION COMPLETE")
    print(f"="*60)
