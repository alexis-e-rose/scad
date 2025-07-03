// Simple NucDeck Demo Assembly
// Simplified version that works reliably for web demonstration

// Parameters
phone_width = 69.1;
phone_height = 151.7;
phone_depth = 7.9;
case_thickness = 3;
grip_width = 40;
case_height = 15;

// Main assembly
module demo_nucdeck() {
    // Main case body
    difference() {
        // Outer case
        hull() {
            translate([-phone_width/2 - grip_width, -phone_height/2, 0])
                cube([phone_width + 2*grip_width, phone_height, case_height]);
        }
        
        // Phone cutout
        translate([-phone_width/2, -phone_height/2, case_thickness])
            cube([phone_width, phone_height, phone_depth + 1]);
        
        // Left joystick hole
        translate([-phone_width/2 - grip_width/2, phone_height/4, -1])
            cylinder(d=20, h=case_height + 2);
        
        // Right joystick hole
        translate([phone_width/2 + grip_width/2, phone_height/4, -1])
            cylinder(d=20, h=case_height + 2);
        
        // D-pad area
        translate([-phone_width/2 - grip_width/2, -phone_height/4, -1])
            cube([15, 15, case_height + 2], center=true);
        
        // ABXY buttons
        for(i = [0:3]) {
            angle = i * 90;
            translate([phone_width/2 + grip_width/2 + 10*cos(angle), -phone_height/4 + 10*sin(angle), -1])
                cylinder(d=8, h=case_height + 2);
        }
    }
    
    // Phone mockup (optional)
    if ($preview) {
        color("black", 0.3)
        translate([-phone_width/2, -phone_height/2, case_thickness])
            cube([phone_width, phone_height, phone_depth]);
    }
    
    // Joystick mockups
    color("red", 0.7) {
        translate([-phone_width/2 - grip_width/2, phone_height/4, case_height])
            cylinder(d=18, h=10);
        translate([phone_width/2 + grip_width/2, phone_height/4, case_height])
            cylinder(d=18, h=10);
    }
}

// Render the demo
demo_nucdeck();
