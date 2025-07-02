#!/usr/bin/env python3
"""
NucDeck CAD Automation & AI-Driven Design Assistant
Automates OpenSCAD rendering and provides AI-driven design modifications
"""

import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NucDeckCADAutomator:
    def __init__(self, workspace_path: str = "/workspaces/scad"):
        self.workspace_path = Path(workspace_path)
        self.openscad_dir = self.workspace_path / "OpenSCAD"
        self.output_dir = self.workspace_path / "output"
        self.main_scad_file = self.openscad_dir / "nucdeck_assembly.scad"
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        # Default parameters
        self.default_params = {
            "phone_width": 69.1,
            "phone_height": 151.7,
            "phone_depth": 7.9,
            "battery_width": 60,
            "battery_length": 90,
            "battery_height": 12,
            "grip_offset": 20,
            "show_phone_mockup": True,
            "show_battery_mockup": True,
            "exploded_view": False,
            "show_housing_front": True,
            "show_housing_back": True,
            "show_left_grip": True,
            "show_right_grip": True,
            "show_joystick_rings": True,
            "show_trigger_mounts": True,
            "show_buttons": True,
            "show_lcd_retainer": True
        }
    
    def check_openscad_installed(self) -> bool:
        """Check if OpenSCAD is installed and available"""
        try:
            result = subprocess.run(['openscad', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            logger.info(f"OpenSCAD found: {result.stdout.strip()}")
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("OpenSCAD not found. Please install OpenSCAD.")
            return False
    
    def generate_scad_with_params(self, params: Dict, output_file: Optional[str] = None) -> str:
        """Generate a custom SCAD file with specified parameters"""
        if output_file is None:
            output_file = self.openscad_dir / "nucdeck_custom.scad"
        
        # Read the base SCAD file
        with open(self.main_scad_file, 'r') as f:
            scad_content = f.read()
        
        # Replace parameter values
        for param, value in params.items():
            if isinstance(value, bool):
                value_str = "true" if value else "false"
            elif isinstance(value, str):
                value_str = f'"{value}"'
            else:
                value_str = str(value)
            
            # Use regex to replace parameter assignments
            pattern = rf'^({param}\s*=\s*)[^;]+;'
            replacement = rf'\g<1>{value_str};'
            scad_content = re.sub(pattern, replacement, scad_content, flags=re.MULTILINE)
        
        # Write the custom SCAD file
        with open(output_file, 'w') as f:
            f.write(scad_content)
        
        logger.info(f"Generated custom SCAD file: {output_file}")
        return str(output_file)
    
    def render_stl(self, scad_file: str, output_stl: str, params: Dict = None) -> bool:
        """Render SCAD file to STL using OpenSCAD"""
        if not self.check_openscad_installed():
            return False
        
        if params:
            scad_file = self.generate_scad_with_params(params)
        
        cmd = [
            'openscad',
            '-o', str(output_stl),
            str(scad_file)
        ]
        
        try:
            logger.info(f"Rendering STL: {output_stl}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Successfully rendered: {output_stl}")
                return True
            else:
                logger.error(f"OpenSCAD error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("OpenSCAD rendering timed out")
            return False
    
    def render_png_preview(self, scad_file: str, output_png: str, params: Dict = None) -> bool:
        """Render SCAD file to PNG preview using OpenSCAD"""
        if not self.check_openscad_installed():
            return False
        
        if params:
            scad_file = self.generate_scad_with_params(params)
        
        cmd = [
            'openscad',
            '--render',
            '--imgsize=800,600',
            '-o', str(output_png),
            str(scad_file)
        ]
        
        try:
            logger.info(f"Rendering preview: {output_png}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                logger.info(f"Successfully rendered preview: {output_png}")
                return True
            else:
                logger.error(f"OpenSCAD preview error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("OpenSCAD preview rendering timed out")
            return False
    
    def ai_suggest_modifications(self, user_prompt: str) -> Dict:
        """
        AI-driven design suggestions based on user input
        This is a placeholder for AI integration (OpenAI API, etc.)
        """
        suggestions = {}
        
        # Simple keyword-based suggestions (replace with actual AI integration)
        prompt_lower = user_prompt.lower()
        
        if "smaller" in prompt_lower or "compact" in prompt_lower:
            suggestions.update({
                "grip_offset": 15,
                "phone_width": self.default_params["phone_width"] * 0.9,
                "phone_height": self.default_params["phone_height"] * 0.9
            })
        
        if "larger" in prompt_lower or "bigger" in prompt_lower:
            suggestions.update({
                "grip_offset": 25,
                "phone_width": self.default_params["phone_width"] * 1.1,
                "phone_height": self.default_params["phone_height"] * 1.1
            })
        
        if "exploded" in prompt_lower or "assembly" in prompt_lower:
            suggestions["exploded_view"] = True
        
        if "hide" in prompt_lower:
            if "button" in prompt_lower:
                suggestions["show_buttons"] = False
            if "grip" in prompt_lower:
                suggestions["show_left_grip"] = False
                suggestions["show_right_grip"] = False
        
        if "show only" in prompt_lower or "isolate" in prompt_lower:
            # Hide all components first
            for key in self.default_params:
                if key.startswith("show_"):
                    suggestions[key] = False
            
            # Then show specific components based on prompt
            if "housing" in prompt_lower:
                suggestions["show_housing_front"] = True
                suggestions["show_housing_back"] = True
            if "grip" in prompt_lower:
                suggestions["show_left_grip"] = True
                suggestions["show_right_grip"] = True
        
        logger.info(f"AI suggestions for '{user_prompt}': {suggestions}")
        return suggestions
    
    def batch_render_variants(self, variants: List[Tuple[str, Dict]]) -> List[str]:
        """Render multiple design variants"""
        rendered_files = []
        
        for variant_name, params in variants:
            # Merge with default parameters
            merged_params = {**self.default_params, **params}
            
            # Generate output filenames
            stl_output = self.output_dir / f"nucdeck_{variant_name}.stl"
            png_output = self.output_dir / f"nucdeck_{variant_name}.png"
            
            # Render STL and PNG
            if self.render_stl(str(self.main_scad_file), str(stl_output), merged_params):
                rendered_files.append(str(stl_output))
            
            self.render_png_preview(str(self.main_scad_file), str(png_output), merged_params)
        
        return rendered_files
    
    def generate_design_report(self, params: Dict) -> str:
        """Generate a design report with specifications"""
        report = f"""
# NucDeck Design Report
Generated: {os.popen('date').read().strip()}

## Design Parameters
"""
        for key, value in params.items():
            report += f"- **{key}**: {value}\n"
        
        report += f"""
## Component Dimensions
- Phone: {params.get('phone_width', 0):.1f} × {params.get('phone_height', 0):.1f} × {params.get('phone_depth', 0):.1f} mm
- Battery: {params.get('battery_width', 0):.1f} × {params.get('battery_length', 0):.1f} × {params.get('battery_height', 0):.1f} mm
- Grip Extension: {params.get('grip_offset', 0):.1f} mm

## Files Generated
- SCAD: nucdeck_custom.scad
- STL: nucdeck_custom.stl
- Preview: nucdeck_custom.png
"""
        
        report_file = self.output_dir / "design_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        return str(report_file)

def main():
    parser = argparse.ArgumentParser(description='NucDeck CAD Automation Tool')
    parser.add_argument('--prompt', type=str, help='AI design prompt')
    parser.add_argument('--render-stl', action='store_true', help='Render STL output')
    parser.add_argument('--render-preview', action='store_true', help='Render PNG preview')
    parser.add_argument('--exploded', action='store_true', help='Generate exploded view')
    parser.add_argument('--batch', action='store_true', help='Render common variants')
    parser.add_argument('--output-name', type=str, default='custom', help='Output filename prefix')
    
    args = parser.parse_args()
    
    automator = NucDeckCADAutomator()
    
    if args.batch:
        # Render common variants
        variants = [
            ("standard", {}),
            ("exploded", {"exploded_view": True}),
            ("compact", {"grip_offset": 15, "phone_width": 62}),
            ("housing_only", {
                "show_buttons": False,
                "show_joystick_rings": False,
                "show_trigger_mounts": False
            })
        ]
        
        logger.info("Rendering batch variants...")
        rendered_files = automator.batch_render_variants(variants)
        logger.info(f"Rendered {len(rendered_files)} variants")
        
    else:
        # Single render with optional AI suggestions
        params = automator.default_params.copy()
        
        if args.prompt:
            ai_suggestions = automator.ai_suggest_modifications(args.prompt)
            params.update(ai_suggestions)
        
        if args.exploded:
            params["exploded_view"] = True
        
        # Generate outputs
        if args.render_stl or args.render_preview:
            stl_output = automator.output_dir / f"nucdeck_{args.output_name}.stl"
            png_output = automator.output_dir / f"nucdeck_{args.output_name}.png"
            
            if args.render_stl:
                automator.render_stl(str(automator.main_scad_file), str(stl_output), params)
            
            if args.render_preview:
                automator.render_png_preview(str(automator.main_scad_file), str(png_output), params)
        
        # Generate design report
        report_file = automator.generate_design_report(params)
        logger.info(f"Design report generated: {report_file}")

if __name__ == "__main__":
    main()
