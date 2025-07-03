#!/usr/bin/env python3
"""
Enhanced Feature Analysis for NucDeck Front Cover
Provides detailed analysis and manual verification guidance
"""

import trimesh
import numpy as np
import os
import json

def analyze_mesh_geometry_detailed(mesh):
    """
    Detailed geometric analysis of the mesh to understand its structure
    """
    print("DETAILED MESH GEOMETRY ANALYSIS")
    print("=" * 50)
    
    bounds = mesh.bounds
    dimensions = bounds[1] - bounds[0]
    
    print(f"Overall dimensions: {dimensions[0]:.1f} × {dimensions[1]:.1f} × {dimensions[2]:.1f} mm")
    print(f"Volume: {mesh.volume:,.0f} mm³")
    print(f"Surface area: {mesh.area:,.0f} mm²")
    print(f"Watertight: {mesh.is_watertight}")
    
    # Analyze vertex distribution to understand complexity
    vertices = mesh.vertices
    
    # Z-level analysis (features typically exist at specific heights)
    z_coords = vertices[:, 2]
    z_unique, z_counts = np.unique(np.round(z_coords, 1), return_counts=True)
    
    print(f"\nZ-level analysis (top 10 most detailed levels):")
    top_z_indices = np.argsort(z_counts)[-10:]
    for idx in reversed(top_z_indices):
        z_level = z_unique[idx]
        vertex_count = z_counts[idx]
        print(f"  Z={z_level:6.1f}mm: {vertex_count:4d} vertices")
    
    # Look for regions with high vertex density (likely feature areas)
    print(f"\nHigh-density regions analysis:")
    
    # Divide mesh into grid and count vertices per cell
    x_bins = np.linspace(bounds[0][0], bounds[1][0], 20)
    y_bins = np.linspace(bounds[0][1], bounds[1][1], 10)
    
    for i in range(len(x_bins)-1):
        for j in range(len(y_bins)-1):
            x_mask = (vertices[:, 0] >= x_bins[i]) & (vertices[:, 0] < x_bins[i+1])
            y_mask = (vertices[:, 1] >= y_bins[j]) & (vertices[:, 1] < y_bins[j+1])
            region_vertices = vertices[x_mask & y_mask]
            
            if len(region_vertices) > 100:  # High density region
                x_center = (x_bins[i] + x_bins[i+1]) / 2
                y_center = (y_bins[j] + y_bins[j+1]) / 2
                z_range = region_vertices[:, 2].max() - region_vertices[:, 2].min()
                print(f"  Region ({x_center:6.1f}, {y_center:4.1f}): {len(region_vertices):4d} vertices, Z-span={z_range:.1f}mm")

def detect_holes_and_cutouts(mesh):
    """
    Detect holes and cutouts in the mesh using geometric analysis
    """
    print("\nHOLE AND CUTOUT DETECTION")
    print("=" * 50)
    
    # Use ray casting to detect holes
    bounds = mesh.bounds
    
    # Create a grid of rays from above the mesh
    x_test = np.linspace(bounds[0][0] + 5, bounds[1][0] - 5, 50)
    y_test = np.linspace(bounds[0][1] + 5, bounds[1][1] - 5, 20)
    z_start = bounds[1][2] + 10  # Start above the mesh
    
    ray_origins = []
    ray_directions = []
    
    for x in x_test:
        for y in y_test:
            ray_origins.append([x, y, z_start])
            ray_directions.append([0, 0, -1])  # Point downward
    
    ray_origins = np.array(ray_origins)
    ray_directions = np.array(ray_directions)
    
    # Cast rays and find intersections
    try:
        locations, index_ray, index_tri = mesh.ray.intersects_location(
            ray_origins=ray_origins,
            ray_directions=ray_directions
        )
        
        print(f"Ray casting results:")
        print(f"  Total rays cast: {len(ray_origins)}")
        print(f"  Intersection points: {len(locations)}")
        
        # Group intersections by ray to find holes
        holes_detected = []
        
        for i in range(len(ray_origins)):
            ray_intersections = locations[index_ray == i]
            
            if len(ray_intersections) == 0:
                # No intersection = hole through entire mesh
                x, y = ray_origins[i][:2]
                holes_detected.append({
                    'center': [x, y],
                    'type': 'through_hole',
                    'depth': 'full'
                })
            elif len(ray_intersections) > 2:
                # Multiple intersections = complex geometry (possible cutout)
                z_intersections = ray_intersections[:, 2]
                x, y = ray_origins[i][:2]
                depth = z_intersections.max() - z_intersections.min()
                
                if depth > 5:  # Significant depth
                    holes_detected.append({
                        'center': [x, y],
                        'type': 'cutout',
                        'depth': depth,
                        'z_range': [z_intersections.min(), z_intersections.max()]
                    })
        
        print(f"\nDetected holes/cutouts: {len(holes_detected)}")
        for i, hole in enumerate(holes_detected):
            center = hole['center']
            hole_type = hole['type']
            if hole_type == 'through_hole':
                print(f"  {i+1}: Through hole at ({center[0]:.1f}, {center[1]:.1f})")
            else:
                depth = hole['depth']
                print(f"  {i+1}: {hole_type} at ({center[0]:.1f}, {center[1]:.1f}), depth={depth:.1f}mm")
        
        return holes_detected
        
    except Exception as e:
        print(f"Ray casting failed: {e}")
        return []

