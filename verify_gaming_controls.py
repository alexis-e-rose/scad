#!/usr/bin/env python3
"""
Gaming Control Verification Script for Modified NucDeck Front Cover
Verifies presence and dimensions of gaming control cutouts in the S20-modified front shell
"""

import trimesh
import numpy as np
import json
import os
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

def load_mesh(filepath):
    """Load and validate the mesh file"""
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found")
        return None
    
    try:
        mesh = trimesh.load(filepath)
        print(f"Loaded mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        print(f"Watertight: {mesh.is_watertight}")
        print(f"Bounds: {mesh.bounds}")
        return mesh
    except Exception as e:
        print(f"Error loading mesh: {e}")
        return None

def detect_circular_holes(mesh, min_radius=5, max_radius=20, samples=1000):
    """
    Detect circular holes in the mesh by analyzing boundary loops
    """
    holes = []
    
    try:
        # Sample points on the mesh surface
        surface_points = mesh.sample(samples)
        
        # Find boundary edges (edges that belong to only one face)
        edges = mesh.edges_unique
        edge_face_count = np.zeros(len(edges))
        
        for i, edge in enumerate(edges):
            # Count how many faces contain this edge
            faces_with_edge = []
            for j, face in enumerate(mesh.faces):
                if edge[0] in face and edge[1] in face:
                    faces_with_edge.append(j)
            edge_face_count[i] = len(faces_with_edge)
        
        # Boundary edges have count == 1
        boundary_edges = edges[edge_face_count == 1]
        
        if len(boundary_edges) > 0:
            # Cluster boundary points to find separate holes
            boundary_points = mesh.vertices[boundary_edges.flatten()]
            
            if len(boundary_points) > 3:
                # Use DBSCAN to cluster boundary points
                clustering = DBSCAN(eps=5.0, min_samples=3).fit(boundary_points)
                labels = clustering.labels_
                
                # Analyze each cluster
                for label in set(labels):
                    if label == -1:  # Skip noise
                        continue
                    
                    cluster_points = boundary_points[labels == label]
                    if len(cluster_points) < 4:
                        continue
                    
                    # Fit circle to cluster points (project to XY plane)
                    xy_points = cluster_points[:, :2]
                    center, radius = fit_circle_2d(xy_points)
                    
                    if min_radius <= radius <= max_radius:
                        # Get Z coordinate (average of cluster points)
                        z_coord = np.mean(cluster_points[:, 2])
                        
                        holes.append({
                            'center': [center[0], center[1], z_coord],
                            'radius': radius,
                            'points': cluster_points,
                            'type': 'circular'
                        })
                        
                        print(f"Found circular hole: center=({center[0]:.1f}, {center[1]:.1f}, {z_coord:.1f}), radius={radius:.1f}mm")
    
    except Exception as e:
        print(f"Error in hole detection: {e}")
    
    return holes

def fit_circle_2d(points):
    """
    Fit a circle to 2D points using least squares
    Returns center (x, y) and radius
    """
    if len(points) < 3:
        return [0, 0], 0
    
    try:
        # Method: Fit circle using algebraic approach
        x = points[:, 0]
        y = points[:, 1]
        
        # Set up the system of equations
        A = np.column_stack([2*x, 2*y, np.ones(len(x))])
        b = x**2 + y**2
        
        # Solve for circle parameters
        params = np.linalg.lstsq(A, b, rcond=None)[0]
        center_x, center_y, c = params
        
        # Calculate radius
        radius = np.sqrt(center_x**2 + center_y**2 + c)
        
        return [center_x, center_y], radius
    
    except Exception as e:
        print(f"Error fitting circle: {e}")
        return [0, 0], 0

def detect_rectangular_features(mesh):
    """
    Detect rectangular cutouts by analyzing mesh geometry
    """
    rectangles = []
    
    try:
        # Get all faces and their normals
        face_centers = mesh.triangles.mean(axis=1)
        face_normals = mesh.face_normals
        
        # Look for clusters of faces with similar normals (indicating flat surfaces)
        # Focus on faces facing upward (Z normal > 0.8) - these could be cutout floors
        upward_faces = face_normals[:, 2] > 0.8
        upward_centers = face_centers[upward_faces]
        
        if len(upward_centers) > 0:
            # Cluster upward-facing face centers
            clustering = DBSCAN(eps=3.0, min_samples=5).fit(upward_centers)
            labels = clustering.labels_
            
            for label in set(labels):
                if label == -1:
                    continue
                
                cluster_centers = upward_centers[labels == label]
                if len(cluster_centers) < 4:
                    continue
                
                # Analyze bounding box of cluster
                min_bounds = np.min(cluster_centers, axis=0)
                max_bounds = np.max(cluster_centers, axis=0)
                dimensions = max_bounds - min_bounds
                
                # Check if it could be a rectangular feature
                if 5 < dimensions[0] < 50 and 5 < dimensions[1] < 50:
                    center = (min_bounds + max_bounds) / 2
                    
                    rectangles.append({
                        'center': center,
                        'dimensions': dimensions,
                        'min_bounds': min_bounds,
                        'max_bounds': max_bounds,
                        'type': 'rectangular'
                    })
                    
                    print(f"Found rectangular feature: center=({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f}), "
                          f"size={dimensions[0]:.1f}×{dimensions[1]:.1f}mm")
    
    except Exception as e:
        print(f"Error in rectangular detection: {e}")
    
    return rectangles

def analyze_gaming_controls(mesh):
    """
    Comprehensive analysis to detect gaming control cutouts
    """
    print("\n=== GAMING CONTROL DETECTION ===")
    
    results = {
        'joysticks': [],
        'dpad': [],
        'abxy': [],
        'start_menu': [],
        'shoulder_buttons': [],
        'triggers': [],
        'other_features': []
    }
    
    # Detect circular holes (joysticks, ABXY, Start/Menu)
    circular_holes = detect_circular_holes(mesh, min_radius=4, max_radius=20, samples=2000)
    
    # Classify circular holes by size
    for hole in circular_holes:
        radius = hole['radius']
        center = hole['center']
        
        if 14 <= radius <= 18:  # Joystick holes (~16mm radius for ∅32mm)
            results['joysticks'].append({
                'center': center,
                'radius': radius,
                'diameter': radius * 2,
                'type': 'joystick'
            })
            print(f"  ✓ Joystick detected: ∅{radius*2:.1f}mm at ({center[0]:.1f}, {center[1]:.1f})")
            
        elif 5 <= radius <= 7:  # ABXY buttons (~6mm radius for ∅12mm)
            results['abxy'].append({
                'center': center,
                'radius': radius,
                'diameter': radius * 2,
                'type': 'abxy'
            })
            print(f"  ✓ ABXY button detected: ∅{radius*2:.1f}mm at ({center[0]:.1f}, {center[1]:.1f})")
            
        elif 3 <= radius <= 5:  # Start/Menu buttons (~4mm radius for ∅8mm)
            results['start_menu'].append({
                'center': center,
                'radius': radius,
                'diameter': radius * 2,
                'type': 'start_menu'
            })
            print(f"  ✓ Start/Menu button detected: ∅{radius*2:.1f}mm at ({center[0]:.1f}, {center[1]:.1f})")
            
        else:
            results['other_features'].append(hole)
    
    # Detect rectangular features (D-pad, shoulder buttons, triggers)
    rectangular_features = detect_rectangular_features(mesh)
    
    for rect in rectangular_features:
        dims = rect['dimensions']
        center = rect['center']
        
        if 20 <= dims[0] <= 30 and 20 <= dims[1] <= 30:  # D-pad (~24×24mm)
            results['dpad'].append({
                'center': center,
                'dimensions': dims,
                'type': 'dpad'
            })
            print(f"  ✓ D-pad detected: {dims[0]:.1f}×{dims[1]:.1f}mm at ({center[0]:.1f}, {center[1]:.1f})")
            
        elif (8 <= dims[0] <= 15 and 3 <= dims[1] <= 6) or (3 <= dims[0] <= 6 and 8 <= dims[1] <= 15):  # Shoulder buttons
            results['shoulder_buttons'].append({
                'center': center,
                'dimensions': dims,
                'type': 'shoulder'
            })
            print(f"  ✓ Shoulder button detected: {dims[0]:.1f}×{dims[1]:.1f}mm at ({center[0]:.1f}, {center[1]:.1f})")
            
        elif (15 <= dims[0] <= 25 and 6 <= dims[1] <= 12) or (6 <= dims[0] <= 12 and 15 <= dims[1] <= 25):  # Triggers
            results['triggers'].append({
                'center': center,
                'dimensions': dims,
                'type': 'trigger'
            })
            print(f"  ✓ Trigger detected: {dims[0]:.1f}×{dims[1]:.1f}mm at ({center[0]:.1f}, {center[1]:.1f})")
            
        else:
            results['other_features'].append(rect)
    
    return results

def validate_gaming_layout(results):
    """
    Validate the detected gaming controls against expected layout
    """
    print("\n=== LAYOUT VALIDATION ===")
    
    validation = {
        'joysticks': {'expected': 2, 'found': len(results['joysticks']), 'valid': False},
        'dpad': {'expected': 1, 'found': len(results['dpad']), 'valid': False},
        'abxy': {'expected': 4, 'found': len(results['abxy']), 'valid': False},
        'start_menu': {'expected': 2, 'found': len(results['start_menu']), 'valid': False},
        'shoulder_buttons': {'expected': 2, 'found': len(results['shoulder_buttons']), 'valid': False},
        'triggers': {'expected': 2, 'found': len(results['triggers']), 'valid': False}
    }
    
    # Check each control type
    for control_type, data in validation.items():
        found = data['found']
        expected = data['expected']
        
        if found == expected:
            data['valid'] = True
            print(f"  ✓ {control_type.upper()}: {found}/{expected} - VALID")
        elif found > expected:
            data['valid'] = False
            print(f"  ⚠ {control_type.upper()}: {found}/{expected} - TOO MANY (possible duplicates)")
        else:
            data['valid'] = False
            print(f"  ✗ {control_type.upper()}: {found}/{expected} - MISSING")
    
    # Overall validation
    all_valid = all(data['valid'] for data in validation.values())
    
    if all_valid:
        print("\n✓ ALL GAMING CONTROLS DETECTED AND VALID")
        return True, validation
    else:
        print("\n⚠ SOME GAMING CONTROLS MISSING OR INVALID")
        return False, validation

def export_feature_map(results, mesh, output_path):
    """
    Export a JSON map of all detected features
    """
    feature_map = {
        'mesh_info': {
            'bounds': mesh.bounds.tolist(),
            'dimensions': (mesh.bounds[1] - mesh.bounds[0]).tolist(),
            'center': mesh.center_mass.tolist(),
            'volume': float(mesh.volume),
            'area': float(mesh.area)
        },
        'gaming_controls': {}
    }
    
    # Add all detected features
    for control_type, features in results.items():
        if features:
            feature_map['gaming_controls'][control_type] = []
            for feature in features:
                feature_data = {
                    'center': [float(x) for x in feature['center']],
                    'type': feature.get('type', control_type)
                }
                
                if 'radius' in feature:
                    feature_data['radius'] = float(feature['radius'])
                    feature_data['diameter'] = float(feature['diameter'])
                if 'dimensions' in feature:
                    feature_data['dimensions'] = [float(x) for x in feature['dimensions']]
                
                feature_map['gaming_controls'][control_type].append(feature_data)
    
    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(feature_map, f, indent=2)
    
    print(f"\nFeature map exported to: {output_path}")
    return feature_map

def main():
    # Load the modified front cover
    mesh_path = "/workspaces/scad/output/FrontCover_Modified_S20Cutout_v2.stl"
    
    mesh = load_mesh(mesh_path)
    if not mesh:
        return
    
    print(f"\nAnalyzing gaming controls in: {os.path.basename(mesh_path)}")
    print("=" * 60)
    
    # Detect all gaming control features
    results = analyze_gaming_controls(mesh)
    
    # Validate the layout
    is_valid, validation = validate_gaming_layout(results)
    
    # Export feature map
    output_dir = "/workspaces/scad/output"
    os.makedirs(output_dir, exist_ok=True)
    
    feature_map_path = os.path.join(output_dir, "gaming_controls_feature_map.json")
    feature_map = export_feature_map(results, mesh, feature_map_path)
    
    # Generate recommendations
    print("\n=== RECOMMENDATIONS ===")
    
    if is_valid:
        print("✓ All gaming controls are present and valid!")
        print("✓ Ready to proceed to Phase 3: Back shell modification")
        print("✓ Feature map exported for future reference")
    else:
        print("⚠ Issues detected with gaming controls:")
        
        for control_type, data in validation.items():
            if not data['valid']:
                found = data['found']
                expected = data['expected']
                
                if found < expected:
                    print(f"  - {control_type.upper()}: Missing {expected - found} features")
                elif found > expected:
                    print(f"  - {control_type.upper()}: {found - expected} extra features detected (check for duplicates)")
        
        print("\nRecommendations:")
        print("1. Review the feature map JSON for detailed coordinates")
        print("2. Manually inspect the mesh in CAD software")
        print("3. If features are missing, they may need to be added manually")
    
    print(f"\nDetailed analysis saved to: {feature_map_path}")

if __name__ == "__main__":
    main()
