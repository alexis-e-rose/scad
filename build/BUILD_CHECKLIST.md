# Handheld Build Checklist - PETG Version

## Pre-Build Preparation
- [ ] All components verified against inventory list
- [ ] Creality Sermoon V1 Pro calibrated for PETG
- [ ] PETG print settings verified (see PETG_PRINT_SETTINGS.md)
- [ ] Tools and workspace prepared
- [ ] Safety equipment available (ESD mat, safety glasses)
- [ ] Teardown video bookmarked: https://youtu.be/1VLbJQIDlQU
- [ ] Datasheets downloaded for all electronic components
- [ ] Measurement templates printed (MEASUREMENT_TEMPLATES.md)

## Phase 1: Controller Salvage ⏱️ 1.5-2.5 hours (Interruptible)

### Setup
- [ ] ESD-safe workspace prepared
- [ ] Tools laid out: Phillips #0, spudger, tweezers
- [ ] Camera/phone ready for documentation photos
- [ ] Component storage containers labeled

### Disassembly
- [ ] Xbox controller photographed (before state)
- [ ] Screws removed and stored safely
- [ ] Cable routing documented with photos
- [ ] Controller opened without damage

### Component Extraction
- [ ] Left joystick module removed (test pots: __ kΩ)
- [ ] Right joystick module removed (test pots: __ kΩ)
- [ ] D-pad assembly extracted intact
- [ ] ABXY buttons removed with switches
- [ ] All wiring harnesses preserved
- [ ] Components cleaned with IPA

### Documentation & Storage
- [ ] Each component labeled and photographed
- [ ] Connection diagram sketched
- [ ] Components stored in anti-static bags
- [ ] Resistance/continuity measurements recorded

**Phase 1 Complete:** ___/___/___ Time: ____

---

## Phase 2: Electronics Assembly ⏱️ 2.5-4 hours ⚠️ COMPLETE POWER CHAIN ONCE STARTED

### Preparation
- [ ] Soldering station heated and tinned
- [ ] JST pigtails cut to ~80mm length
- [ ] All wire ends stripped and tinned
- [ ] Flux applied to connection points
- [ ] Multimeter calibrated and ready

### Wiring Assembly
- [ ] Battery to TP4056: Red→BAT+, Black→BAT- ✓
- [ ] Polarity verified twice before power connection
- [ ] TP4056 OUT+ to PD-trigger IN+ ✓
- [ ] TP4056 OUT- to PD-trigger IN- ✓
- [ ] PD-trigger OUT+ to USB-C splitter VCC ✓
- [ ] PD-trigger OUT- to USB-C splitter GND ✓
- [ ] Power switch wired inline on positive rail ✓

### Indicator Integration
- [ ] Indicator PCB connected to battery output
- [ ] Polarity verified per PCB silkscreen
- [ ] Indicator display tested (shows battery level)

### Testing Protocol
- [ ] Visual inspection: All joints clean and secure
- [ ] Continuity test: No shorts detected
- [ ] Charging test: TP4056 LED indicates charging
- [ ] Power test: Switch operates cleanly
- [ ] Idle draw measured: _____ mA (<20mA target)
- [ ] No component heating detected

**Phase 2 Complete:** ___/___/___ Time: ____

---

## Phase 3: Mechanical Verification ⏱️ 1.5-3 hours (Interruptible)

### Mockup Preparation
- [ ] Phone jig printed/cut: 157.7×75.1×15.9 mm
- [ ] Component mockups created:
  - [ ] TP4056: 23×16×5 mm
  - [ ] PD-trigger: 23.3×11.9×4 mm  
  - [ ] Indicator: 43.5×20 mm
  - [ ] Battery: 90×60×12 mm
- [ ] Ø32mm washers for joystick simulation

### Fit Testing
- [ ] Phone slides into jig smoothly
- [ ] 3mm clearance verified on all phone sides
- [ ] Battery positioned with 4mm clearance
- [ ] Electronics have mounting locations
- [ ] No interference between components

### Layout Verification
- [ ] Joystick positions comfortable for thumbs
- [ ] D-pad accessible without hand repositioning
- [ ] ABXY buttons in natural finger position
- [ ] Power switch reachable but protected
- [ ] USB-C port accessible for charging

