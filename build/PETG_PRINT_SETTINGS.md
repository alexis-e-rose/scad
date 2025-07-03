# PETG Print Settings - Creality Sermoon V1 Pro

## Printer Specifications
- **Build Volume**: 175 × 175 × 165 mm
- **Enclosed Chamber**: Yes (excellent for PETG)
- **Heated Bed**: Up to 100°C
- **Extruder**: All-metal hotend capable of 300°C

## Optimal PETG Settings for Handheld Case

### Basic Settings
```
Material: PETG
Nozzle Temperature: 235-245°C
Bed Temperature: 80-85°C
Chamber Temperature: 45-55°C (if controllable)
Layer Height: 0.2mm
First Layer Height: 0.25mm
```

### Speed Settings
```
Print Speed: 45-55 mm/s
First Layer Speed: 20 mm/s
Outer Perimeter Speed: 35 mm/s
Inner Perimeter Speed: 50 mm/s
Infill Speed: 60 mm/s
Travel Speed: 120 mm/s
```

### Quality Settings
```
Layer Height: 0.2mm (optimal detail/strength balance)
Wall Line Count: 4 (for structural strength)
Wall Thickness: 1.6mm
Top/Bottom Layers: 5
Infill: 25% (increased from 20% for durability)
Infill Pattern: Gyroid or Grid
```

### Support Settings
```
Support: Only for overhangs >50° (PETG bridges well)
Support Overhang Angle: 50°
Support Pattern: Lines
Support Density: 15%
Support Z Distance: 0.25mm
Support X/Y Distance: 0.7mm
```

### Adhesion & Quality
```
Build Plate Adhesion: Brim (5mm width)
Brim Line Count: 8
Z-hop When Retracted: 0.2mm
Retraction Distance: 4mm
Retraction Speed: 35 mm/s
Coasting: Enabled (0.3mm³)
```

### PETG-Specific Considerations

#### Advantages for This Project
- **Chemical Resistance**: Better than PLA for handling oils from hands
- **Impact Resistance**: Superior durability for gaming device
- **Temperature Stability**: Won't deform in car/hot environments
- **Layer Adhesion**: Excellent strength between layers
- **Food Safe**: If using food-safe PETG variant

#### Print Challenges & Solutions
- **Stringing**: Use proper retraction and temperature tuning
- **Overextrusion**: Calibrate flow rate (typically 95-98%)
- **Bed Adhesion**: Clean bed with IPA, use brim
- **Bridging**: PETG bridges well, minimal supports needed

### Pre-Print Checklist
- [ ] Bed cleaned with isopropyl alcohol
- [ ] Nozzle temperature tower completed (235-245°C)
- [ ] Flow rate calibrated for your specific PETG
- [ ] Enclosure temperature stable at 45-55°C
- [ ] Bed leveling verified
- [ ] Z-offset calibrated for PETG (may need adjustment from PLA)

### Estimated Print Times (Sermoon V1 Pro)

#### Front Shell
- **Estimated Time**: 8-12 hours
- **Material Usage**: ~150-200g PETG
- **Complexity**: High (controls cutouts, ergonomic curves)

#### Rear Shell  
- **Estimated Time**: 6-9 hours
- **Material Usage**: ~120-180g PETG
- **Complexity**: Medium (electronics cutouts, battery well)

#### Total Print Time: 14-21 hours
*Note: Times vary based on infill, quality settings, and part orientation*

### Post-Processing for PETG
1. **Removal**: Let bed cool to room temperature for easy removal
2. **Support Removal**: PETG supports remove cleanly
3. **Deburring**: Light sanding with 220-grit if needed
4. **Threading**: Tap M3 holes while plastic is warm for best threads
5. **Test Fit**: PETG has minimal shrinkage, should fit as designed

### Quality Control
- **Layer Adhesion**: Look for consistent extrusion
- **Dimensional Accuracy**: Measure critical features with calipers
- **Surface Finish**: PETG naturally has slight gloss
- **Structural Integrity**: Check wall thickness and infill

### Troubleshooting Common PETG Issues

**Problem: Stringing between features**
- Solution: Increase retraction distance to 5-6mm
- Lower nozzle temperature by 5°C
- Increase travel speed to 150 mm/s

**Problem: Poor bed adhesion**
- Solution: Increase bed temperature to 90°C for first layer
- Clean bed thoroughly with IPA
- Use larger brim (10mm width)

**Problem: Overextrusion/blobs**
- Solution: Reduce flow rate to 95%
- Enable linear advance if available
- Reduce print speed by 10 mm/s

**Problem: Layer splitting**
- Solution: Increase nozzle temperature by 5°C
- Reduce cooling fan speed to 30%
- Check for drafts in enclosure

### Safety Notes for PETG
- **Ventilation**: PETG produces minimal fumes but ensure adequate airflow
- **Temperature**: Hotend temperatures are high (245°C), use caution
- **Handling**: Let parts cool completely before handling
- **Storage**: Store unused PETG in dry environment

### Final Recommendations
- **First Layer**: Take time to get perfect first layer adhesion
- **Temperature**: Run temperature tower with your specific PETG brand
- **Patience**: PETG prints slower than PLA but results are worth it
- **Testing**: Print small test pieces first to verify settings
