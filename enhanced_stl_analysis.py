#!/usr/bin/env python3
"""
Enhanced STL Analysis with Feature Detection
Specifically looks for mounting points, cutouts, and internal cavities
"""

import trimesh
import numpy as np
import os

def detect_mounting_features(mesh, filepath):
    """
    Detect potential mounting points, holes, and cutouts in the mesh
    """
    print(f"\n--- Detailed Feature Detection for {os.path.basename(filepath)} ---")
    
    # Sample points to analyze internal structure
    bounds = mesh.bounds
    dimensions = bounds[1] - bounds[0]
    
    # Create a grid of test points to check if they're inside the mesh
    test_resolution = 20  # Number of test points per dimension
    x_points = np.linspace(bounds[0][0], bounds[1][0], test_resolution)
    y_points = np.linspace(bounds[0][1], bounds[1][1], test_resolution)
    z_points = np.linspace(bounds[0][2], bounds[1][2], test_resolution)
    
    internal_points = []
    external_points = []
    
    # Sample fewer points for performance
    for i in range(0, len(x_points), 3):
        for j in range(0, len(y_points), 2):
            for k in range(0, len(z_points), 3):
                point = [x_points[i], y_points[j], z_points[k]]
                if mesh.contains([point])[0]:
                    internal_points.append(point)
                else:
                    external_points.append(point)
    
    print(f"Internal cavity analysis:")
    print(f"  Total test points: {len(internal_points) + len(external_points)}")
    print(f"  Internal points: {len(internal_points)}")
    print(f"  External points: {len(external_points)}")
    
    if len(internal_points) > 0:
        internal_points = np.array(internal_points)
        cavity_bounds = [
            [internal_points[:, 0].min(), internal_points[:, 1].min(), internal_points[:, 2].min()],
            [internal_points[:, 0].max(), internal_points[:, 1].max(), internal_points[:, 2].max()]
        ]
        cavity_dims = np.array(cavity_bounds[1]) - np.array(cavity_bounds[0])
        print(f"  Largest internal cavity: {cavity_dims[0]:.1f} × {cavity_dims[1]:.1f} × {cavity_dims[2]:.1f} mm")
        print(f"  Cavity center: {np.mean(cavity_bounds, axis=0)}")
    
    # Analyze mesh thickness by looking at face normals and proximity
    try:
        # Find faces that might represent mounting surfaces (flat areas)
        face_normals = mesh.face_normals
        face_areas = mesh.area_faces
        
        # Look for large, flat surfaces (potential mounting areas)
        large_faces = face_areas > np.percentile(face_areas, 90)  # Top 10% largest faces
        flat_faces = np.abs(face_normals[:, 2]) > 0.8  # Nearly horizontal faces
        
        mounting_candidates = large_faces & flat_faces
        print(f"  Potential mounting surfaces: {np.sum(mounting_candidates)} large flat faces")
        
        if np.sum(mounting_candidates) > 0:
            mounting_face_indices = np.where(mounting_candidates)[0]
            for i, face_idx in enumerate(mounting_face_indices[:5]):  # Show first 5
                face_center = mesh.triangles_center[face_idx]
                face_area = face_areas[face_idx]
                print(f"    Mount {i+1}: center=({face_center[0]:.1f}, {face_center[1]:.1f}, {face_center[2]:.1f}), area={face_area:.1f}mm²")
    
    except Exception as e:
        print(f"  Could not analyze mounting features: {e}")
    
    # Look for circular features (holes, posts)
    try:
        # This is a simplified approach - real hole detection would need more sophisticated algorithms
        vertices = mesh.vertices
        
        # Look for vertices that form circular patterns (simplified)
        unique_z_levels = np.unique(np.round(vertices[:, 2], 1))
        
        print(f"  Z-level analysis (potential layers/features):")
        print(f"    Unique Z levels: {len(unique_z_levels)}")
        print(f"    Z range: {unique_z_levels.min():.1f} to {unique_z_levels.max():.1f} mm")
        
        # Find the most populated Z levels (likely to contain features)
        z_level_counts = []
        for z in unique_z_levels:
            count = np.sum(np.abs(vertices[:, 2] - z) < 0.5)  # Within 0.5mm
            z_level_counts.append(count)
        
        z_level_counts = np.array(z_level_counts)
        top_levels = unique_z_levels[np.argsort(z_level_counts)[-5:]]  # Top 5 levels
        
        print(f"    Most detailed Z levels: {[f'{z:.1f}mm' for z in top_levels]}")
        
    except Exception as e:
        print(f"  Could not analyze Z-levels: {e}")

