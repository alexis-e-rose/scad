// NucDeck Handheld Gaming Console Assembly
// Auto-generated OpenSCAD script for 3D model assembly and customization
// Project: DIY Handheld Console based on NUC hardware

// Global parameters - modify these to customize the build
phone_width = 69.1;          // Samsung S20 width
phone_height = 151.7;        // Samsung S20 height  
phone_depth = 7.9;           // Samsung S20 depth
battery_width = 60;          // LiPo battery width
battery_length = 90;         // LiPo battery length
battery_height = 12;         // LiPo battery height
grip_offset = 20;            // How far grips extend from main body
show_phone_mockup = true;    // Show phone placeholder for fitment
show_battery_mockup = true;  // Show battery placeholder for fitment
show_assembly_screws = false; // Show screw holes for assembly
exploded_view = false;       // Exploded view for assembly instructions

// Component visibility toggles
show_housing_front = true;
show_housing_back = true;
show_left_grip = true;
show_right_grip = true;
show_joystick_rings = true;
show_trigger_mounts = true;
show_buttons = true;
show_lcd_retainer = true;

// STL file paths (relative to this script)
housing_front_path = "../Housing - STL/Housing Front.STL";
housing_front_no_rgb_path = "../Housing - STL/Housing Front - No RGB.STL";
housing_back_path = "../Housing - STL/Back Cover 7th Gen Intel NUC.STL";
left_grip_path = "../Housing - STL/Left Side Grip.STL";
right_grip_path = "../Housing - STL/Right Side Grip.STL";
joystick_ring_path = "../Housing - STL/Joystick Surround Ring.STL";
lcd_retainer_path = "../Housing - STL/LCD Retainer.STL";
trigger_left_path = "../Housing - STL/Trigger Mount Left.STL";
trigger_right_path = "../Housing - STL/Trigger Mount Right.STL";

// Button STL paths
power_button_path = "../Buttons - STL/Power Button.STL";
volume_up_path = "../Buttons - STL/+ Volume Button.STL";
volume_down_path = "../Buttons - STL/- Volume Button.STL";
trigger_button_left_path = "../Buttons - STL/Trigger Button Left.STL";
trigger_button_right_path = "../Buttons - STL/Trigger Button Right.STL";

// Main assembly module
module nucdeck_assembly() {
    // Housing components
    if (show_housing_front) {
        color("lightblue", 0.8) 
        translate([0, 0, exploded_view ? 10 : 0])
        import(housing_front_path);
    }
    
    if (show_housing_back) {
        color("darkblue", 0.8)
        translate([0, 0, exploded_view ? -10 : 0]) 
        import(housing_back_path);
    }
    
    // Side grips
    if (show_left_grip) {
        color("gray", 0.9)
        translate([exploded_view ? -grip_offset : 0, 0, 0])
        import(left_grip_path);
    }
    
    if (show_right_grip) {
        color("gray", 0.9)
        translate([exploded_view ? grip_offset : 0, 0, 0])
        import(right_grip_path);
    }
    
    // Joystick components
    if (show_joystick_rings) {
        color("black", 0.9) {
            translate([-30, 20, exploded_view ? 5 : 0])
            import(joystick_ring_path);
            
            translate([30, 20, exploded_view ? 5 : 0])
            import(joystick_ring_path);
        }
    }
    
    // Trigger mounts
    if (show_trigger_mounts) {
        color("red", 0.7) {
            translate([exploded_view ? -20 : 0, 0, exploded_view ? 15 : 0])
            import(trigger_left_path);
            
            translate([exploded_view ? 20 : 0, 0, exploded_view ? 15 : 0])
            import(trigger_right_path);
        }
    }
    
    // LCD retainer
    if (show_lcd_retainer) {
        color("green", 0.8)
        translate([0, 0, exploded_view ? 8 : 0])
        import(lcd_retainer_path);
    }
    
    // Buttons
    if (show_buttons) {
        color("yellow", 0.9) {
            // Power button
            translate([40, -10, exploded_view ? 5 : 0])
            import(power_button_path);
            
            // Volume buttons
            translate([45, 10, exploded_view ? 5 : 0])
            import(volume_up_path);
            
            translate([45, 0, exploded_view ? 5 : 0])
            import(volume_down_path);
            
            // Trigger buttons
            translate([-45, -30, exploded_view ? 15 : 0])
            import(trigger_button_left_path);
            
            translate([45, -30, exploded_view ? 15 : 0])
            import(trigger_button_right_path);
        }
    }
    
    // Mockup components for fitment testing
    if (show_phone_mockup) {
        color("black", 0.3)
        translate([0, 10, 5])
        cube([phone_width, phone_height, phone_depth], center=true);
    }
    
    if (show_battery_mockup) {
        color("red", 0.3)
        translate([0, -30, -5])
        cube([battery_width, battery_length, battery_height], center=true);
    }
}

// Customization modules for AI-driven modifications
module custom_button_cutout(x, y, z, diameter=10, depth=5) {
    translate([x, y, z])
    cylinder(h=depth, d=diameter, center=true);
}

module custom_mounting_hole(x, y, z, diameter=3, depth=10) {
    translate([x, y, z])
    cylinder(h=depth, d=diameter, center=true);
}

module custom_ventilation_grille(x, y, z, width=20, height=5, spacing=2) {
    translate([x, y, z])
    for (i = [0:spacing:width]) {
        translate([i, 0, 0])
        cube([1, height, 5], center=true);
    }
}

// Assembly with customizations
module customized_assembly() {
    difference() {
        nucdeck_assembly();
        
        // Add custom cutouts here (these will be controlled by AI)
        // Example: custom_button_cutout(20, 30, 0, 8, 3);
        // Example: custom_mounting_hole(-10, -10, -2, 3, 8);
    }
}

// Render the assembly
customized_assembly();

// Alternative views (uncomment as needed)
// translate([0, 0, 100]) nucdeck_assembly(); // Side-by-side comparison
