# ScadLM

Open source agentic AI CAD generation built on OpenSCAD. Merging https://github.com/KrishKrosh/ScadLM with https://github.com/dmcke5/NucDeck.git in order to have a play around with the below objective.

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
