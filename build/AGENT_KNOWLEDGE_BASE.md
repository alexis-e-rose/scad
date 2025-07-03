# AI Agent Knowledge Base - Handheld Gaming Device Project

## Quick Project Context
This is a Samsung Galaxy S20-based handheld gaming console build using Xbox Series X/S controller components, custom electronics, and 3D-printed enclosure.

## Component Database

### Electronics Specifications
```json
{
  "phone": {
    "model": "Samsung Galaxy S20",
    "dimensions": {"length": 151.7, "width": 69.1, "depth": 7.9, "unit": "mm"},
    "screen": {"diagonal": 6.2, "unit": "inches"},
    "pocket_clearance": {"x": 3, "y": 3, "z": 5, "unit": "mm"}
  },
  "battery": {
    "model": "MakerFocus 8000mAh Li-ion",
    "dimensions": {"length": 90, "width": 60, "depth": 12, "unit": "mm"},
    "capacity": {"value": 8000, "unit": "mAh"},
    "clearance_required": {"all_sides": 4, "unit": "mm"}
  },
  "charging_board": {
    "model": "TP4056",
    "dimensions": {"length": 23, "width": 16, "depth": 5, "unit": "mm"},
    "function": "Li-ion battery charging controller",
    "connections": ["BAT+", "BAT-", "OUT+", "OUT-", "USB_IN"]
  },
  "pd_trigger": {
    "dimensions": {"length": 23.3, "width": 11.9, "depth": 4, "unit": "mm"},
    "function": "Power delivery controller",
    "connections": ["IN+", "IN-", "OUT+", "OUT-"]
  },
  "battery_indicator": {
    "dimensions": {"length": 43.5, "width": 20, "depth": 2, "unit": "mm"},
    "function": "Visual battery level display",
    "mounting": "Visible location on case exterior"
  },
  "power_switch": {
    "bezel_diameter": {"value": 16, "unit": "mm"},
    "depth": {"value": 12, "unit": "mm"},
    "total_length": {"value": 35, "unit": "mm"},
    "cutout_required": {"diameter": 16, "unit": "mm"}
  },
  "usb_splitter": {
    "type": "USB-C OTG flex cable",
    "thickness": {"value": 3, "unit": "mm"},
    "function": "Route power and data to phone"
  }
}
```

### Xbox Controller Components
```json
{
  "joysticks": {
    "active_diameter": {"value": 32, "unit": "mm"},
    "overall_dimensions": {"x": 32, "y": 32, "z": 18, "unit": "mm"},
    "cutout_diameter": {"value": 32, "unit": "mm"},
    "recess_depth": {"value": 8, "unit": "mm"}
  },
  "dpad": {
    "type": "Integrated unit from Xbox Series X/S",
    "approx_size": {"value": 24, "unit": "mm"},
    "corner_radius": {"value": 4, "unit": "mm"}
  },
  "abxy_buttons": {
    "diameter": {"value": 12, "unit": "mm"},
    "spacing": {"value": 20, "unit": "mm"},
    "layout": "Diamond pattern"
  },
  "shoulder_buttons": {
    "l1_r1": {"width": 11, "height": 4, "unit": "mm"},
    "l2_r2": {"width": 18, "height": 8, "unit": "mm"}
  }
}
```

## Critical Design Parameters

### Case Dimensions
```python
# From parametric_handheld_case.py
CASE_PARAMETERS = {
    'overall_width': 294.0,      # Total case width
    'overall_height': 115.0,     # Total case height  
    'total_depth': 19.0,         # Combined front + back depth
    'front_depth': 10.0,         # Front shell depth
    'back_depth': 9.0,           # Back shell depth
    'wall_thickness': 2.5,       # Minimum wall thickness
    'grip_width': 71.5,          # Width of each grip section
    'grip_height': 95.0,         # Height of grip sections
}
```

### Phone Pocket Specifications
```python
PHONE_POCKET = {
    'target_width': 151.7 + 6,   # Phone width + 2*3mm clearance
    'target_height': 69.1 + 6,   # Phone height + 2*3mm clearance  
    'target_depth': 7.9 + 5,     # Phone depth + 5mm clearance
    'wall_height': 7.9 + 5 + 3,  # Phone + clearance + wall thickness
}
```

