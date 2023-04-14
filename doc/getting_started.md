# Installation
1. Download the latest python script from the source directory (e.g. "export_rfactor2_pm_v0_2_0.py")
2. Start Blender
3. Open the "Edit" menu on the top bar of Blender.
4. Click on "Preferences..."
5. Click on "Add-ons"
6. Click on "Install..."
7. Browse to the location where you downloaded the python script.
8. Select the python script.
9. Click on "Install Add-on"

Note: The addon is not enabled after install, please tick the checkbox on the left side to activate it.

# Usage
1. Modify the suspension objects according to your or the vehicles needs.
2. Open the "File" menu on the top bar of Blender.
3. Hover over "Export"
4. Click on "Export rFactor2 Suspension Model (.pm)"
5. Chose the location to save the file and set the file name.
6. Click on "Export PM"

Open the PM file in a text editor of your choice to verify the export looks OK. If the file looks OK, you can copy it into your vehicle directory in the rF2 ModDev install. I strongly recommend to not export the PM from Blender directly into that directory to not accidentally overwrite working PM files (always take a backup!).

# Known Issues
Calculation of inertia is simplified and may not give accurate results in all cases.