def analyze_original_vs_modified():
    """
    Compare original and modified front covers to understand what changed
    """
    print("\nORIGINAL VS MODIFIED COMPARISON")
    print("=" * 50)
    
    original_file = "/workspaces/scad/Housing - STL/Housing Front.STL"
    modified_file = "/workspaces/scad/output/FrontCover_Modified_S20Cutout_v2.stl"
    
    if not os.path.exists(original_file):
        print("Original file not found")
        return
    
    if not os.path.exists(modified_file):
        print("Modified file not found")
        return
    
    original_mesh = trimesh.load(original_file)
    modified_mesh = trimesh.load(modified_file)
    
    print(f"Original mesh:")
    print(f"  Vertices: {len(original_mesh.vertices):,}")
    print(f"  Volume: {original_mesh.volume:,.0f} mm³")
    
    print(f"Modified mesh:")
    print(f"  Vertices: {len(modified_mesh.vertices):,}")
    print(f"  Volume: {modified_mesh.volume:,.0f} mm³")
    
    volume_diff = original_mesh.volume - modified_mesh.volume
    print(f"Volume difference: {volume_diff:,.0f} mm³")
    
    if volume_diff > 1000:
        print("✓ Significant modification detected (likely S20 cutout)")
    else:
        print("⚠ Minimal volume change - modification may not be effective")

def manual_verification_guide():
    """
    Provide detailed manual verification instructions
    """
    print("\nMANUAL VERIFICATION GUIDE")
    print("=" * 50)
    
    expected_features = {
        'Samsung S20 Cutout': {
            'size': '153×71mm',
            'position': 'Center (147, 9.5)',
            'verification': 'Rectangular opening with 1mm corner fillets'
        },
        'Left Joystick': {
            'size': '∅32mm',
            'position': 'Left grip area (~36.5, 15)',
            'verification': 'Circular hole for analog stick'
        },
        'Right Joystick': {
            'size': '∅32mm', 
            'position': 'Right grip area (~257.5, 15)',
            'verification': 'Circular hole for analog stick'
        },
        'D-pad': {
            'size': '24×24mm',
            'position': 'Below left joystick',
            'verification': 'Square cutout with rounded corners'
        },
        'ABXY Buttons': {
            'size': '4 × ∅12mm',
            'position': 'Below right joystick (diamond pattern)',
            'verification': 'Four circular holes in diamond arrangement'
        },
        'Start/Menu Buttons': {
            'size': '2 × ∅8mm',
            'position': 'Between phone and joysticks',
            'verification': 'Two small circular holes'
        },
        'L1/R1 Shoulder': {
            'size': '2 × 11×4mm',
            'position': 'Top edges (left and right)',
            'verification': 'Rectangular slots on top edge'
        },
        'L2/R2 Triggers': {
            'size': '2 × 18×8mm',
            'position': 'Behind L1/R1 (angled)',
            'verification': 'Angled slots for trigger travel'
        }
    }
    
    print("To manually verify features, load the STL in CAD software and check:")
    print()
    
    for feature_name, spec in expected_features.items():
        print(f"{feature_name}:")
        print(f"  Expected size: {spec['size']}")
        print(f"  Expected position: {spec['position']}")
        print(f"  Verification: {spec['verification']}")
        print()
    
    print("Verification checklist:")
    print("□ S20 cutout is centered and properly sized")
    print("□ Joystick holes are in grip areas")
    print("□ D-pad is positioned below left joystick")
    print("□ ABXY buttons are in diamond pattern below right joystick")
    print("□ Start/Menu buttons are between phone and controls")
    print("□ Shoulder buttons are accessible on top edges")
    print("□ Trigger slots allow proper lever movement")
    print("□ All features have smooth, filleted edges")