def analyze_shell_thickness(mesh):
    """
    Attempt to estimate shell thickness at various points
    """
    try:
        # Use ray casting to estimate thickness
        bounds = mesh.bounds
        center = (bounds[0] + bounds[1]) / 2
        
        # Cast rays from center outward in different directions
        directions = [
            [1, 0, 0],   # X direction
            [-1, 0, 0],  # -X direction
            [0, 1, 0],   # Y direction
            [0, -1, 0],  # -Y direction
            [0, 0, 1],   # Z direction
            [0, 0, -1]   # -Z direction
        ]
        
        thicknesses = []
        for direction in directions:
            # Cast ray from center
            ray_origins = [center]
            ray_directions = [direction]
            
            locations, index_ray, index_tri = mesh.ray.intersects_location(
                ray_origins=ray_origins,
                ray_directions=ray_directions
            )
            
            if len(locations) >= 2:
                # Distance between first two intersections gives thickness
                distances = np.linalg.norm(locations[1] - locations[0])
                thicknesses.append(distances)
        
        if thicknesses:
            avg_thickness = np.mean(thicknesses)
            print(f"  Estimated shell thickness: {avg_thickness:.2f} mm (±{np.std(thicknesses):.2f})")
        
    except Exception as e:
        print(f"  Could not estimate shell thickness: {e}")

def main():
    # File paths
    housing_dir = "/workspaces/scad/Housing - STL"
    front_file = os.path.join(housing_dir, "Housing Front.STL")
    back_file = os.path.join(housing_dir, "Back Cover 7th Gen Intel NUC.STL")
    
    print("ENHANCED NucDeck Housing Analysis")
    print("=" * 60)
    
    # Load and analyze front cover
    if os.path.exists(front_file):
        print(f"\nLoading: {front_file}")
        front_mesh = trimesh.load(front_file)
        detect_mounting_features(front_mesh, front_file)
        analyze_shell_thickness(front_mesh)
    
    # Load and analyze back cover
    if os.path.exists(back_file):
        print(f"\nLoading: {back_file}")
        back_mesh = trimesh.load(back_file)
        detect_mounting_features(back_mesh, back_file)
        analyze_shell_thickness(back_mesh)
    
    print(f"\n=== DESIGN RECOMMENDATIONS ===")
    
    # Based on the analysis results from the first script
    print(f"Front cover: 294 × 19 × 115 mm")
    print(f"Back cover: 137 × 19 × 113 mm")
    print(f"\nObservations:")
    print(f"• Front cover is much wider - likely includes grip extensions")
    print(f"• Both parts are quite thin (19mm depth) - limited internal space")
    print(f"• Height is good for handheld device (115mm)")
    print(f"• Both have complex internal geometry (low volume/hull ratios)")
    
    print(f"\nComponent placement strategy:")
    print(f"• Phone pocket: Center of front cover, ~152×70×9mm clearance needed")
    print(f"• Battery: Back cover cavity, check for 90×60×12mm space")
    print(f"• Electronics: Distribute in available internal cavities")
    print(f"• Joysticks: Front cover, positioned in grip areas")
    print(f"• Buttons: Front cover, around phone pocket area")

if __name__ == "__main__":
    main()
