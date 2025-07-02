# NucDeck AI-Powered CAD Development

## Project Overview

This project merges **ScadLM** (open source agentic AI CAD generation) with **NucDeck** to create an AI-powered handheld gaming device design system built on OpenSCAD. 

**Source repositories:**
- [ScadLM](https://github.com/KrishKrosh/ScadLM) - AI-driven CAD automation
- [NucDeck](https://github.com/dmcke5/NucDeck.git) - Handheld gaming device hardware

## 🚀 Quick Start Guide

### Prerequisites
- **OpenSCAD** (version 2021.01 or later)
- **Python 3.8+** with pip
- **Git** (for version control)
- **Web browser** (for STL viewing)
- **Optional**: OpenAI API key for AI features

### 1. Initial Setup

```bash
# Clone and enter the project directory
cd /workspaces/scad

# Run the automated setup
make setup

# Or manual setup:
chmod +x setup.sh
./setup.sh
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Import and Organize Files

The project already includes organized STL and STEP files:
- `Housing - STL/` - Housing components ready for import
- `Buttons - STL/` - Button components (clicky/membrane variants)
- `Housing - STEP/` - STEP files for parametric editing
- `Buttons - STEP/` - Button STEP files

**Generate model catalog:**
```bash
make catalog
```
This scans all files and creates `OpenSCAD/model_imports.scad` with import statements.

### 3. Configuration & Customization

Edit `config.yaml` to customize your build:

```yaml
# Basic dimensions (in mm)
dimensions:
  case_length: 300      # Overall length
  case_width: 120       # Overall width  
  case_height: 40       # Overall height
  screen_width: 170     # Screen cutout width
  screen_height: 100    # Screen cutout height

# Component positions (relative to center)
layout:
  left_joystick:
    x: -80              # 80mm left of center
    y: -30              # 30mm forward
  right_joystick:
    x: 80               # 80mm right of center
    y: -30              # 30mm forward
  
# Material properties
materials:
  case_thickness: 3     # Wall thickness
  tolerance: 0.2        # Fit tolerance
```

**Key customization areas:**
- **Dimensions**: Adjust case size for different devices
- **Layout**: Reposition components (joysticks, buttons, screen)
- **Materials**: Change wall thickness, tolerances
- **3D Printing**: Layer height, infill, support settings

### 4. Build Instructions

#### Option A: Interactive Assistant (Recommended)
```bash
make interactive
```

Interactive commands:
```
CAD> modify make case 5mm taller
CAD> render high
CAD> config dimensions.case_width 130
CAD> export stl
CAD> models                    # List available components
CAD> status                    # Show project status
```

#### Option B: Direct Commands
```bash
# Quick render and preview
make render

# High quality render
make render-high

# Export STL for 3D printing
make export

# Export all formats (STL, 3MF)
make export-all

# View in web browser
make web                       # Opens http://localhost:8000
```

#### Option C: Python Automation
```python
from cad_automator import CADAutomator

automator = CADAutomator()
automator.apply_modifications([
    "Make the case 10% larger",
    "Move screen cutout 5mm right",
    "Add ventilation slots"
])
automator.render_design()
automator.export_stl()
```

### 5. AI-Powered Features (Optional)

Set up OpenAI for natural language modifications:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Then use natural language commands:
```
CAD> make the grip area more ergonomic
CAD> add mounting holes for the PCB
CAD> optimize for 3D printing
```

### 6. File Organization

```
📁 Your Generated Files:
├── output/
│   ├── stl/                   # 3D printable files
│   ├── images/                # Render previews
│   └── modified/              # Customized versions
├── temp/                      # Temporary files
└── current_project.json       # Your current settings
```

### 7. 3D Printing Workflow

1. **Generate STL**: `make export` or `CAD> export stl`
2. **Check output**: Files saved to `output/stl/`
3. **Import to slicer**: Use Cura, PrusaSlicer, etc.
4. **Recommended settings**:
   - Layer height: 0.2mm
   - Infill: 20%
   - Supports: Yes (for overhangs)
   - Brim: Yes (for bed adhesion)

### 8. Advanced Customization

#### Adding Custom Components
```bash
# Add your STL files to appropriate directories:
cp my_custom_button.stl "Buttons - STL/"
cp my_custom_housing.stl "Housing - STL/"

# Regenerate catalog
make catalog
```

#### Creating Variants
```python
# Create multiple sizes
from cad_automator import CADAutomator
automator = CADAutomator()

for size in ['compact', 'standard', 'large']:
    automator.create_variant(size)
    automator.export_stl(f"nucdeck_{size}")
```

#### Batch Processing
```bash
# Process multiple modifications
python3 -c "
from cad_automator import CADAutomator
automator = CADAutomator()
modifications = [
    'Version A: Standard size',
    'Version B: 10% larger for bigger hands',
    'Version C: Compact for portability'
]
for mod in modifications:
    automator.apply_modifications([mod])
    automator.export_stl()
"
```

### 9. Troubleshooting

**Common Issues:**

- **OpenSCAD not found**: `sudo apt install openscad` (Ubuntu) or download from openscad.org
- **Python errors**: Activate virtual environment with `source venv/bin/activate`
- **Web viewer not loading**: Try different port with `python3 -m http.server 8001 --directory web_viewer`
- **Render failures**: Check OpenSCAD syntax with `make validate`

**Debug Commands:**
```bash
make info          # Show system information
make validate      # Check OpenSCAD files
make clean         # Clear output files
```

### 10. Next Steps

1. **Explore existing models**: `make interactive` → `models`
2. **Create your first modification**: Try "modify make case 5mm taller"
3. **Render and preview**: Use `render` and `make web`
4. **Export for printing**: `export stl` when ready
5. **Iterate and improve**: Use AI suggestions and parameter tweaks

---

## Original Project Description

A clone of Nucdeck
## Project Inventory & Preliminary Case Layout

### 1. Core Electronics (with Dimensions)

| Part                                            | Qty   | Dimensions (L×W×H mm)                         | Notes                                   |      |     |                       |       |
| ----------------------------------------------- | ----- | --------------------------------------------- | --------------------------------------- | ---- | --- | --------------------- | ----- |
| **LiPo Battery (YELUFT 3.7 V, 8000 mAh)**       | 1     | 90 × 60 × 12                                  | PH2.0 pigtail, 120 mm wire leads        |      |     |                       |       |
| **TP4056 Charger Board**                        | 1     | 23 × 16 × 5                                   | USB‑C input + BMS LEDs, 1 A charge      |      |     |                       |       |
| **Youmile PD Trigger/Boost Module**             | 1     | 23.3 × 11.9 × 4                               | Fixed 5 V output for PD pass-through    |      |     |                       |       |
| **DAOKAI Battery Indicator**                    | 1     | 43.5 × 20 × 5                                 | 4‑bar LED display, 2‑wire hookup        |      |     |                       |       |
| **Bestgle 16 mm Latching LED Switch**           | 1     | Bezel Ø 16, body Ø 14 × 12 deep, back 35 deep | Prewired 5‑pin plug, built‑in LED       |      |     |                       |       |
| **MOSWAG USB‑C OTG + PD Splitter**              | 1     | \~40 × 14 × 10 (est.)                         | USB‑C female + USB‑A OTG, braided cable |      |     |                       |       |
| **JST‑XH Connector Kit (2/3/4/5/6 pin)**        | 1 kit | ---                                           | Pre‑crimped 22 AWG pigtails, housings   |      |     |                       |       |
| **Xbox Series X/S Controller Joystick Modules** | 2     | ≈32 × 32 × 18 (each)                          | Salvaged analog sticks & D‑pad          | Part | Qty | Dimensions (L×W×H mm) | Notes |
| -----------------------------------------       | ----- | --------------------------------------------- | --------------------------------------- |      |     |                       |       |
| **LiPo Battery (YELUFT 3.7 V, 8000 mAh)**       | 1     | 90 × 60 × 12                                  | PH2.0 pigtail, 120 mm wire leads        |      |     |                       |       |
| **TP4056 Charger Board**                        | 1     | 23 × 16 × 5                                   | USB‑C input + BMS LEDs, 1 A charge      |      |     |                       |       |
| **Youmile PD Trigger/Boost Module**             | 1     | 23.3 × 11.9 × 4                               | Fixed 5 V output for PD pass-through    |      |     |                       |       |
| **DAOKAI Battery Indicator**                    | 1     | 43.5 × 20 × 5                                 | 4‑bar LED display, 2‑wire hookup        |      |     |                       |       |
| **Bestgle 16 mm Latching LED Switch**           | 1     | Bezel Ø 16, body Ø 14 × 12 deep, back 35 deep | Prewired 5‑pin plug, built‑in LED       |      |     |                       |       |
| **MOSWAG USB‑C OTG + PD Splitter**              | 1     | \~40 × 14 × 10 (est.)                         | USB‑C female + USB‑A OTG, braided cable |      |     |                       |       |
| **JST‑XH Connector Kit (2/3/4/5/6 pin)**        | 1 kit | ---                                           | Pre‑crimped 22 AWG pigtails, housings   |      |     |                       |       |

* **Samsung Galaxy S20** handset & magnetic USB‑C inserts

  * Device dimensions (HxWxD): 151.7 × 69.1 × 7.9 mm
  * Screen: 6.2" (158.3 mm) diagonal, 3200 × 1440 px @ 563 ppi
  * Weight: 163 g (5.75 oz)
* Xbox Wireless Controller (for joystick salvage)

---

## Preliminary Case Layout (Samsung S20 + Xbox PCB Integrated Handheld Enclosure)

1. **Phone Mounting Pocket**

   * Central cavity sized to S20: **152 × 70 × 9 mm** internal clearance
   * Secure with snap-fit clips or TPU bumpers along the long edges
   * Front lip recess to expose screen; rear access for magnetic USB‑C insert

2. **Xbox Controller PCB Integration**

   * Allocate a dedicated PCB bay behind the battery pocket on the lower half
   * Bay dimensions: **80 × 60 × 12 mm** (allow for PCB and wiring)
   * Mount standoffs at four PCB corner mounting holes; use M2 screws to secure PCB
   * Provide 1 mm clearance around the PCB edge for connectors and wiring harness

3. **Joystick & Button Cutouts**

   * **Left Joystick**: 32 mm diameter hole at front-left grip
   * **Right Joystick**: 32 mm diameter hole at front-right grip
   * **D-pad**: 24 × 24 mm square cutout below left joystick; round corners radius 4 mm
   * **ABXY Buttons**: Four 12 mm diameter holes in diamond arrangement below right joystick
   * **Start & Menu Buttons**: Two 8 mm holes centered between phone pocket and joysticks

4. **Shoulder Buttons & Triggers**

   * **L1 / R1**: 11 mm × 4 mm rectangular cutouts on top-left and top-right edges
   * **L2 / R2 Triggers**: 18 × 8 mm angled slots behind L1/R1 for lever travel
   * Use internal guide rails printed in place to hold trigger modules and springs

5. **Power & Indicator Sections**

   * **Battery Pocket**: 95 × 65 × 15 mm under phone; secure with bracket
   * **TP4056 & PD Boost**: Under battery; standoffs at 23 × 16 mm (left) and 23.3 × 11.9 mm (right) footprints
   * **Latching Switch**: top-right rear panel; 16 mm hole, 35 mm clearance
   * **Battery Indicator**: bottom-center rear; slot 45 × 22 × 8 mm

6. **USB-C OTG + PD Splitter Exit**

   * Cutout 14 × 12 mm on bottom-center bezel; braided cable channel behind

7. **Cable Management**

   * 2 mm-wide, 3 mm-deep wire troughs along interior walls; follow component edge paths

8. **Ventilation & Cooling**

   * Vent slots above PD module, switch, and PCB bay: two 20 × 2 mm perforations each
   * Ensure airflow from top vents to rear panel openings

---

*Confirm placements or request further tweaks before STL modification!*
