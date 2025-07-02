# NucDeck CAD Automation - Quick Start Guide

## Overview

This system provides an agentic AI-powered CAD workflow for the NucDeck handheld gaming device project. It combines OpenSCAD scripting, visual editing, and AI assistance to streamline the design process.

## Installation

1. **Clone the repository** (if not already done)
2. **Run setup**:
   ```bash
   make setup
   ```
   Or manually:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   source venv/bin/activate
   ```

3. **Install OpenSCAD** (if not already installed):
   - Ubuntu/Debian: `sudo apt-get install openscad`
   - macOS: `brew install openscad`
   - Windows: Download from https://openscad.org/downloads.html

4. **Set up AI (optional)**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Quick Start

### 1. Generate Model Catalog
```bash
make catalog
```
This scans all STL/STEP files and creates import statements for OpenSCAD.

### 2. Start Interactive Assistant
```bash
make interactive
```
This launches an interactive session where you can:
- Modify designs with natural language
- Render previews
- Export files
- Browse available models

### 3. Render Current Design
```bash
make render
```
Creates a PNG preview of the current design.

### 4. View in Browser
```bash
make web
```
Opens a web-based STL viewer at http://localhost:8000

## Usage Examples

### Interactive Commands

Once in the interactive assistant (`make interactive`):

```
CAD> modify make the case 5mm taller
CAD> render high
CAD> config dimensions.case_width 130
CAD> export stl
CAD> status
CAD> models
```

### Direct Commands

```bash
# Quick render and export
make quick-export

# High quality render
make render-high

# Export all formats
make export-all

# Clean output files
make clean

# Validate OpenSCAD syntax
make validate
```

### AI-Powered Modifications

With OpenAI API key set:

```python
# In Python or interactive mode
from cad_automator import CADAutomator

automator = CADAutomator()
automator.apply_modifications([
    "Make the case 10% larger",
    "Move the screen cutout 5mm to the right",
    "Add mounting holes for the PCB"
])
```

## File Structure

```
/workspaces/scad/
├── OpenSCAD/
│   ├── nucdeck_assembly.scad    # Main assembly file
│   └── model_imports.scad       # Auto-generated imports
├── web_viewer/
│   ├── index.html              # Web STL viewer
│   └── js/                     # Three.js components
├── output/                     # Generated files
├── config.yaml                 # Project configuration
├── cad_automator.py           # Main automation script
├── cad_assistant.py           # Interactive assistant
├── model_library.py           # Model management
└── Makefile                   # Build commands
```

## Configuration

Edit `config.yaml` to customize:

- **Dimensions**: Case size, button spacing, etc.
- **Layout**: Component positions
- **Materials**: Thickness, tolerances
- **AI Settings**: Model, temperature, auto-render
- **Paths**: Input/output directories

Example modifications:

```yaml
dimensions:
  case_length: 320    # Make case longer
  case_height: 45     # Make case taller

layout:
  screen:
    x: -10            # Move screen left
    y: 5              # Move screen up
```

## Advanced Features

### Custom Modifications

Create custom modification functions:

```python
def add_cooling_vents(params):
    """Add cooling vents to the back panel"""
    return {
        'type': 'geometry_modification',
        'openscad_code': '''
        for(i = [0:5]) {
            translate([i*10, 0, 0])
            cylinder(d=3, h=10);
        }
        '''
    }
```

### Batch Processing

Process multiple designs:

```bash
# Create variants
python3 -c "
from cad_automator import CADAutomator
automator = CADAutomator()
for size in ['small', 'medium', 'large']:
    automator.create_variant(size)
    automator.render_design()
"
```

### Integration with External Tools

The system can integrate with:
- **Blender**: Import STL for detailed editing
- **FreeCAD**: Parametric modeling
- **Slic3r/Cura**: Slicing for 3D printing
- **Git**: Version control for designs

## Troubleshooting

### Common Issues

1. **OpenSCAD not found**:
   ```bash
   which openscad  # Check if installed
   sudo apt install openscad  # Install on Ubuntu
   ```

2. **Python dependencies missing**:
   ```bash
   pip install -r requirements.txt
   ```

3. **AI features not working**:
   ```bash
   echo $OPENAI_API_KEY  # Check if set
   export OPENAI_API_KEY="your-key"
   ```

4. **Web viewer not loading**:
   - Check if port 8000 is free
   - Try `python3 -m http.server 8001 --directory web_viewer`

### Debug Commands

```bash
# Check project status
make info

# Validate OpenSCAD files
make validate

# Test Python imports
python3 -c "import yaml, numpy; print('Dependencies OK')"

# List available models
python3 model_library.py --scan
```

## Next Steps

1. **Explore Models**: Use `make interactive` and type `models` to see available components
2. **Customize Design**: Edit `config.yaml` or use natural language modifications
3. **Generate Variants**: Create multiple versions for different use cases
4. **Export for Printing**: Use `make export-all` to get STL files ready for 3D printing

## Tips

- Start with small modifications to understand the system
- Use `render` frequently to see changes
- Save important configurations in git
- Use the web viewer for quick previews
- Combine multiple small changes rather than large ones

Happy building! 🎮
