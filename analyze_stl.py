#!/usr/bin/env python3
"""
STL Analysis Script for NucDeck Housing Components
Analyzes front and back cover STL files to determine dimensions and internal features
"""

import trimesh
import numpy as np
import os
import sys

def analyze_stl_file(filepath):
    """
    Analyze an STL file and return comprehensive information about its geometry
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found")
        return None
    
    try:
        # Load the mesh
        mesh = trimesh.load(filepath)
        
        # Basic mesh info
        print(f"\n=== Analysis for: {os.path.basename(filepath)} ===")
        print(f"Vertices: {len(mesh.vertices)}")
        print(f"Faces: {len(mesh.faces)}")
        print(f"Volume: {mesh.volume:.2f} mm³")
        print(f"Surface Area: {mesh.area:.2f} mm²")
        print(f"Is Watertight: {mesh.is_watertight}")
        print(f"Is Winding Consistent: {mesh.is_winding_consistent}")
        
        # Bounding box analysis
        bounds = mesh.bounds
        min_bounds = bounds[0]
        max_bounds = bounds[1]
        dimensions = max_bounds - min_bounds
        
        print(f"\n--- Bounding Box ---")
        print(f"Min coordinates (X, Y, Z): ({min_bounds[0]:.2f}, {min_bounds[1]:.2f}, {min_bounds[2]:.2f}) mm")
        print(f"Max coordinates (X, Y, Z): ({max_bounds[0]:.2f}, {max_bounds[1]:.2f}, {max_bounds[2]:.2f}) mm")
        print(f"Dimensions (Width, Depth, Height): ({dimensions[0]:.2f}, {dimensions[1]:.2f}, {dimensions[2]:.2f}) mm")
        
        # Center of mass
        center = mesh.center_mass
        print(f"Center of mass: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}) mm")
        
        # Geometric center
        geometric_center = (min_bounds + max_bounds) / 2
        print(f"Geometric center: ({geometric_center[0]:.2f}, {geometric_center[1]:.2f}, {geometric_center[2]:.2f}) mm")
        
        # Check for internal features by analyzing mesh complexity
        print(f"\n--- Internal Feature Analysis ---")
        
        # Check if mesh has holes or complex internal geometry
        genus = mesh.euler_number  # Euler characteristic can indicate holes
        print(f"Euler characteristic: {genus}")
        
        # Analyze thickness by checking wall thickness at various points
        try:
            # Sample points on the surface and check distances
            surface_points = mesh.sample(1000)  # Sample 1000 points on surface
            
            # Calculate distances from surface points to the mesh
            distances = []
            for point in surface_points[:100]:  # Check first 100 points for performance
                # Find the closest point on the mesh to this surface point
                closest, distance, face_id = mesh.nearest.on_surface([point])
                distances.append(distance)
            
            avg_wall_thickness = np.mean(distances) * 2  # Approximate wall thickness
            print(f"Estimated average wall thickness: {avg_wall_thickness:.2f} mm")
            
        except Exception as e:
            print(f"Could not estimate wall thickness: {e}")
        
        # Check for overhangs and complex features
        # Analyze normal vectors to understand surface orientation
        face_normals = mesh.face_normals
        vertical_faces = np.abs(face_normals[:, 2]) < 0.1  # Nearly vertical faces
        horizontal_faces = np.abs(face_normals[:, 2]) > 0.9  # Nearly horizontal faces
        
        print(f"Vertical faces (potential walls): {np.sum(vertical_faces)}")
        print(f"Horizontal faces (potential floors/ceilings): {np.sum(horizontal_faces)}")
        
        # Check for potential mounting features by looking for small holes or protrusions
        try:
            # Look for cylindrical features (holes, posts, etc.)
            # This is a simplified analysis - in practice, you'd need more sophisticated feature detection
            convex_hull_volume = mesh.convex_hull.volume
            volume_ratio = mesh.volume / convex_hull_volume
            print(f"Volume to convex hull ratio: {volume_ratio:.3f}")
            if volume_ratio < 0.8:
                print("  -> Indicates potential internal cavities or complex features")
            else:
                print("  -> Relatively solid geometry")
                
        except Exception as e:
            print(f"Could not analyze convex hull: {e}")
        
        return {
            'filepath': filepath,
            'dimensions': dimensions,
            'bounds': bounds,
            'volume': mesh.volume,
            'area': mesh.area,
            'center_mass': center,
            'geometric_center': geometric_center,
            'is_watertight': mesh.is_watertight,
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces)
        }
        
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return None

def compare_meshes(front_data, back_data):
    """
    Compare two meshes and provide assembly insights
    """
    if not front_data or not back_data:
        return
    
    print(f"\n=== COMPARISON AND ASSEMBLY ANALYSIS ===")
    
    # Compare dimensions
    front_dims = front_data['dimensions']
    back_dims = back_data['dimensions']
    
    print(f"Front cover dimensions (W×D×H): {front_dims[0]:.1f} × {front_dims[1]:.1f} × {front_dims[2]:.1f} mm")
    print(f"Back cover dimensions (W×D×H): {back_dims[0]:.1f} × {back_dims[1]:.1f} × {back_dims[2]:.1f} mm")
    
    # Check if they're similar sizes (should be for mating parts)
    dim_diff = np.abs(front_dims - back_dims)
    print(f"Dimension differences: {dim_diff[0]:.1f} × {dim_diff[1]:.1f} × {dim_diff[2]:.1f} mm")
    
    # Estimate combined assembly dimensions
    max_dims = np.maximum(front_dims, back_dims)
    print(f"Estimated assembly envelope: {max_dims[0]:.1f} × {max_dims[1]:.1f} × {max_dims[2]:.1f} mm")
    
    # Volume comparison
    print(f"Volume comparison:")
    print(f"  Front: {front_data['volume']:.0f} mm³")
    print(f"  Back: {back_data['volume']:.0f} mm³")
    print(f"  Total: {front_data['volume'] + back_data['volume']:.0f} mm³")

def main():
    # Define the file paths - check both possible front cover options
    housing_dir = "/workspaces/scad/Housing - STL"
    
    front_files = [
        os.path.join(housing_dir, "Housing Front.STL"),
        os.path.join(housing_dir, "Housing Front - No RGB.STL")
    ]
    
    back_file = os.path.join(housing_dir, "Back Cover 7th Gen Intel NUC.STL")
    
    # Find which front file exists
    front_file = None
    for f in front_files:
        if os.path.exists(f):
            front_file = f
            break
    
    if not front_file:
        print("Error: No front cover STL file found")
        print(f"Looked for: {front_files}")
        return
    
    if not os.path.exists(back_file):
        print(f"Error: Back cover file not found: {back_file}")
        return
    
    print("NucDeck Housing STL Analysis")
    print("=" * 50)
    
    # Analyze both files
    front_data = analyze_stl_file(front_file)
    back_data = analyze_stl_file(back_file)
    
    # Compare and provide assembly insights
    compare_meshes(front_data, back_data)
    
    print(f"\n=== COMPONENT PLACEMENT RECOMMENDATIONS ===")
    if front_data and back_data:
        # Use the larger of the two for envelope calculations
        max_dims = np.maximum(front_data['dimensions'], back_data['dimensions'])
        
        print(f"Shell envelope: {max_dims[0]:.1f} × {max_dims[1]:.1f} × {max_dims[2]:.1f} mm")
        print(f"Recommended component placement zones:")
        print(f"  Central phone pocket: ~{max_dims[0]*0.6:.1f} × {max_dims[1]*0.8:.1f} mm")
        print(f"  Side grip areas: {max_dims[0]*0.15:.1f} mm wide each side")
        print(f"  Battery compartment depth: ~{max_dims[2]*0.6:.1f} mm")
        
        # Joystick placement suggestions
        joystick_y_offset = max_dims[1] * 0.3  # 30% from front
        joystick_x_spacing = max_dims[0] * 0.4  # 40% of width apart
        
        print(f"  Suggested joystick positions:")
        print(f"    Left: X={-joystick_x_spacing/2:.1f}, Y={joystick_y_offset:.1f}")
        print(f"    Right: X={joystick_x_spacing/2:.1f}, Y={joystick_y_offset:.1f}")

if __name__ == "__main__":
    main()