## Build Phase Quick Reference

### Phase 1: Component Salvage (Xbox Controller)
**Duration**: 2-3 hours  
**Key Tools**: Phillips #0, spudger, ESD mat, multimeter  
**Critical Step**: Follow video guide exactly - https://youtu.be/1VLbJQIDlQU  
**Success Criteria**: All components extracted, tested, and labeled

### Phase 2: Electronics Assembly
**Duration**: 3-4 hours  
**Key Tools**: Soldering iron, multimeter, flux  
**Critical Step**: Verify polarity on ALL connections before power-on  
**Success Criteria**: <20mA idle draw, charging works, indicator functions

### Phase 3: Mechanical Fitting
**Duration**: 2-3 hours  
**Key Tools**: Calipers, cardboard, Ø32mm washers  
**Critical Step**: Physical verification before final print  
**Success Criteria**: All components fit with proper clearances

### Phase 4: Final Assembly
**Duration**: 4-6 hours  
**Key Tools**: 3D printer, M3 screws, foam tape  
**Critical Step**: Print settings must be exact (0.2mm layers, 20% infill)  
**Success Criteria**: Complete functional handheld

## Common Agent Questions & Answers

### Q: What are the exact phone pocket dimensions?
A: 157.7mm × 75.1mm × 15.9mm (phone + clearances + wall thickness)

### Q: How much clearance is needed around the battery?
A: 4mm minimum on all sides to prevent contact with phone pocket

### Q: What's the joystick cutout diameter?
A: 32mm diameter, matching Xbox Series X/S joystick active area

### Q: What print settings should be used?
A: 0.2mm layers, 20% infill, 3-4 wall lines, supports only for >45° overhangs

### Q: How is the power system wired?
A: Battery → TP4056 → PD-trigger → USB-C splitter, with switch inline on positive rail

### Q: What's the expected idle power draw?
A: <20mA maximum; higher indicates wiring issue or component problem

### Q: How are components mounted in the case?
A: Foam tape for electronics, snap-fit for controls, M3 screws for shell assembly

## File Structure Reference

```
/workspaces/scad/
├── parametric_handheld_case.py     # Main case generation code
├── current_project.json            # Project configuration
├── HANDHELD_BUILD_GUIDE.md        # Complete user guide
├── AGENT_KNOWLEDGE_BASE.md         # This file
├── Housing - STL/                  # Reference STL files
├── Housing - STEP/                 # Reference STEP files
├── Buttons - STL/                  # Controller component STLs
└── output/                         # Generated files
```

## Parametric Code Key Functions

### Main Classes & Methods
- `ParametricHandheldCase.__init__()` - Sets all design parameters
- `create_base_shell(is_front=True)` - Generates shell structure
- `create_ergonomic_grip()` - Creates grip areas
- `add_phone_pocket()` - Creates phone cutout
- `add_electronics_cutouts()` - Battery/PCB mounting areas
- `add_control_cutouts()` - Joystick/button openings

### Critical Parameters to Monitor
- `phone_cutout_width/height` - Must accommodate phone + clearance
- `battery_*` dimensions - Must match actual battery
- `joystick_diameter` - Must match Xbox controller parts
- `wall_thickness` - Affects structural integrity
- `*_tolerance` values - Control fit and clearances

## Error Prevention

### Common Mistakes
1. **Wrong polarity on battery connections** - Always double-check
2. **Insufficient clearances** - Verify measurements before printing
3. **Incorrect print settings** - Use exact specifications provided
4. **Missing strain relief** - Secure all wiring properly
5. **Over-tightening screws** - Can crack printed parts

### Validation Steps
1. Measure twice, cut/print once
2. Test electronics before final assembly
3. Verify component fit before closing case
4. Check power draw after each connection
5. Thermal test under load before daily use

## Integration Notes

This knowledge base should be referenced alongside:
- The main build guide (`HANDHELD_BUILD_GUIDE.md`)
- The parametric code (`parametric_handheld_case.py`)
- Component datasheets and Xbox teardown video
- 3D printing community best practices

Updates to component specifications or build process should be reflected in both this file and the main build guide to maintain consistency.
