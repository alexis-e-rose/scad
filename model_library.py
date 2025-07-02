#!/usr/bin/env python3
"""
NucDeck Model Library Manager
Manages STL/STEP files and provides interfaces for OpenSCAD integration
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

class ModelLibrary:
    """Manages the collection of 3D models and their metadata"""
    
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.base_path = Path(".")
        self.cache_file = "model_cache.json"
        self.model_cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load model metadata cache"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save model metadata cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.model_cache, f, indent=2)
    
    def scan_models(self) -> Dict[str, List[str]]:
        """Scan directories for STL and STEP files"""
        models = {
            'housing_stl': [],
            'housing_step': [],
            'buttons_stl': [],
            'buttons_step': []
        }
        
        # Scan housing files
        housing_stl_path = self.base_path / self.config['paths']['stl_import']
        if housing_stl_path.exists():
            models['housing_stl'] = list(housing_stl_path.glob("*.STL"))
        
        housing_step_path = self.base_path / self.config['paths']['step_import']
        if housing_step_path.exists():
            models['housing_step'] = list(housing_step_path.glob("*.STEP"))
        
        # Scan button files
        buttons_stl_path = self.base_path / self.config['paths']['buttons_stl']
        if buttons_stl_path.exists():
            for subdir in buttons_stl_path.iterdir():
                if subdir.is_dir():
                    models['buttons_stl'].extend(subdir.glob("*.STL"))
                else:
                    if subdir.suffix == ".STL":
                        models['buttons_stl'].append(subdir)
        
        buttons_step_path = self.base_path / self.config['paths']['buttons_step']
        if buttons_step_path.exists():
            for subdir in buttons_step_path.iterdir():
                if subdir.is_dir():
                    models['buttons_step'].extend(subdir.glob("*.STEP"))
                else:
                    if subdir.suffix == ".STEP":
                        models['buttons_step'].append(subdir)
        
        return models
    
    def get_model_info(self, model_path: Path) -> Dict:
        """Get metadata for a specific model"""
        model_key = str(model_path)
        
        if model_key in self.model_cache:
            return self.model_cache[model_key]
        
        # Generate new metadata
        info = {
            'name': model_path.stem,
            'path': str(model_path),
            'type': model_path.suffix.lower(),
            'size': model_path.stat().st_size if model_path.exists() else 0,
            'category': self._categorize_model(model_path),
            'description': self._generate_description(model_path)
        }
        
        self.model_cache[model_key] = info
        self._save_cache()
        return info
    
    def _categorize_model(self, model_path: Path) -> str:
        """Categorize model based on path and name"""
        path_str = str(model_path).lower()
        name = model_path.stem.lower()
        
        if 'housing' in path_str:
            if 'front' in name:
                return 'housing_front'
            elif 'back' in name or 'cover' in name:
                return 'housing_back'
            elif 'grip' in name:
                return 'housing_grip'
            elif 'trigger' in name:
                return 'housing_trigger'
            else:
                return 'housing_misc'
        
        elif 'button' in path_str:
            if 'action' in name:
                return 'button_action'
            elif 'trigger' in name:
                return 'button_trigger'
            elif 'shoulder' in name:
                return 'button_shoulder'
            elif 'dpad' or 'd-pad' in name:
                return 'button_dpad'
            elif 'volume' in name:
                return 'button_volume'
            else:
                return 'button_misc'
        
        return 'unknown'
    
    def _generate_description(self, model_path: Path) -> str:
        """Generate a description for the model"""
        name = model_path.stem
        category = self._categorize_model(model_path)
        
        descriptions = {
            'housing_front': 'Front housing panel with screen cutout and button holes',
            'housing_back': 'Back cover with ventilation and port access',
            'housing_grip': 'Side grip for ergonomic handling',
            'housing_trigger': 'Trigger mount assembly',
            'button_action': 'Action button (A/B/X/Y)',
            'button_trigger': 'Trigger button assembly',
            'button_shoulder': 'Shoulder button',
            'button_dpad': 'Directional pad',
            'button_volume': 'Volume control button'
        }
        
        return descriptions.get(category, f"3D model component: {name}")
    
    def get_models_by_category(self, category: str) -> List[Dict]:
        """Get all models in a specific category"""
        models = self.scan_models()
        result = []
        
        for model_list in models.values():
            for model_path in model_list:
                info = self.get_model_info(Path(model_path))
                if info['category'] == category:
                    result.append(info)
        
        return result
    
    def generate_openscad_imports(self) -> str:
        """Generate OpenSCAD import statements for all models"""
        models = self.scan_models()
        imports = []
        
        imports.append("// Auto-generated model imports")
        imports.append("")
        
        for category, model_list in models.items():
            if model_list:
                imports.append(f"// {category.replace('_', ' ').title()}")
                for i, model_path in enumerate(model_list):
                    var_name = f"{category}_{i}"
                    imports.append(f'module {var_name}() {{')
                    imports.append(f'    import("{model_path}");')
                    imports.append('}')
                imports.append("")
        
        return "\n".join(imports)
    
    def export_model_catalog(self, output_file: str = "model_catalog.json"):
        """Export complete model catalog"""
        models = self.scan_models()
        catalog = {}
        
        for category, model_list in models.items():
            catalog[category] = []
            for model_path in model_list:
                catalog[category].append(self.get_model_info(Path(model_path)))
        
        with open(output_file, 'w') as f:
            json.dump(catalog, f, indent=2, default=str)
        
        print(f"Model catalog exported to {output_file}")

def main():
    """CLI interface for model library management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NucDeck Model Library Manager")
    parser.add_argument("--scan", action="store_true", help="Scan for models")
    parser.add_argument("--catalog", action="store_true", help="Export model catalog")
    parser.add_argument("--generate-imports", action="store_true", help="Generate OpenSCAD imports")
    parser.add_argument("--category", type=str, help="Filter by category")
    
    args = parser.parse_args()
    
    library = ModelLibrary()
    
    if args.scan:
        models = library.scan_models()
        print("Found models:")
        for category, model_list in models.items():
            print(f"  {category}: {len(model_list)} files")
    
    if args.catalog:
        library.export_model_catalog()
    
    if args.generate_imports:
        imports = library.generate_openscad_imports()
        with open("OpenSCAD/model_imports.scad", "w") as f:
            f.write(imports)
        print("OpenSCAD imports generated in OpenSCAD/model_imports.scad")
    
    if args.category:
        models = library.get_models_by_category(args.category)
        print(f"Models in category '{args.category}':")
        for model in models:
            print(f"  - {model['name']}: {model['description']}")

if __name__ == "__main__":
    main()
