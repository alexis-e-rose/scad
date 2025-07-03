#!/usr/bin/env python3
"""
NucDeck Feature Detection Script
Analyzes the modified front cover to identify existing gaming control features
"""

import trimesh
import numpy as np
import os
import json
from scipy.spatial.distance import cdist
from scipy.spatial import ConvexHull

def detect_circular_features(mesh, min_radius=3, max_radius=20, center_z_range=None):
    """
    Detect circular holes/features in the mesh (joysticks, buttons)
    """
    print(f"Detecting circular features (radius {min_radius}-{max_radius} mm)...")
    
    vertices = mesh.vertices
    
    # Filter by Z-range if specified
    if center_z_range:
        z_mask = (vertices[:, 2] >= center_z_range[0]) & (vertices[:, 2] <= center_z_range[1])
        vertices = vertices[z_mask]
    
    # Group vertices by Z-level to find circular patterns
    z_levels = np.round(vertices[:, 2], 1)
    unique_z = np.unique(z_levels)
    
    circular_features = []
    
    for z in unique_z:
        level_vertices = vertices[np.abs(vertices[:, 2] - z) < 0.5]
        
        if len(level_vertices) < 10:  # Skip levels with few vertices
            continue
        
        # Look for circular patterns by finding vertex clusters
        # Use 2D coordinates only (X, Y)
        xy_coords = level_vertices[:, :2]
        
        # Find potential centers by clustering
        from sklearn.cluster import DBSCAN
        clustering = DBSCAN(eps=2.0, min_samples=5).fit(xy_coords)
        labels = clustering.labels_
        
        for label in set(labels):
            if label == -1:  # Skip noise
                continue
                
            cluster_points = xy_coords[labels == label]
            
            if len(cluster_points) < 8:  # Need enough points for circle
                continue
            
            # Find center and radius of this cluster
            center = np.mean(cluster_points, axis=0)
            distances = np.linalg.norm(cluster_points - center, axis=1)
            radius = np.mean(distances)
            radius_std = np.std(distances)
            
            # Check if it's circular (low standard deviation)
            if radius_std < radius * 0.3 and min_radius <= radius <= max_radius:
                circular_features.append({
                    'center': [center[0], center[1], z],
                    'radius': radius,
                    'radius_std': radius_std,
                    'point_count': len(cluster_points),
                    'circularity': 1.0 - (radius_std / radius)
                })
    
    return circular_features

def detect_rectangular_features(mesh, min_area=100, max_area=1000):
    """
    Detect rectangular features (D-pad, button clusters)
    """
    print(f"Detecting rectangular features (area {min_area}-{max_area} mm²)...")
    
    # Analyze face normals and areas to find flat rectangular regions
    face_normals = mesh.face_normals
    face_areas = mesh.area_faces
    face_centers = mesh.triangles_center
    
    # Look for large, flat faces (potential rectangular features)
    horizontal_faces = np.abs(face_normals[:, 2]) > 0.8  # Nearly horizontal
    large_faces = face_areas > 50  # Significant area
    
    candidate_faces = horizontal_faces & large_faces
    candidate_indices = np.where(candidate_faces)[0]
    
    rectangular_features = []
    
    if len(candidate_indices) > 0:
        # Group nearby face centers
        centers = face_centers[candidate_indices]
        
        from sklearn.cluster import DBSCAN
        clustering = DBSCAN(eps=10.0, min_samples=2).fit(centers[:, :2])  # Cluster in XY
        labels = clustering.labels_
        
        for label in set(labels):
            if label == -1:
                continue
                
            cluster_faces = candidate_indices[labels == label]
            cluster_centers = centers[labels == label]
            cluster_areas = face_areas[cluster_faces]
            
            # Calculate bounding box of this cluster
            min_coords = np.min(cluster_centers, axis=0)
            max_coords = np.max(cluster_centers, axis=0)
            dimensions = max_coords - min_coords
            
            total_area = np.sum(cluster_areas)
            
            if min_area <= total_area <= max_area:
                rectangular_features.append({
                    'center': np.mean(cluster_centers, axis=0),
                    'min_coords': min_coords,
                    'max_coords': max_coords,
                    'dimensions': dimensions,
                    'area': total_area,
                    'face_count': len(cluster_faces)
                })
    
    return rectangular_features