### Parameter Updates
- [ ] OpenSCAD parameters updated if needed:
  - [ ] phone_cutout_width: ______ mm
  - [ ] phone_cutout_height: ______ mm
  - [ ] joystick_position_x: ±____ mm
  - [ ] joystick_position_y: ______ mm
  - [ ] battery_clearance: ______ mm

**Phase 3 Complete:** ___/___/___ Time: ____

---

## Phase 4: Final Assembly ⏱️ 4-6 hours + 14-21 hour prints

### PETG Print Phase (Can run unattended)
- [ ] Sermoon V1 Pro ready with PETG settings
- [ ] Print settings confirmed:
  - [ ] Nozzle: 240°C
  - [ ] Bed: 85°C
  - [ ] Layer height: 0.2mm
  - [ ] Infill: 25%
  - [ ] Walls: 4 lines
  - [ ] Speed: 50mm/s
- [ ] Estimated material needed: ~350g PETG
- [ ] Front shell started: ___/___/___ at ___:___
- [ ] Front shell completed: ___/___/___ at ___:___
- [ ] Rear shell started: ___/___/___ at ___:___
- [ ] Rear shell completed: ___/___/___ at ___:___

### Print Quality Check
- [ ] 3D printer calibrated
- [ ] Print settings verified:
  - [ ] Layer height: 0.2mm
  - [ ] Infill: 20%
  - [ ] Wall lines: 3-4
  - [ ] Support: Only >45° overhangs
- [ ] Estimated print time: ______ hours

### Shell Printing
- [ ] Front shell printed successfully
- [ ] Rear shell printed successfully
- [ ] Support material removed
- [ ] All edges deburred
- [ ] Shell halves test-fit together
- [ ] M3 threaded inserts installed

### Electronics Installation (Rear Shell)
- [ ] Battery mounted with foam tape
- [ ] TP4056 board installed near battery
- [ ] PD-trigger mounted near USB-C opening
- [ ] Indicator PCB in visible location
- [ ] All wiring routed with strain relief
- [ ] Zip ties used for wire management

### Controls Installation (Front Shell)
- [ ] Left joystick installed and secured
- [ ] Right joystick installed and secured
- [ ] D-pad mounted in position
- [ ] ABXY buttons installed
- [ ] Power switch mounted
- [ ] All control harnesses connected

### Final Integration
- [ ] USB-C splitter routed to phone pocket
- [ ] All electronic connections made
- [ ] Continuity check passed
- [ ] No pinched wires detected
- [ ] Shell alignment verified

### Closing & Testing
- [ ] Front and rear shells aligned
- [ ] M3 screws installed in sequence
- [ ] Shell gaps <0.5mm
- [ ] Power-on test successful
- [ ] Charging test passed
- [ ] All controls responsive
- [ ] Battery indicator functional
- [ ] Thermal test completed (30 min load)

**Phase 4 Complete:** ___/___/___ Time: ____

---

## Final Quality Checks

### Functional Tests
- [ ] Phone fits and operates correctly
- [ ] All joystick axes calibrated
- [ ] D-pad responds in all directions
- [ ] ABXY buttons register properly
- [ ] Power switch operates cleanly
- [ ] Charging system works correctly
- [ ] Battery indicator accurate

### Physical Inspection
- [ ] No sharp edges or rough surfaces
- [ ] All screws properly tightened
- [ ] Shell flex minimal under normal grip
- [ ] Controls have good tactile feel
- [ ] Ergonomics comfortable for extended use

### Performance Verification
- [ ] Idle power draw: _____ mA
- [ ] Gaming power draw: _____ mA
- [ ] Component temperatures normal
- [ ] No overheating after 1-hour test
- [ ] Battery life meets expectations

---

## Project Documentation

### Final Documentation
- [ ] Build photos taken
- [ ] Lessons learned documented
- [ ] Any modifications noted
- [ ] Parts list updated with sources
- [ ] Performance measurements recorded

### Maintenance Schedule
- [ ] Monthly: Clean joystick mechanisms
- [ ] Quarterly: Check screw tightness  
- [ ] Annually: Battery performance assessment
- [ ] As needed: Software updates

**Project Complete:** ___/___/___  
**Total Build Time:** ______ hours

---

## Notes & Modifications

**Changes Made:**
_____________________________________
_____________________________________
_____________________________________

**Issues Encountered:**
_____________________________________
_____________________________________
_____________________________________

**Future Improvements:**
_____________________________________
_____________________________________
_____________________________________

**Final Rating:** ⭐⭐⭐⭐⭐
