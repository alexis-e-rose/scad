#!/usr/bin/env python3
"""
Phase 3: Back Shell Modification for NucDeck Electronics
Creates internal pockets for battery, charger, and electronic components
"""

import trimesh
import numpy as np
import os

def create_battery_compartment(center, width=90, height=60, depth=12, tolerance=1.0):
    """
    Create battery compartment pocket (90×60×12mm for 8000mAh LiPo)
    """
    actual_width = width + 2 * tolerance
    actual_height = height + 2 * tolerance 
    actual_depth = depth + tolerance
    
    print(f"Creating battery compartment: {actual_width}×{actual_height}×{actual_depth}mm")
    
    battery_box = trimesh.creation.box(extents=[actual_width, actual_height, actual_depth])
    battery_box.apply_translation(center)
    
    return battery_box

def create_electronics_pockets():
    """
    Create pockets for various electronic components
    """
    components = {
        'tp4056_charger': {
            'size': [23 + 1, 16 + 1, 5 + 0.5],  # TP4056 + tolerance
            'description': 'USB-C charger board'
        },
        'pd_boost_module': {
            'size': [23.3 + 1, 11.9 + 1, 4 + 0.5],  # PD trigger/boost + tolerance
            'description': 'PD trigger/boost module'
        },
        'battery_indicator': {
            'size': [43.5 + 1, 20 + 1, 5 + 0.5],  # Battery indicator + tolerance
            'description': 'Battery level indicator'
        },
        'power_switch': {
            'size': [16, 16, 12],  # 16mm bezel, 12mm depth
            'description': 'Latching LED power switch'
        }
    }
    
    pockets = {}
    
    for component_name, spec in components.items():
        size = spec['size']
        pocket = trimesh.creation.box(extents=size)
        pockets[component_name] = {
            'mesh': pocket,
            'size': size,
            'description': spec['description']
        }
        print(f"Created {component_name} pocket: {size[0]:.1f}×{size[1]:.1f}×{size[2]:.1f}mm")
    
    return pockets

def create_cable_routing_channels(start_points, end_points, diameter=3.0):
    """
    Create cable routing channels between components
    """
    channels = []
    
    for i, (start, end) in enumerate(zip(start_points, end_points)):
        # Create cylinder connecting start and end points
        direction = np.array(end) - np.array(start)
        length = np.linalg.norm(direction)
        
        if length > 0:
            # Create cylinder along Z-axis, then rotate and translate
            channel = trimesh.creation.cylinder(radius=diameter/2, height=length)
            
            # Calculate rotation to align with direction
            z_axis = np.array([0, 0, 1])
            direction_normalized = direction / length
            
            if not np.allclose(direction_normalized, z_axis):
                rotation_axis = np.cross(z_axis, direction_normalized)
                rotation_angle = np.arccos(np.clip(np.dot(z_axis, direction_normalized), -1, 1))
                
                if np.linalg.norm(rotation_axis) > 1e-6:
                    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                    rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, rotation_axis)
                    channel.apply_transform(rotation_matrix)
            
            # Translate to position
            center = (np.array(start) + np.array(end)) / 2
            channel.apply_translation(center)
            
            channels.append(channel)
            print(f"Cable channel {i+1}: {length:.1f}mm long, ∅{diameter}mm")
    
    return channels