def classify_detected_features(circular_features, rectangular_features):
    """
    Classify detected features based on size and position
    """
    print("Classifying detected features...")
    
    classified = {
        'joysticks': [],
        'large_buttons': [],  # ABXY
        'small_buttons': [],  # Start/Menu
        'dpad': [],
        'triggers': [],
        'unknown_circular': [],
        'unknown_rectangular': []
    }
    
    # Classify circular features by radius
    for feature in circular_features:
        radius = feature['radius']
        center = feature['center']
        
        if 14 <= radius <= 18:  # Joystick holes (∅32mm = radius 16mm)
            feature['type'] = 'joystick'
            classified['joysticks'].append(feature)
        elif 5 <= radius <= 8:  # ABXY buttons (∅12mm = radius 6mm)
            feature['type'] = 'large_button'
            classified['large_buttons'].append(feature)
        elif 3 <= radius <= 5:  # Start/Menu buttons (∅8mm = radius 4mm)
            feature['type'] = 'small_button'
            classified['small_buttons'].append(feature)
        else:
            feature['type'] = 'unknown'
            classified['unknown_circular'].append(feature)
    
    # Classify rectangular features by size
    for feature in rectangular_features:
        dims = feature['dimensions']
        area = feature['area']
        
        # D-pad should be roughly square, ~24x24mm
        if 20 <= dims[0] <= 30 and 20 <= dims[1] <= 30 and abs(dims[0] - dims[1]) < 5:
            feature['type'] = 'dpad'
            classified['dpad'].append(feature)
        # Trigger slots (18x8mm)
        elif 15 <= max(dims[:2]) <= 22 and 6 <= min(dims[:2]) <= 10:
            feature['type'] = 'trigger'
            classified['triggers'].append(feature)
        else:
            feature['type'] = 'unknown'
            classified['unknown_rectangular'].append(feature)
    
    return classified

def analyze_front_cover_features():
    """
    Main function to analyze the modified front cover features
    """
    # Load the modified front cover
    modified_file = "/workspaces/scad/output/FrontCover_Modified_S20Cutout_v2.stl"
    
    if not os.path.exists(modified_file):
        print(f"Error: Modified front cover not found: {modified_file}")
        return None
    
    print("NUCDECK FRONT COVER FEATURE DETECTION")
    print("=" * 60)
    print(f"Analyzing: {os.path.basename(modified_file)}")
    
    # Load mesh
    mesh = trimesh.load(modified_file)
    
    print(f"\nMesh properties:")
    print(f"  Vertices: {len(mesh.vertices):,}")
    print(f"  Faces: {len(mesh.faces):,}")
    print(f"  Bounds: {mesh.bounds[0]} to {mesh.bounds[1]}")
    print(f"  Watertight: {mesh.is_watertight}")
    
    # Install sklearn if not available
    try:
        from sklearn.cluster import DBSCAN
    except ImportError:
        print("Installing scikit-learn for clustering...")
        os.system("/home/codespace/.python/current/bin/python3 -m pip install scikit-learn")
        from sklearn.cluster import DBSCAN
    
    # Detect circular features (joysticks, buttons)
    print(f"\n" + "="*40)
    circular_features = detect_circular_features(mesh, min_radius=3, max_radius=20)
    
    print(f"Found {len(circular_features)} circular features:")
    for i, feature in enumerate(circular_features):
        center = feature['center']
        radius = feature['radius']
        circularity = feature['circularity']
        print(f"  {i+1}: Center=({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f}), "
              f"R={radius:.1f}mm, Circularity={circularity:.2f}")
    
    # Detect rectangular features (D-pad, trigger slots)
    print(f"\n" + "="*40)
    rectangular_features = detect_rectangular_features(mesh, min_area=50, max_area=2000)
    
    print(f"Found {len(rectangular_features)} rectangular features:")
    for i, feature in enumerate(rectangular_features):
        center = feature['center']
        dims = feature['dimensions']
        area = feature['area']
        print(f"  {i+1}: Center=({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f}), "
              f"Size={dims[0]:.1f}×{dims[1]:.1f}mm, Area={area:.0f}mm²")
    
    # Classify features
    print(f"\n" + "="*40)
    classified = classify_detected_features(circular_features, rectangular_features)
    
    return classified, mesh

