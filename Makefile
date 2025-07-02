# NucDeck CAD Automation Makefile
# Provides easy commands for building, rendering, and managing the project

.PHONY: help setup install render clean export catalog interactive demo test

# Default target
help:
	@echo "🎮 NucDeck CAD Automation"
	@echo "========================"
	@echo ""
	@echo "Available targets:"
	@echo "  setup      - Set up development environment"
	@echo "  install    - Install Python dependencies"
	@echo "  render     - Render current design"
	@echo "  catalog    - Generate model catalog"
	@echo "  export     - Export STL files"
	@echo "  interactive - Start interactive CAD assistant"
	@echo "  web        - Start web viewer server"
	@echo "  demo       - Run demo modifications"
	@echo "  clean      - Clean output files"
	@echo "  test       - Run tests"

# Environment setup
setup:
	@echo "🔧 Setting up NucDeck CAD environment..."
	chmod +x setup.sh
	./setup.sh

install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt

# Model operations
catalog:
	@echo "📚 Generating model catalog..."
	python3 model_library.py --catalog --generate-imports

render:
	@echo "🎨 Rendering design..."
	python3 cad_automator.py --render

render-high:
	@echo "🎨 Rendering design (high quality)..."
	python3 cad_automator.py --render --quality high

# Export operations
export:
	@echo "📤 Exporting STL files..."
	mkdir -p output/stl
	openscad -o output/stl/nucdeck_housing_front.stl OpenSCAD/nucdeck_assembly.scad
	@echo "✅ Export complete"

export-all:
	@echo "📤 Exporting all formats..."
	mkdir -p output/stl output/3mf
	openscad -o output/stl/nucdeck_complete.stl OpenSCAD/nucdeck_assembly.scad
	openscad -o output/3mf/nucdeck_complete.3mf OpenSCAD/nucdeck_assembly.scad
	@echo "✅ All exports complete"

# Interactive tools
interactive:
	@echo "🤖 Starting interactive CAD assistant..."
	python3 cad_assistant.py

web:
	@echo "🌐 Starting web viewer at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	python3 -m http.server 8000 --directory web_viewer

# Demo and testing
demo:
	@echo "🎯 Running demo modifications..."
	python3 -c "from cad_automator import CADAutomator; c = CADAutomator(); c.apply_modifications(['Increase case height by 5mm', 'Move screen 10mm to the left'])"

test:
	@echo "🧪 Running tests..."
	python3 -m pytest tests/ -v

# Utility commands
clean:
	@echo "🧹 Cleaning output files..."
	rm -rf output/* temp/* *.png *.stl
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "✅ Clean complete"

validate:
	@echo "✅ Validating OpenSCAD files..."
	openscad --check OpenSCAD/nucdeck_assembly.scad

# Development commands
dev-server:
	@echo "🔄 Starting development server with auto-reload..."
	python3 -c "import time; print('Development server started. Modify files and run make render to see changes.'); time.sleep(1000)"

watch:
	@echo "👀 Watching for file changes..."
	@which inotifywait > /dev/null || (echo "Install inotify-tools: sudo apt install inotify-tools"; exit 1)
	while inotifywait -e modify OpenSCAD/*.scad config.yaml; do make render; done

# Quick commands
quick-render: catalog render
quick-export: catalog export
quick-start: setup catalog interactive

# Documentation
docs:
	@echo "📖 Generating documentation..."
	@echo "TODO: Add documentation generation"

# Project info
info:
	@echo "ℹ️  Project Information"
	@echo "Name: NucDeck CAD Automation"
	@echo "Version: $(shell grep version config.yaml | cut -d'"' -f2)"
	@echo "Python: $(shell python3 --version)"
	@echo "OpenSCAD: $(shell openscad --version 2>/dev/null | head -1 || echo 'Not installed')"
	@echo ""
	@python3 model_library.py --scan