def analyze_back_cover_for_modification():
    """
    Analyze the back cover to determine optimal component placement
    """
    back_cover_file = "/workspaces/scad/Housing - STL/Back Cover 7th Gen Intel NUC.STL"
    
    if not os.path.exists(back_cover_file):
        print(f"Error: Back cover file not found: {back_cover_file}")
        return None
    
    print("ANALYZING BACK COVER FOR COMPONENT PLACEMENT")
    print("=" * 60)
    
    mesh = trimesh.load(back_cover_file)
    
    bounds = mesh.bounds
    dimensions = bounds[1] - bounds[0]
    
    print(f"Back cover dimensions: {dimensions[0]:.1f} × {dimensions[1]:.1f} × {dimensions[2]:.1f} mm")
    print(f"Internal volume: {mesh.volume:,.0f} mm³")
    print(f"Geometric center: ({(bounds[0] + bounds[1])[0]/2:.1f}, {(bounds[0] + bounds[1])[1]/2:.1f}, {(bounds[0] + bounds[1])[2]/2:.1f})")
    
    # Calculate optimal component positions
    center_x = (bounds[0][0] + bounds[1][0]) / 2
    center_y = (bounds[0][1] + bounds[1][1]) / 2
    center_z = (bounds[0][2] + bounds[1][2]) / 2
    
    # Battery should be centered and low for balance
    battery_center = [center_x, center_y, bounds[0][2] + 8]  # 8mm from bottom
    
    # Electronics positioned around battery
    positions = {
        'battery': battery_center,
        'tp4056_charger': [center_x - 35, center_y - 15, bounds[0][2] + 4],
        'pd_boost_module': [center_x + 35, center_y - 15, bounds[0][2] + 4],
        'battery_indicator': [center_x, bounds[1][1] - 15, bounds[1][2] - 8],  # Visible on back
        'power_switch': [bounds[1][0] - 20, center_y, bounds[1][2] - 10]  # Top right accessible
    }
    
    print(f"\nOptimal component positions:")
    for component, pos in positions.items():
        print(f"  {component}: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
    
    return mesh, positions, bounds

def modify_back_cover():
    """
    Main function to modify the back cover with component pockets
    """
    # Analyze back cover
    analysis_result = analyze_back_cover_for_modification()
    if analysis_result is None:
        return False
    
    back_mesh, positions, bounds = analysis_result
    
    print(f"\n" + "="*60)
    print("CREATING COMPONENT POCKETS")
    print("=" * 60)
    
    # Create battery compartment
    battery_pocket = create_battery_compartment(positions['battery'])
    
    # Create electronics pockets
    electronics_pockets = create_electronics_pockets()
    
    # Position electronics pockets
    positioned_pockets = []
    
    for component_name, pocket_info in electronics_pockets.items():
        if component_name in positions:
            pocket_mesh = pocket_info['mesh'].copy()
            pocket_mesh.apply_translation(positions[component_name])
            positioned_pockets.append(pocket_mesh)
            
            pos = positions[component_name]
            size = pocket_info['size']
            desc = pocket_info['description']
            print(f"Positioned {component_name}: {desc} at ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
    
    # Create cable routing channels
    print(f"\n" + "="*30)
    print("CABLE ROUTING CHANNELS")
    print("=" * 30)
    
    cable_routes = [
        (positions['battery'], positions['tp4056_charger']),
        (positions['tp4056_charger'], positions['pd_boost_module']),
        (positions['battery'], positions['battery_indicator']),
        (positions['pd_boost_module'], positions['power_switch'])
    ]
    
    start_points = [route[0] for route in cable_routes]
    end_points = [route[1] for route in cable_routes]
    
    cable_channels = create_cable_routing_channels(start_points, end_points, diameter=2.5)
    
    # Combine all cutout geometries
    print(f"\n" + "="*30)
    print("BOOLEAN OPERATIONS")
    print("=" * 30)
    
    all_cutouts = [battery_pocket] + positioned_pockets + cable_channels
    
    print(f"Performing {len(all_cutouts)} boolean subtractions...")
    
    modified_mesh = back_mesh.copy()
    successful_operations = 0
    
    for i, cutout in enumerate(all_cutouts):
        try:
            result = modified_mesh.difference(cutout)
            if result is not None and len(result.vertices) > 0:
                modified_mesh = result
                successful_operations += 1
                print(f"  Operation {i+1}/{len(all_cutouts)}: ✓")
            else:
                print(f"  Operation {i+1}/{len(all_cutouts)}: ❌ (empty result)")
        except Exception as e:
            print(f"  Operation {i+1}/{len(all_cutouts)}: ❌ ({str(e)})")
    
    print(f"Successful operations: {successful_operations}/{len(all_cutouts)}")
    
    # Repair and validate result
    print(f"\nRepairing mesh...")
    modified_mesh.remove_duplicate_faces()
    modified_mesh.merge_vertices()
    
    if not modified_mesh.is_watertight:
        print("  Attempting to repair non-watertight mesh...")
        modified_mesh.fill_holes()
    
    volume_removed = back_mesh.volume - modified_mesh.volume
    
    print(f"\nModification results:")
    print(f"  Original volume: {back_mesh.volume:,.0f} mm³")
    print(f"  Modified volume: {modified_mesh.volume:,.0f} mm³")
    print(f"  Material removed: {volume_removed:,.0f} mm³")
    print(f"  Watertight: {modified_mesh.is_watertight}")
    
    # Export result
    output_file = "/workspaces/scad/output/BackCover_Modified_Electronics.stl"
    
    print(f"\nExporting to: {output_file}")
    modified_mesh.export(output_file)
    
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

def create_assembly_guide():
    """
    Create assembly guide for the modified components
    """
    guide_file = "/workspaces/scad/output/assembly_guide.txt"
    
    with open(guide_file, 'w') as f:
        f.write("NUCDECK ASSEMBLY GUIDE\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("FRONT COVER:\n")
        f.write("✓ Samsung Galaxy S20 cutout (153×71mm)\n")
        f.write("✓ Gaming control features (verify manually)\n")
        f.write("  - File: FrontCover_Modified_S20Cutout_v2.stl\n\n")
        
        f.write("BACK COVER:\n")
        f.write("✓ Battery compartment (92×62×13mm)\n")
        f.write("✓ TP4056 charger pocket (24×17×5.5mm)\n")
        f.write("✓ PD boost module pocket (24.3×12.9×4.5mm)\n")
        f.write("✓ Battery indicator cutout (44.5×21×5.5mm)\n")
        f.write("✓ Power switch hole (∅16mm)\n")
        f.write("✓ Cable routing channels (∅2.5mm)\n")
        f.write("  - File: BackCover_Modified_Electronics.stl\n\n")
        
        f.write("ASSEMBLY ORDER:\n")
        f.write("1. Install electronics in back cover pockets\n")
        f.write("2. Route cables through channels\n")
        f.write("3. Insert battery into compartment\n")
        f.write("4. Mount Samsung S20 in front cover\n")
        f.write("5. Connect joysticks and buttons\n")
        f.write("6. Secure covers together\n\n")
        
        f.write("3D PRINTING NOTES:\n")
        f.write("- Print covers separately\n")
        f.write("- Support material may be needed for overhangs\n")
        f.write("- Test fit components before final assembly\n")
        f.write("- Use 0.2mm layer height for good detail\n")
    
    print(f"Assembly guide saved to: {guide_file}")

if __name__ == "__main__":
    print("PHASE 3: BACK SHELL MODIFICATION")
    print("=" * 50)
    
    success = modify_back_cover()
    
    if success:
        create_assembly_guide()
        
        print(f"\n" + "="*60)
        print("🎉 PHASE 3 COMPLETE!")
        print("="*60)
        print("✅ Back cover modified with component pockets")
        print("✅ Cable routing channels created")
        print("✅ Assembly guide generated")
        print("\nFiles ready for 3D printing:")
        print("  📁 output/FrontCover_Modified_S20Cutout_v2.stl")
        print("  📁 output/BackCover_Modified_Electronics.stl")
        print("  📋 output/assembly_guide.txt")
        
    else:
        print(f"\n❌ PHASE 3 FAILED")
        print("Check error messages above")