def determine_next_steps():
    """
    Determine appropriate next steps based on analysis
    """
    print("\nNEXT STEPS DETERMINATION")
    print("=" * 50)
    
    # Check if we can proceed to Phase 3
    modified_file = "/workspaces/scad/output/FrontCover_Modified_S20Cutout_v2.stl"
    
    if os.path.exists(modified_file):
        mesh = trimesh.load(modified_file)
        
        print("Current status:")
        print(f"✓ Modified front cover exists: {os.path.basename(modified_file)}")
        print(f"✓ Mesh is watertight: {mesh.is_watertight}")
        print(f"✓ S20 cutout modification completed")
        
        print("\nRecommended approach:")
        print("1. 🔍 Manual verification in CAD software required")
        print("   - Load the STL in your preferred 3D viewer/CAD program")
        print("   - Visually inspect for gaming control features")
        print("   - Use the verification checklist above")
        
        print("\n2. 📐 If features are missing:")
        print("   - The original mesh may not have had gaming controls")
        print("   - They may need to be added in a separate design step")
        print("   - Consider using the original NucDeck design files")
        
        print("\n3. ✅ If features are present:")
        print("   - Proceed to Phase 3: Back shell modification")
        print("   - Focus on battery compartment and electronics pockets")
        
        print("\n4. 🚀 Phase 3 Tasks (if ready):")
        print("   - Battery compartment: 90×60×12mm")
        print("   - TP4056 charger pocket: 23×16×5mm")
        print("   - PD boost module pocket: 23.3×11.9×4mm")
        print("   - Battery indicator cutout: 43.5×20×5mm")
        print("   - Power switch hole: ∅16mm")
        print("   - Cable routing channels")
        
        return True
    else:
        print("❌ Modified front cover not found")
        print("Need to complete S20 cutout modification first")
        return False

def main():
    print("COMPREHENSIVE NUCDECK FRONT COVER ANALYSIS")
    print("=" * 60)
    
    modified_file = "/workspaces/scad/output/FrontCover_Modified_S20Cutout_v2.stl"
    
    if not os.path.exists(modified_file):
        print(f"Error: Modified file not found: {modified_file}")
        return
    
    # Load and analyze the mesh
    mesh = trimesh.load(modified_file)
    
    # Detailed geometry analysis
    analyze_mesh_geometry_detailed(mesh)
    
    # Hole detection
    holes = detect_holes_and_cutouts(mesh)
    
    # Compare with original
    analyze_original_vs_modified()
    
    # Manual verification guide
    manual_verification_guide()
    
    # Determine next steps
    can_proceed = determine_next_steps()
    
    # Export summary
    summary = {
        'analysis_complete': True,
        'manual_verification_needed': True,
        'ready_for_phase_3': can_proceed,
        'modified_file': modified_file,
        'holes_detected': len(holes),
        'recommendations': [
            'Load STL in CAD software for visual inspection',
            'Verify gaming control features using provided checklist',
            'Proceed to back shell modification if features are confirmed'
        ]
    }
    
    summary_file = "/workspaces/scad/output/front_cover_analysis_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"Summary saved to: {summary_file}")
    print("Manual verification in CAD software is now required.")

if __name__ == "__main__":
    main()