def verify_expected_features(classified):
    """
    Verify that all expected gaming control features are present
    """
    print("FEATURE VERIFICATION REPORT")
    print("=" * 40)
    
    expected_features = {
        'joysticks': {'count': 2, 'spec': '∅32mm (radius ~16mm)'},
        'large_buttons': {'count': 4, 'spec': '∅12mm ABXY buttons'},
        'small_buttons': {'count': 2, 'spec': '∅8mm Start/Menu buttons'},
        'dpad': {'count': 1, 'spec': '24×24mm square with rounded corners'},
        'triggers': {'count': 2, 'spec': '18×8mm trigger slots (L2/R2)'}
    }
    
    verification_results = {}
    all_features_present = True
    
    for feature_type, expected in expected_features.items():
        found_count = len(classified[feature_type])
        expected_count = expected['count']
        spec = expected['spec']
        
        status = "✓ FOUND" if found_count >= expected_count else "❌ MISSING"
        if found_count > expected_count:
            status = f"⚠ EXTRA ({found_count} found, {expected_count} expected)"
        
        print(f"{feature_type.upper()}: {status}")
        print(f"  Expected: {expected_count} × {spec}")
        print(f"  Found: {found_count}")
        
        if found_count > 0:
            print(f"  Detected locations:")
            for i, feature in enumerate(classified[feature_type]):
                center = feature['center']
                if feature_type in ['joysticks', 'large_buttons', 'small_buttons']:
                    radius = feature['radius']
                    print(f"    {i+1}: ({center[0]:.1f}, {center[1]:.1f}) R={radius:.1f}mm")
                else:
                    dims = feature['dimensions']
                    print(f"    {i+1}: ({center[0]:.1f}, {center[1]:.1f}) {dims[0]:.1f}×{dims[1]:.1f}mm")
        
        verification_results[feature_type] = {
            'expected': expected_count,
            'found': found_count,
            'status': 'ok' if found_count >= expected_count else 'missing'
        }
        
        if found_count < expected_count:
            all_features_present = False
        
        print()
    
    # Check for shoulder buttons (L1/R1) - these might be harder to detect
    print("ADDITIONAL FEATURES:")
    print("L1/R1 Shoulder buttons (11×4mm): Manual verification needed")
    print("  - These may be on the edges and harder to detect automatically")
    print("  - Check top edge of shell for rectangular cutouts")
    
    return verification_results, all_features_present

def export_feature_map(classified, mesh_bounds, output_file):
    """
    Export a JSON map of detected features for reference
    """
    feature_map = {
        'metadata': {
            'generated_by': 'NucDeck Feature Detection Script',
            'mesh_file': 'FrontCover_Modified_S20Cutout_v2.stl',
            'mesh_bounds': {
                'min': mesh_bounds[0].tolist(),
                'max': mesh_bounds[1].tolist()
            },
            'units': 'millimeters'
        },
        'features': {}
    }
    
    for feature_type, features in classified.items():
        if len(features) > 0:
            feature_map['features'][feature_type] = []
            for feature in features:
                center = feature['center']
                if isinstance(center, np.ndarray):
                    center = center.tolist()
                
                feature_data = {
                    'center': center,
                    'type': feature.get('type', feature_type)
                }
                
                if 'radius' in feature:
                    feature_data['radius'] = feature['radius']
                    feature_data['diameter'] = feature['radius'] * 2
                
                if 'dimensions' in feature:
                    dims = feature['dimensions']
                    if isinstance(dims, np.ndarray):
                        dims = dims.tolist()
                    feature_data['dimensions'] = dims
                    feature_data['area'] = feature['area']
                
                feature_map['features'][feature_type].append(feature_data)
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(feature_map, f, indent=2)
    
    print(f"Feature map exported to: {output_file}")
    return feature_map

def main():
    # Analyze features
    result = analyze_front_cover_features()
    
    if result is None:
        return
    
    classified, mesh = result
    
    # Verify expected features
    print(f"\n" + "="*60)
    verification_results, all_present = verify_expected_features(classified)
    
    # Export feature map
    output_file = "/workspaces/scad/output/front_cover_feature_map.json"
    feature_map = export_feature_map(classified, mesh.bounds, output_file)
    
    # Summary and recommendations
    print(f"\n" + "="*60)
    print("SUMMARY AND RECOMMENDATIONS")
    print("=" * 60)
    
    if all_present:
        print("✅ ALL EXPECTED FEATURES DETECTED!")
        print("The front cover appears to have all required gaming controls.")
        print("\nReady to proceed to Phase 3: Back shell modification")
        print("- Battery compartment (90×60×12mm)")
        print("- Electronics pockets (TP4056, PD boost, indicators)")
        print("- Cable routing channels")
        
    else:
        print("⚠ SOME FEATURES MISSING OR UNCLEAR")
        print("Missing features may need manual verification or creation.")
        
        missing_features = []
        for feature_type, result in verification_results.items():
            if result['status'] == 'missing':
                missing_features.append(feature_type)
        
        if missing_features:
            print(f"\nMissing: {', '.join(missing_features)}")
            print("Recommendation: Visual inspection in CAD software needed")
    
    print(f"\nFeature detection complete. Results saved to:")
    print(f"  {output_file}")

if __name__ == "__main__":
    main()
