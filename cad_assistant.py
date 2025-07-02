#!/usr/bin/env python3
"""
Interactive CAD Assistant for NucDeck
Provides a conversational interface for CAD modifications
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import openai
from model_library import ModelLibrary

class CADAssistant:
    """Interactive assistant for CAD operations"""
    
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model_library = ModelLibrary(config_path)
        self.conversation_history = []
        self.current_project = {
            'name': 'Default Project',
            'version': '1.0',
            'modifications': [],
            'last_render': None,
            'parameters': {}
        }
        
        # Initialize OpenAI if API key is available
        if "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
            self.ai_enabled = True
        else:
            print("⚠️  OpenAI API key not found. AI features disabled.")
            print("   Set OPENAI_API_KEY environment variable to enable AI.")
            self.ai_enabled = False
    
    def start_interactive_session(self):
        """Start an interactive CAD session"""
        print("🎮 NucDeck CAD Assistant")
        print("=" * 50)
        print("Type 'help' for commands, 'quit' to exit")
        print()
        
        # Load existing project or create new
        self.load_or_create_project()
        
        while True:
            try:
                user_input = input("CAD> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                elif user_input.startswith('modify '):
                    self.handle_modification(user_input[7:])
                elif user_input.startswith('render'):
                    self.handle_render(user_input)
                elif user_input.startswith('list '):
                    self.handle_list(user_input[5:])
                elif user_input.startswith('config '):
                    self.handle_config(user_input[7:])
                elif user_input.startswith('export '):
                    self.handle_export(user_input[7:])
                elif user_input.lower() == 'status':
                    self.show_status()
                elif user_input.lower() == 'models':
                    self.show_models()
                elif user_input and self.ai_enabled:
                    self.handle_ai_query(user_input)
                else:
                    print("Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Show available commands"""
        help_text = """
Available Commands:
  help                    - Show this help
  status                  - Show current project status
  models                  - List available models
  
  modify <description>    - Modify design (e.g., "modify make case 5mm taller")
  render [quality]        - Render current design (low/medium/high)
  config <param> <value>  - Update configuration
  export <format>         - Export design (stl, step, 3mf)
  
  list models            - List all available models
  list categories        - List model categories
  
  <natural language>     - Ask AI assistant (if enabled)
  
  quit                   - Exit assistant
"""
        print(help_text)
    
    def load_or_create_project(self):
        """Load existing project or create new one"""
        project_file = "current_project.json"
        
        if os.path.exists(project_file):
            with open(project_file, 'r') as f:
                self.current_project = json.load(f)
            print(f"📁 Loaded project: {self.current_project.get('name', 'Unnamed')}")
        else:
            self.current_project = {
                'name': self.config['project']['name'],
                'version': self.config['project']['version'],
                'modifications': [],
                'last_render': None,
                'parameters': self.config.copy()
            }
            self.save_project()
            print(f"📁 Created new project: {self.current_project['name']}")
    
    def save_project(self):
        """Save current project state"""
        with open("current_project.json", 'w') as f:
            json.dump(self.current_project, f, indent=2)
    
    def handle_modification(self, description: str):
        """Handle design modification requests"""
        print(f"🔧 Processing modification: {description}")
        
        if self.ai_enabled:
            # Use AI to interpret the modification
            modification = self.ai_interpret_modification(description)
            if modification:
                self.apply_modification(modification)
        else:
            # Manual interpretation
            print("AI not available. Please use specific commands like:")
            print("  config dimensions.case_height 45")
            print("  config layout.screen.x 10")
    
    def ai_interpret_modification(self, description: str) -> Optional[Dict]:
        """Use AI to interpret modification request"""
        prompt = f"""
Given this CAD modification request: "{description}"
And this current configuration:
{json.dumps(self.current_project['parameters'], indent=2)}

Generate a specific modification as JSON with this structure:
{{
  "type": "parameter_change|geometry_modification|component_addition",
  "changes": {{
    "config_path": "value",
    ...
  }},
  "description": "What this modification does",
  "openscad_code": "Any additional OpenSCAD code needed"
}}

Focus on the parameters in the config that can be modified.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config['ai']['model'],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config['ai']['temperature']
            )
            
            result = response.choices[0].message.content
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        
        except Exception as e:
            print(f"AI interpretation failed: {e}")
        
        return None
    
    def apply_modification(self, modification: Dict):
        """Apply a modification to the current project"""
        print(f"Applying: {modification.get('description', 'Unnamed modification')}")
        
        # Update configuration parameters
        if 'changes' in modification:
            for config_path, value in modification['changes'].items():
                self.set_nested_config(config_path, value)
        
        # Add to modification history
        self.current_project['modifications'].append(modification)
        self.save_project()
        
        # Auto-render if enabled
        if self.config['ai']['auto_render']:
            self.render_design()
        
        print("✅ Modification applied")
    
    def set_nested_config(self, path: str, value):
        """Set a nested configuration value using dot notation"""
        keys = path.split('.')
        target = self.current_project['parameters']
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
        print(f"  {path} = {value}")
    
    def handle_render(self, command: str):
        """Handle render commands"""
        parts = command.split()
        quality = parts[1] if len(parts) > 1 else "medium"
        self.render_design(quality)
    
    def render_design(self, quality: str = "medium"):
        """Render the current design"""
        print(f"🎨 Rendering design (quality: {quality})...")
        
        # Update OpenSCAD file with current parameters
        self.generate_openscad_file()
        
        # Render with OpenSCAD
        input_file = "OpenSCAD/nucdeck_assembly.scad"
        output_file = f"output/nucdeck_render_{quality}.png"
        
        quality_settings = {
            "low": "--imgsize=800,600 --render",
            "medium": "--imgsize=1200,900 --render",
            "high": "--imgsize=1920,1440 --render"
        }
        
        cmd = f"openscad {quality_settings.get(quality, quality_settings['medium'])} -o {output_file} {input_file}"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Render complete: {output_file}")
                self.current_project['last_render'] = output_file
                self.save_project()
            else:
                print(f"❌ Render failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Render error: {e}")
    
    def generate_openscad_file(self):
        """Generate OpenSCAD file with current parameters"""
        # This would generate a new .scad file based on current parameters
        # For now, we'll update variables in the existing file
        print("📝 Updating OpenSCAD parameters...")
    
    def handle_list(self, what: str):
        """Handle list commands"""
        if what == "models":
            models = self.model_library.scan_models()
            for category, model_list in models.items():
                print(f"{category}: {len(model_list)} files")
        elif what == "categories":
            # Get unique categories
            all_models = self.model_library.scan_models()
            categories = set()
            for model_list in all_models.values():
                for model_path in model_list:
                    info = self.model_library.get_model_info(Path(model_path))
                    categories.add(info['category'])
            
            print("Available categories:")
            for cat in sorted(categories):
                print(f"  - {cat}")
    
    def handle_config(self, command: str):
        """Handle configuration changes"""
        parts = command.split(' ', 1)
        if len(parts) != 2:
            print("Usage: config <parameter> <value>")
            return
        
        param, value = parts
        try:
            # Try to convert value to appropriate type
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.replace('.', '', 1).isdigit():
                value = float(value) if '.' in value else int(value)
            
            self.set_nested_config(param, value)
            self.save_project()
            print("✅ Configuration updated")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
    
    def handle_export(self, format_type: str):
        """Handle export commands"""
        print(f"📤 Exporting to {format_type.upper()}...")
        
        input_file = "OpenSCAD/nucdeck_assembly.scad"
        output_file = f"output/nucdeck_export.{format_type.lower()}"
        
        cmd = f"openscad -o {output_file} {input_file}"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Export complete: {output_file}")
            else:
                print(f"❌ Export failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Export error: {e}")
    
    def show_status(self):
        """Show current project status"""
        print(f"📊 Project Status")
        print(f"Name: {self.current_project['name']}")
        print(f"Version: {self.current_project['version']}")
        print(f"Modifications: {len(self.current_project['modifications'])}")
        if self.current_project['last_render']:
            print(f"Last render: {self.current_project['last_render']}")
        print(f"AI enabled: {self.ai_enabled}")
    
    def show_models(self):
        """Show available models"""
        models = self.model_library.scan_models()
        total = sum(len(model_list) for model_list in models.values())
        print(f"📦 Available Models ({total} total)")
        
        for category, model_list in models.items():
            if model_list:
                print(f"\n{category.replace('_', ' ').title()}:")
                for model_path in model_list[:5]:  # Show first 5
                    name = Path(model_path).stem
                    print(f"  - {name}")
                if len(model_list) > 5:
                    print(f"  ... and {len(model_list) - 5} more")
    
    def handle_ai_query(self, query: str):
        """Handle general AI queries"""
        if not self.ai_enabled:
            print("AI features are disabled. Set OPENAI_API_KEY to enable.")
            return
        
        print("🤖 Thinking...")
        
        context = f"""
You are a CAD assistant for the NucDeck handheld gaming device project.
Current project configuration:
{json.dumps(self.current_project['parameters'], indent=2)}

Available models: {list(self.model_library.scan_models().keys())}

User query: {query}

Provide helpful advice, suggestions, or ask for clarification.
If the user wants to modify something, suggest specific config commands.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": "You are a helpful CAD assistant."},
                    {"role": "user", "content": context}
                ],
                temperature=self.config['ai']['temperature']
            )
            
            print("🤖", response.choices[0].message.content)
        
        except Exception as e:
            print(f"❌ AI query failed: {e}")

def main():
    """Main entry point"""
    assistant = CADAssistant()
    assistant.start_interactive_session()

if __name__ == "__main__":
    main()
