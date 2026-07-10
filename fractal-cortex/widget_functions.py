"""
widget_functions.py

Copyright (C) 2025 Daniel Brogan

This file is part of the Fractal Cortex project.
Fractal Cortex is a Multidirectional 5-Axis FDM Slicer.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pyglet
from pyglet import event
from pyglet.window import key
import glooey
from glooey import drawing
from tkinter import filedialog
import os
from glooey.helpers import *
from fractal_widgets import *
from slicing_functions import *

"""
Instantiates and places all widgets within the GUI.
Contains all functions that are triggered upon interacting with widgets.
"""

# Adding a custom font
font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roboto-Regular.ttf")
pyglet.font.add_file(font_path)
pyglet.font.load("Roboto")

import json


PRINTER_FILE = "printer.json"
DEFAULT_PRINTER = {
    "buildPlateShape": "rectangular",
    "buildPlateX": 235.0,
    "buildPlateY": 235.0,
    "buildPlateZ": 250.0
}

if not os.path.exists(PRINTER_FILE):
    with open(PRINTER_FILE, 'w') as f:
        json.dump(DEFAULT_PRINTER, f, indent=4)
        
with open(PRINTER_FILE, 'r') as f:
    printerConfig = json.load(f)

buildPlateShape = printerConfig.get("buildPlateShape", "rectangular")
buildPlateX = printerConfig.get("buildPlateX", 235.0)
buildPlateY = printerConfig.get("buildPlateY", 235.0)
buildPlateZ = printerConfig.get("buildPlateZ", 250.0)

def save_printer_config():
    global buildPlateShape, buildPlateX, buildPlateY, buildPlateZ, buildPlateBounds
    config = {
        "buildPlateShape": buildPlateShape,
        "buildPlateX": buildPlateX,
        "buildPlateY": buildPlateY,
        "buildPlateZ": buildPlateZ
    }
    with open(PRINTER_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    # Update bounds
    if buildPlateShape == "circular":
        buildPlateBounds = [-buildPlateX/2, buildPlateX/2]
    else:
        buildPlateBounds = [-buildPlateX/2, buildPlateX/2]

save_printer_config() # initialize bounds

PROFILES_FILE = "profiles.json"

DEFAULT_PROFILES = {
    "PLA": {
        "type": "PLA",
        "diameter": 1.75,
        "softeningTemp": 45,
        "idleTemp": 0,
        "minNozzleTemp": 190,
        "maxNozzleTemp": 240,
        "enablePressureAdvance": False,
        "chamberTemp": 0,
        "activateChamberTemp": False,
        "nozzleFirstLayer": 220,
        "nozzleOtherLayers": 220,
        "bedFirstLayer": 55,
        "bedOtherLayers": 55
    },
    "Bambu PLA Basic": {
        "type": "PLA",
        "diameter": 1.75,
        "softeningTemp": 45,
        "idleTemp": 0,
        "minNozzleTemp": 190,
        "maxNozzleTemp": 240,
        "enablePressureAdvance": False,
        "chamberTemp": 0,
        "activateChamberTemp": False,
        "nozzleFirstLayer": 220,
        "nozzleOtherLayers": 220,
        "bedFirstLayer": 65,
        "bedOtherLayers": 65
    },
    "Bambu PETG Basic": {
        "type": "PETG",
        "diameter": 1.75,
        "softeningTemp": 68,
        "idleTemp": 0,
        "minNozzleTemp": 240,
        "maxNozzleTemp": 270,
        "enablePressureAdvance": False,
        "chamberTemp": 0,
        "activateChamberTemp": False,
        "nozzleFirstLayer": 255,
        "nozzleOtherLayers": 255,
        "bedFirstLayer": 70,
        "bedOtherLayers": 70
    },
    "Bambu ABS": {
        "type": "ABS",
        "diameter": 1.75,
        "softeningTemp": 100,
        "idleTemp": 0,
        "minNozzleTemp": 240,
        "maxNozzleTemp": 280,
        "enablePressureAdvance": False,
        "chamberTemp": 90,
        "activateChamberTemp": False,
        "nozzleFirstLayer": 270,
        "nozzleOtherLayers": 270,
        "bedFirstLayer": 90,
        "bedOtherLayers": 90
    },
    "Bambu TPU 95A": {
        "type": "TPU",
        "diameter": 1.75,
        "softeningTemp": 50,
        "idleTemp": 0,
        "minNozzleTemp": 200,
        "maxNozzleTemp": 250,
        "enablePressureAdvance": False,
        "chamberTemp": 0,
        "activateChamberTemp": False,
        "nozzleFirstLayer": 240,
        "nozzleOtherLayers": 240,
        "bedFirstLayer": 35,
        "bedOtherLayers": 35
    }
}

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, 'r') as f:
                loaded = json.load(f)
                for k, v in DEFAULT_PROFILES.items():
                    if k not in loaded:
                        loaded[k] = v
                return loaded
        except Exception:
            pass
    return dict(DEFAULT_PROFILES)

def save_profiles():
    with open(PROFILES_FILE, 'w') as f:
        json.dump(filament_profiles, f, indent=4)

filament_profiles = load_profiles()
current_profile_name = list(filament_profiles.keys())[0]

""" GLOBAL VARIABLES """
# Geometry Action Variables
translateX = 0.0
translateY = 0.0
translateZ = 0.0
rotateX = 0.0
rotateY = 0.0
rotateZ = 0.0
scaleFactor = 100.0

init_prof = filament_profiles[current_profile_name]

filamentType = init_prof["type"]
filamentDiameter = init_prof["diameter"]
softeningTemp = init_prof["softeningTemp"]
idleTemp = init_prof["idleTemp"]
minNozzleTemp = init_prof["minNozzleTemp"]
maxNozzleTemp = init_prof["maxNozzleTemp"]
enablePressureAdvance = init_prof["enablePressureAdvance"]
chamberTemp = init_prof["chamberTemp"]
activateChamberTemp = init_prof["activateChamberTemp"]
nozzleFirstLayer = init_prof["nozzleFirstLayer"]
nozzleOtherLayers = init_prof["nozzleOtherLayers"]
bedFirstLayer = init_prof["bedFirstLayer"]
bedOtherLayers = init_prof["bedOtherLayers"]

# Backwards compatibility globals
nozzleTemp = nozzleOtherLayers
initialNozzleTemp = nozzleFirstLayer
bedTemp = bedOtherLayers
initialBedTemp = bedFirstLayer
infillPercentage = 20.0
shellThickness = 3
layerHeight = 0.3
printSpeed = 100.0
initialPrintSpeed = printSpeed - 50.0
travelSpeed = 150.0
initialTravelSpeed = travelSpeed - 50.0
enableZHop = True
enableRetraction = True
retractionDistance = 1.0
retractionSpeed = 20.0
enableSupports = False
enableBrim = False

buildPlateBounds = [-150, 150]
zBounds = [0, 300]
rotateBounds = [-720, 720]
scaleBounds = [1, 1000]

bannerHeight = 80
baseGridRight = 450
baseGridTop = 720 - bannerHeight

numSlicingDirections = 1
maxSlicingDirections = 20
startingPositions = [[0.0, 0.0, 0.0]]   # [xPosition, yPosition, zPosition]
directions = [[0.0, 0.0]]               # [theta, phi]
NANs = ["", "-", ".", "-."]

widgetBufferRight = 20
widgetBufferVertical = 10
widgetHeightSpacing = 40
popUpWidgetHeightSpacing = 35

""" WIDGET FUNCTIONS """

def cycle_decks(width, height):  # This cycles through all deck states for all decks so that the visual artifacts don't appear in the lower left corner of the window. This is basically a band-aid for an anomalous problem with glooey/pyglet
    for state in r0GeometryActionDeck.known_states:
        set_geometry_action_deck_states(state)
    set_geometry_action_deck_states(geometryActionState)
    geometryActionBackgroundDeck.set_state(geometryActionBackgroundState)

    for state in r0c0SettingsDeck.known_states:
        set_settings_deck_states(state)
    set_settings_deck_states(settingsState)

def set_geometry_action_deck_states(currentState):
    r0GeometryActionDeck.set_state(currentState)
    r2c0GeometryActionDeck.set_state(currentState)
    r2c1GeometryActionDeck.set_state(currentState)
    r3c0GeometryActionDeck.set_state(currentState)
    r3c1GeometryActionDeck.set_state(currentState)
    r4c0GeometryActionDeck.set_state(currentState)
    r4c1GeometryActionDeck.set_state(currentState)

def set_settings_deck_states(currentState):
    for state in r0c0SettingsDeck.known_states:
        r0c0SettingsDeck.set_state(state)
        r0c1SettingsDeck.set_state(state)
        r1c0SettingsDeck.set_state(state)
        r1c1SettingsDeck.set_state(state)
        r2c0SettingsDeck.set_state(state)
        r2c1SettingsDeck.set_state(state)
        r3c0SettingsDeck.set_state(state)
        r3c1SettingsDeck.set_state(state)
        r4c0SettingsDeck.set_state(state)
        r4c1SettingsDeck.set_state(state)
        r5c0SettingsDeck.set_state(state)
        r5c1SettingsDeck.set_state(state)
        r6c0SettingsDeck.set_state(state)
        r6c1SettingsDeck.set_state(state)
        r7c0SettingsDeck.set_state(state)
        r7c1SettingsDeck.set_state(state)
        r8c0SettingsDeck.set_state(state)
        r8c1SettingsDeck.set_state(state)
        r9c0SettingsDeck.set_state(state)
        r9c1SettingsDeck.set_state(state)
        r10c0SettingsDeck.set_state(state)
        r10c1SettingsDeck.set_state(state)
        r11c0SettingsDeck.set_state(state)
        r11c1SettingsDeck.set_state(state)
        r12c0SettingsDeck.set_state(state)
        r12c1SettingsDeck.set_state(state)
        r13c0SettingsDeck.set_state(state)
        r13c1SettingsDeck.set_state(state)
        r14c0SettingsDeck.set_state(state)
        r14c1SettingsDeck.set_state(state)
    
    currentState = R_optionMode.currentlyChecked.lower()
    
    r0c0SettingsDeck.set_state(currentState)
    r0c1SettingsDeck.set_state(currentState)
    r1c0SettingsDeck.set_state(currentState)
    r1c1SettingsDeck.set_state(currentState)
    r2c0SettingsDeck.set_state(currentState)
    r2c1SettingsDeck.set_state(currentState)
    r3c0SettingsDeck.set_state(currentState)
    r3c1SettingsDeck.set_state(currentState)
    r4c0SettingsDeck.set_state(currentState)
    r4c1SettingsDeck.set_state(currentState)
    r5c0SettingsDeck.set_state(currentState)
    r5c1SettingsDeck.set_state(currentState)
    r6c0SettingsDeck.set_state(currentState)
    r6c1SettingsDeck.set_state(currentState)
    r7c0SettingsDeck.set_state(currentState)
    r7c1SettingsDeck.set_state(currentState)
    r8c0SettingsDeck.set_state(currentState)
    r8c1SettingsDeck.set_state(currentState)
    r9c0SettingsDeck.set_state(currentState)
    r9c1SettingsDeck.set_state(currentState)
    r10c0SettingsDeck.set_state(currentState)
    r10c1SettingsDeck.set_state(currentState)
    r11c0SettingsDeck.set_state(currentState)
    r11c1SettingsDeck.set_state(currentState)
    r12c0SettingsDeck.set_state(currentState)
    r12c1SettingsDeck.set_state(currentState)
    r13c0SettingsDeck.set_state(currentState)
    r13c1SettingsDeck.set_state(currentState)
    r14c0SettingsDeck.set_state(currentState)
    r14c1SettingsDeck.set_state(currentState)

transform3DList = None
adhesionList = None
shellRingsListList = None
optimizedInternalInfills = None
optimizedSolidInfills = None
optimizedSupportInfills = None

chunk_transform3DList = None
chunk_shellRingsListList = None
chunk_optimizedInternalInfills = None
chunk_optimizedSolidInfills = None

def disable_all_settings():
    r0c1SettingsDeck.get_widget("material").set_disabled(True)
    r0c1SettingsDeck.get_widget("strength").set_disabled(True)
    r0c1SettingsDeck.get_widget("resolution").set_disabled(True)
    r0c1SettingsDeck.get_widget("movement").set_disabled(True)
    r0c1SettingsDeck.get_widget("supports").set_disabled(True)
    r0c1SettingsDeck.get_widget("adhesion").set_disabled(True)
    
    r1c1SettingsDeck.get_widget("material").set_disabled(True)
    r1c1SettingsDeck.get_widget("strength").set_disabled(True)
    r1c1SettingsDeck.get_widget("movement").set_disabled(True)
    
    r2c1SettingsDeck.get_widget("material").set_disabled(True)
    r2c1SettingsDeck.get_widget("movement").set_disabled(True)
    
    r3c1SettingsDeck.get_widget("material").set_disabled(True)
    r3c1SettingsDeck.get_widget("movement").set_disabled(True)
    
    r4c1SettingsDeck.get_widget("material").set_disabled(True)
    r4c1SettingsDeck.get_widget("movement").set_disabled(True)
    
    r5c1SettingsDeck.get_widget("material").set_disabled(True)
    r5c1SettingsDeck.get_widget("movement").set_disabled(True)
    
    r6c1SettingsDeck.get_widget("material").set_disabled(True)
    r6c1SettingsDeck.get_widget("movement").get_widget("enabled").set_disabled(True)
    
    r7c1SettingsDeck.get_widget("material").set_disabled(True)
    r7c1SettingsDeck.get_widget("movement").get_widget("enabled").set_disabled(True)

    r8c1SettingsDeck.get_widget("material").set_disabled(True)
    r9c1SettingsDeck.get_widget("material").set_disabled(True)
    r10c1SettingsDeck.get_widget("material").set_disabled(True)
    r11c1SettingsDeck.get_widget("material").set_disabled(True)
    r12c1SettingsDeck.get_widget("material").set_disabled(True)
    r13c1SettingsDeck.get_widget("material").set_disabled(True)
    r14c1SettingsDeck.get_widget("material").set_disabled(True)

def ungray_all_settings_widgets():
    r0c1SettingsDeck.get_widget("material").set_disabled(False)
    r0c1SettingsDeck.get_widget("strength").set_disabled(False)
    r0c1SettingsDeck.get_widget("resolution").set_disabled(False)
    r0c1SettingsDeck.get_widget("movement").set_disabled(False)
    r0c1SettingsDeck.get_widget("supports").set_disabled(False)
    r0c1SettingsDeck.get_widget("adhesion").set_disabled(False)
    
    r1c1SettingsDeck.get_widget("material").set_disabled(False)
    r1c1SettingsDeck.get_widget("strength").set_disabled(False)
    r1c1SettingsDeck.get_widget("movement").set_disabled(False)
    
    r2c1SettingsDeck.get_widget("material").set_disabled(False)
    r2c1SettingsDeck.get_widget("movement").set_disabled(False)
    
    r3c1SettingsDeck.get_widget("material").set_disabled(False)
    r3c1SettingsDeck.get_widget("movement").set_disabled(False)
    
    r4c1SettingsDeck.get_widget("material").set_disabled(False)
    r4c1SettingsDeck.get_widget("movement").set_disabled(False)
    
    r5c1SettingsDeck.get_widget("material").set_disabled(False)
    r5c1SettingsDeck.get_widget("movement").set_disabled(False)
    
    r6c1SettingsDeck.get_widget("material").set_disabled(False)
    r6c1SettingsDeck.get_widget("movement").get_widget("enabled").set_disabled(False)
    
    r7c1SettingsDeck.get_widget("material").set_disabled(False)
    r7c1SettingsDeck.get_widget("movement").get_widget("enabled").set_disabled(False)

    r8c1SettingsDeck.get_widget("material").set_disabled(False)
    r9c1SettingsDeck.get_widget("material").set_disabled(False)
    r10c1SettingsDeck.get_widget("material").set_disabled(False)
    r11c1SettingsDeck.get_widget("material").set_disabled(False)
    r12c1SettingsDeck.get_widget("material").set_disabled(False)
    r13c1SettingsDeck.get_widget("material").set_disabled(False)
    r14c1SettingsDeck.get_disabled(False)

def toggle_viewMode_layout(parentWidget):
    global \
        transform3DList, \
        adhesionList, \
        shellRingsListList, \
        optimizedInternalInfills, \
        optimizedSolidInfills, \
        optimizedSupportInfills, \
        chunk_transform3DList, \
        chunk_shellRingsListList, \
        chunk_optimizedInternalInfills, \
        chunk_optimizedSolidInfills
    currentViewMode = parentWidget.currentlyChecked # Prepare or Preview Mode
    printMode = R_viewMode.D_variables["printMode"]
    if currentViewMode == "Preview" and (transform3DList is not None or chunk_transform3DList is not None):

        """ Turning slice data into renderable vertices """
        if R_viewMode.preRendered == False: # If the toolpaths haven't been processed for rendering yet, process them, otherwise, don't do anything
                
            if printMode == "3-Axis Mode":
                adhesionPathsCombined, shellPathsCombined, internalInfillPathsCombined, solidInfillPathsCombined, supportInfillPathsCombined = convert_slice_data_to_renderable_vertices(transform3DList, adhesionList, shellRingsListList, optimizedInternalInfills, optimizedSolidInfills, optimizedSupportInfills)
            elif printMode == "5-Axis Mode":
                # Assuming 5-axis doesn't have supports yet, so pass None
                adhesionPathsCombined, shellPathsCombined, internalInfillPathsCombined, solidInfillPathsCombined, supportInfillPathsCombined = convert_slice_data_to_renderable_vertices(chunk_transform3DList, adhesionList, chunk_shellRingsListList, chunk_optimizedInternalInfills, chunk_optimizedSolidInfills, None)

            R_viewMode.D_variables["adhesionPathsCombined"] = adhesionPathsCombined
            R_viewMode.D_variables["shellPathsCombined"] = shellPathsCombined
            R_viewMode.D_variables["internalInfillPathsCombined"] = internalInfillPathsCombined
            R_viewMode.D_variables["solidInfillPathsCombined"] = solidInfillPathsCombined
            R_viewMode.D_variables["supportInfillPathsCombined"] = supportInfillPathsCombined
            

        elif R_viewMode.preRendered == True:
            sliceButtonDeck.set_state("B_saveGcodeAs")
            
    elif currentViewMode == "Prepare":  # If the user switches to Prepare mode, reenable the slice button
        enable_all_settings()           # Reenable all settings
        if R_viewMode.preRendered == True:
            sliceButtonDeck.set_state("B_slice")

def toggle_left_toolbar_layout(parentWidget):
    global geometryActionState, geometryActionBackgroundState
    unhide_geometry_action_pop_up_window()
    selectedAction = parentWidget.currentlyChecked
    if selectedAction == "Translate":
        currentState = "translate"
        geometryActionBackgroundState = "base"

    elif selectedAction == "Rotate":
        currentState = "rotate"
        geometryActionBackgroundState = "base"

    elif selectedAction == "Scale":
        currentState = "scale"
        geometryActionBackgroundState = "scale"

    elif selectedAction == "Deactivated":
        currentState = "blank"
        geometryActionBackgroundState = "deactivated"

    geometryActionBackgroundDeck.set_state(geometryActionBackgroundState)
    geometryActionState = currentState
    set_geometry_action_deck_states(currentState)

def unhide_geometry_action_pop_up_window():
    r0GeometryActionDeck.unhide()

def hide_geometry_action_pop_up_window():
    geometryActionBackgroundDeck.set_state("deactivated")
    set_geometry_action_deck_states("blank")

def toggle_printMode_layout(parentWidget):
    printMode = parentWidget.currentlyChecked
    if printMode == "3-Axis Mode":
        enable_3_axis_mode()
    elif printMode == "5-Axis Mode":
        enable_5_axis_mode()

def toggle_settings_layout(parentWidget):
    global settingsState
    update_values()
    selectedMenu = parentWidget.currentlyChecked
    if selectedMenu == "Material":
        currentState = "material"

    elif selectedMenu == "Strength":
        currentState = "strength"

    elif selectedMenu == "Resolution":
        currentState = "resolution"

    elif selectedMenu == "Movement":
        currentState = "movement"

    elif selectedMenu == "Supports":
        currentState = "supports"

    elif selectedMenu == "Adhesion":
        currentState = "adhesion"

    settingsState = currentState
    set_settings_deck_states(currentState)

def update_mode_placeholder(parentWidget):
    mode = parentWidget.currentlyChecked

def apply_placeholder():
    pass

def update_values():
    global buildPlateShape, buildPlateX, buildPlateY, buildPlateZ
    global nozzleTemp, E_nozzleTemp, initialNozzleTemp, E_initialNozzleTemp, bedTemp, E_bedTemp, initialBedTemp, E_initialBedTemp
    global infillPercentage, E_infillPercentage, shellThickness, E_shellThickness
    global layerHeight, E_layerHeight
    global \
        printSpeed, \
        E_printSpeed, \
        initialPrintSpeed, \
        E_initialPrintSpeed, \
        travelSpeed, \
        E_travelSpeed, \
        initialTravelSpeed, \
        E_initialTravelSpeed, \
        enableZHop, \
        C_enableZHop, \
        enableRetraction, \
        C_enableRetraction, \
        retractionDistance, \
        E_retractionDistance, \
        retractionSpeed, \
        E_retractionSpeed
    global enableSupports, C_enableSupports
    global enableBrim, C_enableBrim
    global enableNonPlanarTopSurfaces, nozzleTipDiameter, nozzleShoulderWidth, nozzleAngle
    try:
        filamentDiameter = r3c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        softeningTemp = r4c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        idleTemp = r5c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        minNozzleTemp = r6c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        maxNozzleTemp = r7c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        enablePressureAdvance = r8c1SettingsDeck.get_widget("material").is_checked
        chamberTemp = r9c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        activateChamberTemp = r10c1SettingsDeck.get_widget("material").is_checked
        nozzleFirstLayer = r11c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        nozzleOtherLayers = r12c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        bedFirstLayer = r13c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        bedOtherLayers = r14c1SettingsDeck.get_widget("material").entryBoxEditableLabel.get_text()
        
        # update backwards compatibility fields
        nozzleTemp = nozzleOtherLayers
        initialNozzleTemp = nozzleFirstLayer
        bedTemp = bedOtherLayers
        initialBedTemp = bedFirstLayer

        try:
            buildPlateShape = plateShapeDropdown.options[plateShapeDropdown.currentSelection]
            buildPlateX = float(r2c1PlateEntry.entryBoxEditableLabel.get_text())
            if buildPlateShape == "circular":
                buildPlateY = buildPlateX
            else:
                buildPlateY = float(r3c1PlateEntry.entryBoxEditableLabel.get_text())
            buildPlateZ = float(r4c1PlateEntry.entryBoxEditableLabel.get_text())
            save_printer_config()
        except Exception as e:
            pass
        
        # Auto-save changes to the profile
        prof = filament_profiles[current_profile_name]
        prof["diameter"] = float(filamentDiameter)
        prof["softeningTemp"] = float(softeningTemp)
        prof["idleTemp"] = float(idleTemp)
        prof["minNozzleTemp"] = float(minNozzleTemp)
        prof["maxNozzleTemp"] = float(maxNozzleTemp)
        prof["enablePressureAdvance"] = enablePressureAdvance
        prof["chamberTemp"] = float(chamberTemp)
        prof["activateChamberTemp"] = activateChamberTemp
        prof["nozzleFirstLayer"] = float(nozzleFirstLayer)
        prof["nozzleOtherLayers"] = float(nozzleOtherLayers)
        prof["bedFirstLayer"] = float(bedFirstLayer)
        prof["bedOtherLayers"] = float(bedOtherLayers)
        save_profiles()
    except:
        pass
    try:
        infillPercentage = r0c1SettingsDeck.get_widget( "strength").entryBoxEditableLabel.get_text()
        shellThickness = r1c1SettingsDeck.get_widget("strength").entryBoxEditableLabel.get_text()
    except:
        pass
    try:
        layerHeight = r0c1SettingsDeck.get_widget("resolution").entryBoxEditableLabel.get_text()
    except:
        pass
    try:
        printSpeed = r0c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.get_text()
        initialPrintSpeed = r1c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.get_text()
        travelSpeed = r2c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.get_text()
        initialTravelSpeed = r3c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.get_text()
        enableZHop = r4c1SettingsDeck.get_widget("movement").is_checked
        enableRetraction = r5c1SettingsDeck.get_widget("movement").is_checked
    except:
        pass
    try:
        retractionDistance = r6c1SettingsDeck.get_widget("movement").get_widget("enabled").entryBoxEditableLabel.get_text()
        retractionSpeed = r7c1SettingsDeck.get_widget("movement").get_widget("enabled").entryBoxEditableLabel.get_text()
    except:
        pass
    try:
        enableSupports = r0c1SettingsDeck.get_widget("supports").is_checked
    except:
        pass
    try:
        enableBrim = r0c1SettingsDeck.get_widget("adhesion").is_checked
    except:
        pass
        
    # Backend hooks for Non-Planar Slicing
    try:
        enableNonPlanarTopSurfaces = r1c1SettingsDeck.get_widget("resolution").is_checked
    except:
        enableNonPlanarTopSurfaces = False 
    
    try:
        nozzleTipDiameter = 0.4
        nozzleShoulderWidth = 2.0
        nozzleAngle = 45.0
    except:
        pass

def print_slicing_parameters():
    print("nozzleTemp:", nozzleTemp, "\n")
    print("initialNozzleTemp:", initialNozzleTemp, "\n")
    print("bedTemp:", bedTemp, "\n")
    print("initialBedTemp:", initialBedTemp, "\n")
    print("infillPercentage:", infillPercentage, "\n")
    print("shellThickness:", shellThickness, "\n")
    print("layerHeight:", layerHeight, "\n")
    print("printSpeed:", printSpeed, "\n")
    print("initialPrintSpeed:", initialPrintSpeed, "\n")
    print("travelSpeed:", travelSpeed, "\n")
    print("initialTravelSpeed:", initialTravelSpeed, "\n")
    print("enableZHop:", enableZHop, "\n")
    print("enableRetraction:", enableRetraction, "\n")
    if enableRetraction == True:
        print("Retraction Distance:", retractionDistance, "\n")
        print("Retraction Speed:", retractionSpeed, "\n")
    print("enableSupports:", enableSupports, "\n")
    print("enableBrim:", enableBrim, "\n")
    print("enableNonPlanarTopSurfaces:", enableNonPlanarTopSurfaces, "\n")
    print("nozzleTipDiameter:", nozzleTipDiameter, "\n")
    print("nozzleShoulderWidth:", nozzleShoulderWidth, "\n")
    print("nozzleAngle:", nozzleAngle, "\n")

def set_sliceFlag(args):
    sliceButtonDeck.get_widget("B_slice").sliceFlag = True

project_transforms = None

def export_project_settings():
    update_values()
    settings = {
        "nozzleTemp": nozzleTemp,
        "initialNozzleTemp": initialNozzleTemp,
        "bedTemp": bedTemp,
        "initialBedTemp": initialBedTemp,
        "infillPercentage": infillPercentage,
        "shellThickness": shellThickness,
        "layerHeight": layerHeight,
        "printSpeed": printSpeed,
        "initialPrintSpeed": initialPrintSpeed,
        "travelSpeed": travelSpeed,
        "initialTravelSpeed": initialTravelSpeed,
        "enableZHop": enableZHop,
        "enableRetraction": enableRetraction,
        "retractionDistance": retractionDistance,
        "retractionSpeed": retractionSpeed,
        "enableSupports": enableSupports,
        "enableBrim": enableBrim,
        "enableNonPlanarTopSurfaces": enableNonPlanarTopSurfaces,
        "nozzleTipDiameter": nozzleTipDiameter,
        "nozzleShoulderWidth": nozzleShoulderWidth,
        "nozzleAngle": nozzleAngle,
    }
    
    import __main__ as slicer_main
    transforms = {}
    for key in slicer_main.Graphics_Window.D_finalPositions.keys():
        transforms[str(key)] = {
            "finalPosition": [float(x) for x in slicer_main.Graphics_Window.D_finalPositions[key]],
            "finalScale": [float(x) for x in slicer_main.Graphics_Window.D_finalScales[key]],
            "finalRotation": slicer_main.Graphics_Window.D_finalRotations[key].tolist()
        }
    return {"settings": settings, "transforms": transforms}

def save_project(*args):
    try:
        desktopDirectory = os.path.join(os.path.expanduser("~"), "Desktop")
        newFile = filedialog.asksaveasfilename(initialdir=desktopDirectory, title="Save Project As...", defaultextension=".3mf", filetypes=(("3MF Project File", "*.3mf"),))
        if not newFile:
            return
            
        import json
        import trimesh
        import __main__ as slicer_main
        import zipfile
        import io
        import numpy as np
        
        if not slicer_main.Render_Model.D_stlMeshes:
            print("Cannot save an empty project!")
            return
            
        scene = trimesh.Scene()
        
        for key, mesh in slicer_main.Render_Model.D_stlMeshes.items():
            translation = slicer_main.Graphics_Window.D_finalPositions[key]
            scale = slicer_main.Graphics_Window.D_finalScales[key]
            R = slicer_main.Graphics_Window.D_finalRotations[key] # 4x4 numpy array
            
            M_translate = trimesh.transformations.translation_matrix(translation)
            S = np.diag([scale[0], scale[1], scale[2], 1.0])
            
            # The rotation matrix is already a 4x4 matrix
            M = trimesh.transformations.concatenate_matrices(M_translate, R, S)
            scene.add_geometry(mesh, geom_name=str(key), transform=M)
            
        raw_3mf_bytes = trimesh.exchange.threemf.export_3MF(scene)
        settings_json = json.dumps(export_project_settings(), indent=4)
        
        zip_buffer = io.BytesIO(raw_3mf_bytes)
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as z:
            z.writestr("Metadata/fractal_cortex_settings.json", settings_json)
            
        with open(newFile, "wb") as f:
            f.write(zip_buffer.getvalue())
            
        print(f"Project saved to {newFile}")
    except Exception as e:
        import traceback
        traceback.print_exc()

def import_project_settings(settings_json_str):
    import json
    data = json.loads(settings_json_str)
    settings = data.get("settings", {})
    transforms = data.get("transforms", {})
    
    if "nozzleTemp" in settings: r0c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(settings["nozzleTemp"]))
    if "initialNozzleTemp" in settings: r1c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(settings["initialNozzleTemp"]))
    if "bedTemp" in settings: r2c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(settings["bedTemp"]))
    if "initialBedTemp" in settings: r3c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(settings["initialBedTemp"]))
    
    if "infillPercentage" in settings: r0c1SettingsDeck.get_widget("strength").entryBoxEditableLabel.set_text(str(settings["infillPercentage"]))
    if "shellThickness" in settings: r1c1SettingsDeck.get_widget("strength").entryBoxEditableLabel.set_text(str(settings["shellThickness"]))
    
    if "layerHeight" in settings: r0c1SettingsDeck.get_widget("resolution").entryBoxEditableLabel.set_text(str(settings["layerHeight"]))
    
    if "printSpeed" in settings: r0c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.set_text(str(settings["printSpeed"]))
    if "initialPrintSpeed" in settings: r1c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.set_text(str(settings["initialPrintSpeed"]))
    if "travelSpeed" in settings: r2c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.set_text(str(settings["travelSpeed"]))
    if "initialTravelSpeed" in settings: r3c1SettingsDeck.get_widget("movement").entryBoxEditableLabel.set_text(str(settings["initialTravelSpeed"]))
    
    if "enableZHop" in settings:
        w = r4c1SettingsDeck.get_widget("movement")
        if settings["enableZHop"] != w.is_checked: w.toggle()
    if "enableRetraction" in settings:
        w = r5c1SettingsDeck.get_widget("movement")
        if settings["enableRetraction"] != w.is_checked: w.toggle()
        
    if "retractionDistance" in settings: r6c1SettingsDeck.get_widget("movement").get_widget("enabled").entryBoxEditableLabel.set_text(str(settings["retractionDistance"]))
    if "retractionSpeed" in settings: r7c1SettingsDeck.get_widget("movement").get_widget("enabled").entryBoxEditableLabel.set_text(str(settings["retractionSpeed"]))
    
    if "enableSupports" in settings:
        w = r0c1SettingsDeck.get_widget("supports")
        if settings["enableSupports"] != w.is_checked: w.toggle()
    if "enableBrim" in settings:
        w = r0c1SettingsDeck.get_widget("adhesion")
        if settings["enableBrim"] != w.is_checked: w.toggle()
        
    if "enableNonPlanarTopSurfaces" in settings:
        w = r1c1SettingsDeck.get_widget("resolution")
        if settings["enableNonPlanarTopSurfaces"] != w.is_checked: w.toggle()
    
    update_values()
    
    global project_transforms
    project_transforms = transforms

def slice_function(meshData):
    global \
        printSettings, \
        transform3DList, \
        adhesionList, \
        shellRingsListList, \
        optimizedInternalInfills, \
        optimizedSolidInfills, \
        optimizedSupportInfills, \
        chunk_transform3DList, \
        chunk_shellRingsListList, \
        chunk_optimizedInternalInfills, \
        chunk_optimizedSolidInfills
    update_values()
    print_slicing_parameters() # Print all slicing parameters
    printSettings = [
        nozzleTemp,
        initialNozzleTemp,
        bedTemp,
        initialBedTemp,
        infillPercentage,
        shellThickness,
        layerHeight,
        printSpeed,
        initialPrintSpeed,
        travelSpeed,
        initialTravelSpeed,
        enableZHop,
        enableRetraction,
        retractionDistance,
        retractionSpeed,
        enableSupports,
        enableBrim,
        enableNonPlanarTopSurfaces,
        nozzleTipDiameter,
        nozzleShoulderWidth,
        nozzleAngle,
    ]

    if sliceButtonDeck.get_widget("B_slice").argsList[0][0] != []: # Only proceed with slicing if there are STL's to slice
        printMode = R_printMode.currentlyChecked

        if printMode == "3-Axis Mode":
            (
                transform3DList,
                adhesionList,
                shellRingsListList,
                optimizedInternalInfills,
                optimizedSolidInfills,
                optimizedSupportInfills,
            ) = slice_in_3_axes(printSettings, meshData)            

        elif printMode == "5-Axis Mode":
            numSlicingDirections = R_optionMode.D_variables['numSlicingDirections']
            startingPositions = R_optionMode.D_variables['startingPositions']
            directions = R_optionMode.D_variables['directions']
            slicingDirections = [numSlicingDirections, startingPositions, directions]
            
            chunk_transform3DList, adhesionList, chunk_shellRingsListList, chunk_optimizedInternalInfills, chunk_optimizedSolidInfills = slice_in_5_axes(printSettings, meshData, slicingDirections)

        sliceButtonDeck.get_widget("B_slice").clearVBOs = True  # Tracks if there is new slice data (Used for determining when to reset toolpath VBO's for "Preview" mode
        R_viewMode.preRendered = False                          # Next time the "Preview" button is selected, toolpaths need to be regenerated
        R_viewMode.set_disabled(False)

def save_gcode_as(fileName):
    global \
        printSettings, \
        transform3DList, \
        adhesionList, \
        shellRingsListList, \
        optimizedInternalInfills, \
        optimizedSolidInfills, \
        chunk_transform3DList, \
        chunk_shellRingsListList, \
        chunk_optimizedInternalInfills, \
        chunk_optimizedSolidInfills
    print("Save G-Code As...")
    desktopDirectory = os.path.join(os.path.expanduser("~"), "Desktop")
    if len(fileName) == 1:
        fileName_start_index = fileName[0].rfind("/") + 1
        fileName_end_index = fileName[0].index(".stl")
        stlFileName = fileName[0][fileName_start_index:fileName_end_index]
    else:
        stlFileName = "new_file"

    newFile = filedialog.asksaveasfilename(initialdir=desktopDirectory, title="Save Gcode File As...", defaultextension=".gcode", filetypes=(("gcode File", "*.gcode*"), ("Text Document", "*.txt")), initialfile=stlFileName)

    print(newFile)

    if newFile:  # Only write the gcode if the user hits "save". Otherwise, the user canceled out of the menu
        savedFileName_start_index = newFile.rfind("/") + 1
        savedFileName_extension = newFile[newFile.rfind(".") :]
        savedFileName_end_index = newFile.index(savedFileName_extension)
        savedFileName = newFile[savedFileName_start_index:savedFileName_end_index]

        printMode = R_printMode.currentlyChecked

        if printMode == "3-Axis Mode":
            write_3_axis_gcode(
                newFile,
                savedFileName,
                printSettings,
                transform3DList,
                adhesionList,
                shellRingsListList,
                optimizedInternalInfills,
                optimizedSolidInfills,
                optimizedSupportInfills
            )
        elif printMode == "5-Axis Mode":
            startingPositions = R_optionMode.D_variables['startingPositions']
            directions = R_optionMode.D_variables['directions']
            
            write_5_axis_gcode(
                newFile,
                savedFileName,
                printSettings,
                startingPositions,
                directions,
                chunk_transform3DList,
                adhesionList,
                chunk_shellRingsListList,
                chunk_optimizedInternalInfills,
                chunk_optimizedSolidInfills
            )

fileKey = 0  # Keeps track of which file has been opened
def select_file():      # Called when the user clicks the file select button
    global selectedNewFile, fileKey
    desktopDirectory = os.path.join(
        os.path.expanduser("~"), "Desktop"
    )
    fileName = filedialog.askopenfilename(
        initialdir=desktopDirectory,
        title="Select a Mesh File",
        filetypes=(("Mesh Files", "*.stl;*.3mf"), ("All Files", "*.*")),
    )

    if fileName:        # If a file has been selected
        is_project = False
        if fileName.endswith('.3mf'):
            import zipfile
            try:
                with zipfile.ZipFile(fileName, 'r') as z:
                    if "Metadata/fractal_cortex_settings.json" in z.namelist():
                        is_project = True
                        settings_str = z.read("Metadata/fractal_cortex_settings.json").decode('utf-8')
                        import_project_settings(settings_str)
            except:
                pass
                
        if is_project:
            import trimesh
            import __main__ as slicer_main
            
            slicer_main.Graphics_Window.D_finalPositions.clear()
            slicer_main.Graphics_Window.D_sizeHistory.clear()
            slicer_main.Graphics_Window.D_axisRotationHistory.clear()
            slicer_main.Graphics_Window.D_finalRotations.clear()
            slicer_main.Graphics_Window.D_finalScales.clear()
            slicer_main.Render_Model.D_stlMeshes.clear()
            B_selectFile.D_variables.clear()
            slicer_main.L_loadedIndices.clear()
            
            global fileKey
            fileKey = 0
            
            scene = trimesh.load(fileName)
            if isinstance(scene, trimesh.Scene):
                for node_name in scene.graph.nodes_geometry:
                    geom_name = scene.graph.get(node_name)[1]
                    mesh = scene.geometry[geom_name]
                    try:
                        k = int(geom_name)
                    except:
                        k = fileKey
                        
                    slicer_main.Graphics_Window.D_finalPositions[k] = [0.0, 0.0, 0.0]
                    slicer_main.Graphics_Window.D_sizeHistory[k] = [[1.0, 1.0, 1.0]]
                    slicer_main.Graphics_Window.D_axisRotationHistory[k] = "X"
                    
                    global project_transforms
                    if project_transforms and str(k) in project_transforms:
                        t = project_transforms[str(k)]
                        slicer_main.Graphics_Window.D_finalPositions[k] = t["finalPosition"]
                        slicer_main.Graphics_Window.D_finalScales[k] = t["finalScale"]
                        
                        import numpy as np
                        rot = np.array(t["finalRotation"])
                        slicer_main.Graphics_Window.D_finalRotations[k] = rot
                        slicer_main.Graphics_Window.D_previousRotations[k] = rot
                        
                    B_selectFile.D_variables[k] = fileName
                    slicer_main.L_loadedIndices.append(k)
                    fileKey = max(fileKey, k) + 1
                    
            return fileName
            
        else:
            B_selectFile.D_variables[fileKey] = (
                fileName    # Add the filename to the list of selected files
            )
            fileKey += 1    # Update the fileKey
    return fileName

def checkSlicePlaneValidity():
    """Checks if any of the user-defined slice planes are oriented in "illegal" positions that would cause a collision between the bed and nozzle.
        If a slice plane is determined to cause a collision, this script raises a flag to stop the slicing process from continuing."""
    
    numSlicingDirections = R_optionMode.D_variables['numSlicingDirections']
    slicingDirections = list(range(int(numSlicingDirections)))
    startingPositions = R_optionMode.D_variables['startingPositions']
    directionsDeg = R_optionMode.D_variables['directions']
    directionsRad = [np.radians(anglePair).tolist() for anglePair in directionsDeg]
    meshSections = []
    meshData = B_numSlicingDirections.D_variables['meshData']

    numObjects = len(meshData[0])

    if numObjects > 1:  # If there are multiple STLs, merge all STLs into one big STL
        importedMeshList = list(meshData[1].values())
        importedMergedMesh = trimesh.util.concatenate(importedMeshList)
        importedMesh = importedMergedMesh

    elif numObjects == 1:  # There is only one STL
        fileKey = meshData[0][0]
        importedMesh = meshData[1][fileKey]

    mesh = importedMesh.copy()  # Makes a local copy of the imported mesh so it can be pickleable

    def spherical_to_normal(theta, phi):
        """
        Convert spherical coordinates to a normal vector.
        """
        nx = np.sin(theta) * np.cos(phi)
        ny = np.sin(theta) * np.sin(phi)
        nz = np.cos(theta)
        
        return np.array([nx, ny, nz])

    '''
    First, get cross Sections of where each slice plane intersects with the STL mesh
    '''
    for k in slicingDirections:
        if k > 0: # The initial sliceplane is automatically safe since slicing happens perpendicular to the bed
            start = startingPositions[k]
            normal = spherical_to_normal(*directionsRad[k])
            meshSections.append(mesh.section(plane_normal=normal, plane_origin=start))

    '''
    Second, get points from mesh Sections and extract their Z values
    '''
    sectionPoints = [section.vertices for section in meshSections]
    sectionZValuesBySlicePlane = [[point[2] for point in section] for section in sectionPoints]

    '''
    Third, Calculate the distance between each point to the build surface given theta (bed tilt angle) and each point's Z value
    '''
    minAcceptableBedToNozzleClearance = 12.0                                            # Too much closer than this would result in a collision (if the bed was tilted at 90 degrees)
    D_slicePlaneValidity = {}
    for slicePlane in range(len(sectionZValuesBySlicePlane)):                           # For each slicePlane, get the ZValues and theta value
        ZValues = sectionZValuesBySlicePlane[slicePlane]
        theta = directionsRad[slicePlane+1][0]
        D_slicePlaneValidity[str(slicePlane+1)] = []
        for z in ZValues:                                                               # For each point in the section, calculate the bed to nozzle distance to see if it's passable
            if round(theta, 2) == 0:                                                    # If the sliceplane is mostly pointing up, assume it is safe and also do this step to avoid dividing by zero later
                D_slicePlaneValidity[str(slicePlane+1)].append(True)
            else:                                                                       # For non-vertical slicing normals:
                if z <= minAcceptableBedToNozzleClearance:                              # Only calculate currentBedToNozzleDistance if this point's z value is less than minAcceptableBedToNozzleClearance 
                    currentBedToNozzleDistance = abs(z)/np.sin(theta)                   # We want this to be larger than 12.0 mm
                    if currentBedToNozzleDistance > minAcceptableBedToNozzleClearance:  # Valid (No collision)
                        D_slicePlaneValidity[str(slicePlane+1)].append(True)
                    else:                                                               # Invalid (Collision between bed and nozzle)
                        D_slicePlaneValidity[str(slicePlane+1)].append(False)
                else:                                                                   # If the z value of the point is greater than minAcceptableBedToNozzleClearance, it inherently won't cause a collision and does not require a calculation
                    D_slicePlaneValidity[str(slicePlane+1)].append(True)

    '''
    Lastly, process D_slicePlaneValidity so it shows True or False for a given sliceplane
    '''
    for key in D_slicePlaneValidity:
        if any(slicePlane is False for slicePlane in D_slicePlaneValidity[key]):
            D_slicePlaneValidity[key] = False
        else:
            D_slicePlaneValidity[key] = True

    validityCheck = [all([value for value in D_slicePlaneValidity.values()]), D_slicePlaneValidity]

    R_optionMode.D_variables['D_slicePlaneValidity'] = D_slicePlaneValidity
    return validityCheck

def set_numSlicingDirections():
    global numSlicingDirections, slicingDirectionList, startingPositions, directions, D_slicePlaneValidity
    numSlicingDirections = S_numSlicingDirections.entryBox.entryBoxEditableLabel.get_text()
    if numSlicingDirections in NANs:
        numSlicingDirections = 2
    def get_maxHeightOfAllSTLs():
        # Find the max height of the STL (or collection of STL's) to evenly space the startingPositions
        heights = []
        meshData = B_numSlicingDirections.D_variables['meshData']
        importedMeshList = list(meshData[1].values())
        for k in importedMeshList:
            heights.append(k.bounds[1][2])

        maxHeight = max(heights)
        return maxHeight

    maxHeight = get_maxHeightOfAllSTLs()
    verticalSpacing = float(maxHeight/int(numSlicingDirections))
    D_slicePlaneValidity = {}
    for k in range(int(numSlicingDirections)):
        D_slicePlaneValidity[str(k)] = True                                     # Initialize all sliceplanes as valid until proven otherwise
        
    for k in range(int(numSlicingDirections)-1):
        startingPositions.append([0.0, 0.0, verticalSpacing+k*verticalSpacing]) # Vertically space out slicing directions when initially spawned
    directions = [[0.0, 0.0]] * int(numSlicingDirections)
    slicingDirectionList = list(range(2, int(numSlicingDirections) + 1))        # List of slicing direction numbers starting at 2 and going until n

    R_optionMode.D_variables['numSlicingDirections'] = numSlicingDirections     # Update this so it can be retrieved from the main script
    R_optionMode.D_variables['startingPositions'] = startingPositions
    R_optionMode.D_variables['directions'] = directions
    R_optionMode.D_variables['D_slicePlaneValidity'] = D_slicePlaneValidity
    
    enable_5_axis_mode()

    update_current_selection()

def add_new_slicing_direction():
    global slicingDirectionList, startingPositions, directions, D_slicePlaneValidity
    if slicingDirectionList[-1] < maxSlicingDirections:
        newMaxValue = slicingDirectionList[-1] + 1
        lastZ = startingPositions[-1][2]
        startingPositions.append([0.0, 0.0, float(lastZ)+5.0])                                              # Spawn the next slicePlane slightly above the last one
        directions.append([0.0, 0.0])

        S_currentSlicingDirection.update_maxValue(newMaxValue)                                              # Update the size of slicingDirectionList
        slicingDirectionList = list(range(2, newMaxValue + 1))                                              # Update slicingDirectionList
        S_currentSlicingDirection.entryBox.entryBoxEditableLabel.set_text(str(slicingDirectionList[-1]))    # Set the current text to the last index

        D_slicePlaneValidity[str(newMaxValue-1)] = True
        
        update_current_selection()

        R_optionMode.D_variables['numSlicingDirections'] = newMaxValue # Update this so it can be retrieved from the main script

def remove_slicing_direction():
    global slicingDirectionList, startingPositions, directions, D_slicePlaneValidity
    if slicingDirectionList[-1] > 2:
        newMaxValue = slicingDirectionList[-1] - 1
        S_currentSlicingDirection.update_maxValue(newMaxValue)                                              # Update the size of slicingDirectionList
        slicingDirectionList.pop(-1)                                                                        # Update slicingDirectionList
        startingPositions.pop(-1)
        directions.pop(-1)

        S_currentSlicingDirection.entryBox.entryBoxEditableLabel.set_text(str(slicingDirectionList[-1]))    # Set the current text to the last index

        del D_slicePlaneValidity[str(newMaxValue)]
        
        update_current_selection()

        R_optionMode.D_variables['numSlicingDirections'] = newMaxValue                                      # Update this so it can be retrieved from the main script

def remove_all_slicing_directions():
    global numSlicingDirections, slicingDirectionList, startingPositions, directions, D_slicePlaneValidity
    numSlicingDirections = 1
    slicingDirectionList = []
    startingPositions = [[0.0, 0.0, 0.0]]
    directions = [[0.0, 0.0]]
    S_numSlicingDirections.entryBox.entryBoxEditableLabel.set_text(str(2))      # Reset the current text to 2
    S_currentSlicingDirection.entryBox.entryBoxEditableLabel.set_text(str(2))   # Reset the current text to 2
    slicingDirectionBoard.clear()                                               # This line makes it so that the units text doesn't appear in the lower left corner of the window

    D_slicePlaneValidity = {'0': True}

    R_optionMode.D_variables['numSlicingDirections'] = 1 # Update this so it can be retrieved from the main script
    R_optionMode.D_variables['startingPositions'] = [[0.0, 0.0, 0.0]]
    R_optionMode.D_variables['directions'] = [[0.0, 0.0]]
    
    enable_5_axis_mode()

def update_starting_positions():  # This is called every time the up or down button is pressed on a starting position spin box. This should also be called every time the text is updated on them
    global startingPositions
    currentIndex = (int(S_currentSlicingDirection.entryBox.entryBoxEditableLabel.get_text()) - 1)
    xPosition = S_startingX.entryBox.entryBoxEditableLabel.get_text()
    yPosition = S_startingY.entryBox.entryBoxEditableLabel.get_text()
    zPosition = S_startingZ.entryBox.entryBoxEditableLabel.get_text()
    if xPosition in NANs:
        xPosition = 0.0
    else:
        xPosition = float(xPosition)

    if yPosition in NANs:
        yPosition = 0.0
    else:
        yPosition = float(yPosition)

    if zPosition in NANs:
        zPosition = 0.0
    else:
        zPosition = float(zPosition)
    startingPositions[currentIndex] = [xPosition, yPosition, zPosition]

def update_directions():
    global directions
    currentIndex = (int(S_currentSlicingDirection.entryBox.entryBoxEditableLabel.get_text()) - 1)
    theta = S_theta.entryBox.entryBoxEditableLabel.get_text()
    phi = S_phi.entryBox.entryBoxEditableLabel.get_text()
    if theta in NANs:
        theta = 0.0
    else:
        theta = float(theta)
    if phi in NANs:
        phi = 0.0
    else:
        phi = float(phi)
    directions[currentIndex] = [theta, phi]

def update_current_selection():
    global startingPositions
    currentSlicingDirection = S_currentSlicingDirection.entryBox.entryBoxEditableLabel.get_text()
    if currentSlicingDirection == "":
        currentIndex = 1
    else:
        currentIndex = int(S_currentSlicingDirection.entryBox.entryBoxEditableLabel.get_text()) - 1
    S_startingX.entryBox.entryBoxEditableLabel.set_text(str(startingPositions[currentIndex][0]))
    S_startingY.entryBox.entryBoxEditableLabel.set_text(str(startingPositions[currentIndex][1]))
    S_startingZ.entryBox.entryBoxEditableLabel.set_text(str(startingPositions[currentIndex][2]))
    S_theta.entryBox.entryBoxEditableLabel.set_text(str(directions[currentIndex][0]))
    S_phi.entryBox.entryBoxEditableLabel.set_text(str(directions[currentIndex][1]))

def update_placeholder():
    pass

""" Functions for adding widgets """


def safe_board_add(board, widget, **kwargs):
    if widget in board._pins:
        board.move(widget, **kwargs)
    else:
        board.add(widget, **kwargs)

def enable_3_axis_mode():
    R_optionMode.D_variables['numSlicingDirections'] = 1
    R_optionMode.D_variables['startingPositions'] = [[0.0, 0.0, 0.0]]
    R_optionMode.D_variables['directions'] = [[0.0, 0.0]]
    
    for w in startingBoxWidgets:
        w.hide()
    for w in slicingDirectionsBoxWidgets:
        w.hide()
    lowerLine.hide()
    slicingDirectionBoard.clear()
    safe_board_add(settingsBoard, 
        R_optionMode,
        center_x_percent=0.5,
        top=530,
    )
    menuTopY = 495
    rowSpacing = 25
    safe_board_add(settingsBoard, 
        r0c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 0 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r0c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 0 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r1c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 1 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r1c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 1 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r2c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 2 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r2c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 2 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r3c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 3 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r3c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 3 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r4c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 4 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r4c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 4 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r5c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 5 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r5c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 5 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r6c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 6 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r6c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 6 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r7c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 7 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r7c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 7 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r8c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 8 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r8c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 8 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r9c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 9 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r9c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 9 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r10c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 10 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r10c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 10 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r11c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 11 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r11c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 11 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r12c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 12 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r12c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 12 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r13c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 13 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r13c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 13 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r14c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 14 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r14c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 14 * rowSpacing,
    )

    cycle_decks(0, 0)

def display_starting_box():
    safe_board_add(settingsBoard, I_startingBox, center_x_percent=0.5, top=530)
    safe_board_add(slicingDirectionBoard, S_numSlicingDirections, left=285, top=530 - 13)
    safe_board_add(slicingDirectionBoard, B_numSlicingDirections, left=355, top=530 - 11)

def display_slicing_directions_box():
    height = 320

    safe_board_add(rightToolBarBoard, I_slicingDirectionBox, left=21, bottom=5)

    safe_board_add(rightToolBarTopBoard, S_currentSlicingDirection, left=285, top=height - 2 * widgetHeightSpacing - 2 * widgetBufferVertical - 13)
    S_currentSlicingDirection.update_maxValue(int(numSlicingDirections))  # Update the size of slicingDirectionList

    safe_board_add(rightToolBarTopBoard, B_addNew, left=352, top=height - 2 * widgetHeightSpacing - 2 * widgetBufferVertical - 11)
    safe_board_add(rightToolBarTopBoard, B_remove, left=391, top=height - 2 * widgetHeightSpacing - 2 * widgetBufferVertical - 11)
    safe_board_add(rightToolBarTopBoard, B_removeAll, left=229, top=height - 275)

    safe_board_add(rightToolBarTopBoard, S_startingX, left=90, top=height - 180)
    safe_board_add(rightToolBarTopBoard, S_startingY, left=90, top=height - 220)
    safe_board_add(rightToolBarTopBoard, S_startingZ, left=90, top=height - 260)
    safe_board_add(rightToolBarTopBoard, S_theta, left=285, top=height - 180)
    safe_board_add(rightToolBarTopBoard, S_phi, left=285, top=height - 220)

def enable_5_axis_mode():
    global numSlicingDirections, startingPositions, directions

    R_optionMode.D_variables['numSlicingDirections'] = numSlicingDirections
    R_optionMode.D_variables['startingPositions'] = startingPositions
    R_optionMode.D_variables['directions'] = directions

    if (numSlicingDirections == 1):  # If the user has not yet specified the number of slicing directions, display the starter box
        spacing = 68
        display_starting_box()
        B_numSlicingDirections.D_variables['applied'] = False
        for w in slicingDirectionsBoxWidgets:
            w.hide()
        for w in startingBoxWidgets:
            w.unhide()
    else:  # Display the slicing direction box
        B_numSlicingDirections.D_variables['applied'] = True
        spacing = 0
        display_slicing_directions_box()
        for w in startingBoxWidgets:
            w.hide()
        for w in slicingDirectionsBoxWidgets:
            w.unhide()

    lowerLine.unhide()
    numSlicingDirections = R_optionMode.D_variables.get('numSlicingDirections', 1)
    
    if (numSlicingDirections == 1):
        spacing = 68
        display_starting_box()
        B_numSlicingDirections.D_variables['applied'] = False
        for w in slicingDirectionsBoxWidgets:
            w.hide()
        for w in startingBoxWidgets:
            w.unhide()
    else:
        B_numSlicingDirections.D_variables['applied'] = True
        spacing = 0
        display_slicing_directions_box()
        for w in startingBoxWidgets:
            w.hide()
        for w in slicingDirectionsBoxWidgets:
            w.unhide()
            
    lowerLine.unhide()
    safe_board_add(settingsBoard, 
        lowerLine,
        left=0,
        top=530 - spacing,
    )
    safe_board_add(settingsBoard, 
        R_optionMode,
        center_x_percent=0.5,
        top=530 - spacing,
    )
    menuTopY = 495 - spacing
    rowSpacing = 25
    
    safe_board_add(settingsBoard, 
        r0c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 0 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r0c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 0 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r1c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 1 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r1c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 1 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r2c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 2 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r2c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 2 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r3c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 3 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r3c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 3 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r4c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 4 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r4c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 4 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r5c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 5 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r5c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 5 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r6c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 6 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r6c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 6 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r7c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 7 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r7c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 7 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r8c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 8 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r8c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 8 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r9c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 9 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r9c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 9 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r10c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 10 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r10c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 10 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r11c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 11 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r11c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 11 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r12c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 12 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r12c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 12 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r13c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 13 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r13c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 13 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r14c0SettingsDeck,
        left=widgetBufferRight,
        top=menuTopY - 14 * rowSpacing,
    )
    safe_board_add(settingsBoard, 
        r14c1SettingsDeck,
        right=baseGridRight - widgetBufferRight,
        top=menuTopY - 14 * rowSpacing,
    )
    
    cycle_decks(0, 0)

def initialize_all_widgets(gui, windowHeight):
    """CONTAINER WIDGETS"""
    # Entire window
    gui.add(baseGrid)
    baseGrid.clear()
    # R0 C0
    baseGrid.add(0, 0, topLeftGrid)
    topLeftGrid.add(0, 1, topLeftStack1)
    topLeftStack1.insert(Dark_Gray_Background(), 0)
    # R0 C1
    # R1 C0
    leftToolBarStack.insert(leftToolBarBoard, 0)
    leftToolBarStack.insert(leftToolBarTopBoard, 1)
    rightToolBarStack.insert(rightToolBarBoard, 0)
    rightToolBarStack.insert(rightToolBarTopBoard, 1)
    
    # R1 C1
    baseGrid.add(1, 1, settingsStack)
    settingsStack.insert(Light_Gray_Background(), 0)
    settingsStack.insert(settingsBoard, 1)
    settingsStack.insert(slicingDirectionBoard, 2)
    
    # R2 C0

    # R2 C1
    baseGrid.add(2, 1, Light_Gray_Background())

    """ Adjust container parameters """
    baseGrid.set_row_height(0, bannerHeight)
    baseGrid.set_col_width(1, baseGridRight)
    baseGrid.set_row_height(1, baseGridTop)
    lowerLeftTop = windowHeight - (bannerHeight + baseGridTop)
    topLeftGrid.set_col_width(0, 315)

    """ Add widgets to containers """
    # R0 C0
    topLeftStack1.add(R_viewMode)
    topLeftGrid.add(0, 0, I_logo)
    # R0 C1
    baseGrid.add(0, 1, Dark_Gray_Background())
    # R1 C0
    leftToolBarBoard.add(B_selectFile, left=0, top=baseGridTop)
    leftToolBarBoard.add(B_saveProject, left=60, top=baseGridTop)
    leftToolBarBoard.add(B_calibration, left=120, top=baseGridTop)
    leftToolBarBoard.add(B_plateSettings, left=180, top=baseGridTop)
    
    leftToolBarBoard.add(plateSettingsBackgroundDeck, left=180, top=baseGridTop - 50)
    leftToolBarTopBoard.add(r1c0PlateSettingsDeck, left=190, top=baseGridTop - 60)
    leftToolBarTopBoard.add(r1c1PlateSettingsDeck, left=250, top=baseGridTop - 60)
    leftToolBarTopBoard.add(r2c0PlateSettingsDeck, left=190, top=baseGridTop - 60 - popUpWidgetHeightSpacing)
    leftToolBarTopBoard.add(r2c1PlateSettingsDeck, left=265, top=baseGridTop - 60 - popUpWidgetHeightSpacing)
    leftToolBarTopBoard.add(r3c0PlateSettingsDeck, left=190, top=baseGridTop - 60 - 2*popUpWidgetHeightSpacing)
    leftToolBarTopBoard.add(r3c1PlateSettingsDeck, left=265, top=baseGridTop - 60 - 2*popUpWidgetHeightSpacing)
    leftToolBarTopBoard.add(r4c0PlateSettingsDeck, left=190, top=baseGridTop - 60 - 3*popUpWidgetHeightSpacing)
    leftToolBarTopBoard.add(r4c1PlateSettingsDeck, left=265, top=baseGridTop - 60 - 3*popUpWidgetHeightSpacing)
    
    leftToolBarBoard.add(R_geometryAction, left=0, bottom=5)
    leftToolBarBoard.add(geometryActionBackgroundDeck, left=60, bottom=5)
    leftToolBarTopBoard.add(r0GeometryActionDeck,center_x=130, bottom=120)
    leftToolBarTopBoard.add(r2c0GeometryActionDeck, left=70, bottom=115 - popUpWidgetHeightSpacing + 15)
    leftToolBarTopBoard.add(r2c1GeometryActionDeck,left=85, bottom=115 - popUpWidgetHeightSpacing + 10)
    leftToolBarTopBoard.add(r3c0GeometryActionDeck,left=70, bottom=115 - 2 * popUpWidgetHeightSpacing + 15)
    leftToolBarTopBoard.add(r3c1GeometryActionDeck,left=85, bottom=115 - 2 * popUpWidgetHeightSpacing + 10)
    leftToolBarTopBoard.add(r4c0GeometryActionDeck,left=70, bottom=115 - 3 * popUpWidgetHeightSpacing + 15)
    leftToolBarTopBoard.add(r4c1GeometryActionDeck,left=85, bottom=115 - 3 * popUpWidgetHeightSpacing + 10)
    # R1 C1
    safe_board_add(settingsBoard, L_settingsTitle, center_x_percent=0.5, top=baseGridTop - widgetBufferVertical)
    safe_board_add(settingsBoard, Black_Underline_Frame(), left=0, top=565)
    safe_board_add(settingsBoard, R_printMode, center_x_percent=0.5, top=565)
    safe_board_add(settingsBoard, Gray_Underline_Frame(), left=0, top=baseGridTop - 2 * widgetHeightSpacing - widgetBufferVertical)
    enable_5_axis_mode()  # Default mode provides starter 5-axis options

    viewportGrid.set_col_width(1, 420)
    rightToolBarHBox.add(rightToolBarStack)
    viewportGrid.add(0, 0, leftToolBarStack)
    viewportGrid.add(0, 1, rightToolBarHBox)
    baseGrid.add(1, 0, viewportGrid) # This needs to be added after everything has been added to the settingsBoard or else the radio button order will get messed up again
    
    # R2 C0

    # R2 C1
    safe_board_add(settingsBoard, sliceButtonDeck, center_x_percent=0.5, bottom=2 * widgetBufferVertical)

""" WIDGET DEFINITIONS """
# CONTAINER WIDGETS:
# Entire Window
baseGrid = glooey.Grid(3, 2)
# R0 C0
topLeftGrid = glooey.Grid(1, 2)
topLeftStack1 = glooey.Stack()
# R0 C1
# R1 C0
viewportGrid = glooey.Grid(1, 2)
rightToolBarHBox = glooey.HBox()
rightToolBarHBox.alignment = 'bottom right'
rightToolBarStack = glooey.Stack()
rightToolBarBoard = glooey.Board()
rightToolBarTopBoard = glooey.Board()
leftToolBarStack = glooey.Stack()
leftToolBarBoard = glooey.Board()
leftToolBarTopBoard = glooey.Board()
# R1 C1
settingsStack = glooey.Stack()
settingsBoard = glooey.Board()
slicingDirectionBoard = glooey.Board()
# R2 C0

# R2 C1
lowerSettingsStack = glooey.Stack()

# WIDGETS
# Rotate Mode Radio Button Variables
rotateModeBackground = "image_resources/rotateMode_Radio_Button_Images/background.png"
rotateModeNames = ["X", "Y", "Z"]
rotateModeImages = [
    [
        "image_resources/rotateMode_Radio_Button_Images/x/R_uncheckedBase.png",
        "image_resources/rotateMode_Radio_Button_Images/x/R_uncheckedOver.png",
        "image_resources/rotateMode_Radio_Button_Images/x/R_uncheckedDown.png",
        "image_resources/rotateMode_Radio_Button_Images/x/R_checked.png",
    ],
    [
        "image_resources/rotateMode_Radio_Button_Images/y/R_uncheckedBase.png",
        "image_resources/rotateMode_Radio_Button_Images/y/R_uncheckedOver.png",
        "image_resources/rotateMode_Radio_Button_Images/y/R_uncheckedDown.png",
        "image_resources/rotateMode_Radio_Button_Images/y/R_checked.png",
    ],
    [
        "image_resources/rotateMode_Radio_Button_Images/z/R_uncheckedBase.png",
        "image_resources/rotateMode_Radio_Button_Images/z/R_uncheckedOver.png",
        "image_resources/rotateMode_Radio_Button_Images/z/R_uncheckedDown.png",
        "image_resources/rotateMode_Radio_Button_Images/z/R_checked.png",
    ],
]

rotateModeDefaultIndex = 0

geometryActionBackgroundDeck = glooey.Deck(
    "deactivated",
    deactivated=Widget_Label(""),
    base=Custom_Image("image_resources/geometryActionPopUpBox_Images/background.png"),
    scale=Custom_Image(
        "image_resources/geometryActionPopUpBox_Images/scaleBackground.png"
    ),
)
geometryActionBackgroundState = "deactivated"
geometryActionState = "blank"
settingsState = "material"

r0GeometryActionDeck = glooey.Deck(
    "blank",
    blank=Widget_Label(""),
    translate=Pop_Up_Box_Label("Translate", color="black"),
    rotate=Pop_Up_Box_Label("Rotate", color="black"),
    scale=Pop_Up_Box_Label("Scale", color="black"),
)
r2c0GeometryActionDeck = glooey.Deck(
    "blank",
    blank=Widget_Label(""),
    translate=Widget_Label("X", color="red"),
    rotate=Widget_Label("", color="red"),
    scale=Widget_Label("", color="red"),
)
r2c1GeometryActionDeck = glooey.Deck(
    "blank",
    blank=Widget_Label(""),
    translate=Entry_Box(
        str(translateX), buildPlateBounds[0], buildPlateBounds[1], "mm"
    ),
    rotate=Radio_Buttons(
        "Horizontal",
        False,
        False,
        rotateModeBackground,
        rotateModeNames,
        rotateModeImages,
        rotateModeDefaultIndex,
        None,
        update_mode_placeholder,
        [],
    ),
    scale=Entry_Box(str(scaleFactor), scaleBounds[0], scaleBounds[1], "%"),
)
r3c0GeometryActionDeck = glooey.Deck(
    "blank",
    blank=Widget_Label(""),
    translate=Widget_Label("Y", color="green"),
    rotate=Widget_Label("", color="green"),
    scale=Widget_Label("", color="green"),
)
r3c1GeometryActionDeck = glooey.Deck(
    "blank",
    blank=Widget_Label(""),
    translate=Entry_Box(
        str(translateY), buildPlateBounds[0], buildPlateBounds[1], "mm"
    ),
    rotate=Entry_Box(str(rotateY), rotateBounds[0], rotateBounds[1], "°CCW"),
    scale=Unlabeled_Image_Button(
        "image_resources/apply_Button_Images/Base.png",
        "image_resources/apply_Button_Images/Over.png",
        "image_resources/apply_Button_Images/Down.png",
        apply_placeholder,
        [],
    ),
)
r4c0GeometryActionDeck = glooey.Deck(
    "blank",
    blank=Widget_Label(""),
    translate=Widget_Label("Z", color="blue"),
    rotate=Widget_Label("", color="blue"),
    scale=Widget_Label("", color="blue"),
)
r4c1GeometryActionDeck = glooey.Deck(
    "blank",
    blank=Widget_Label(""),
    translate=Entry_Box(str(translateZ), zBounds[0], zBounds[1], "mm"),
    rotate=Unlabeled_Image_Button(
        "image_resources/apply_Button_Images/Base.png",
        "image_resources/apply_Button_Images/Over.png",
        "image_resources/apply_Button_Images/Down.png",
        apply_placeholder,
        [],
    ),
    scale=Widget_Label(""),
)

# Print Mode Radio Button Variables
printModeBackground = "image_resources/printMode_Radio_Button_Images/background.png"
printModeNames = ["5-Axis Mode", "3-Axis Mode"]
printModeImages = [
    [
        "image_resources/printMode_Radio_Button_Images/5AxisMode/R_uncheckedBase.png",
        "image_resources/printMode_Radio_Button_Images/5AxisMode/R_uncheckedOver.png",
        "image_resources/printMode_Radio_Button_Images/5AxisMode/R_uncheckedDown.png",
        "image_resources/printMode_Radio_Button_Images/5AxisMode/R_checked.png",
    ],
    [
        "image_resources/printMode_Radio_Button_Images/3AxisMode/R_uncheckedBase.png",
        "image_resources/printMode_Radio_Button_Images/3AxisMode/R_uncheckedOver.png",
        "image_resources/printMode_Radio_Button_Images/3AxisMode/R_uncheckedDown.png",
        "image_resources/printMode_Radio_Button_Images/3AxisMode/R_checked.png",
    ],
]

printModeDefaultIndex = 0
# Option Mode Radio Button Variables
optionModeBackground = "image_resources/optionMode_Radio_Button_Images/background.png"
optionModeNames = [
    "Material",
    "Strength",
    "Resolution",
    "Movement",
    "Supports",
    "Adhesion",
]
optionModeImages = [
    [
        "image_resources/optionMode_Radio_Button_Images/material/R_uncheckedBase.png",
        "image_resources/optionMode_Radio_Button_Images/material/R_uncheckedOver.png",
        "image_resources/optionMode_Radio_Button_Images/material/R_uncheckedDown.png",
        "image_resources/optionMode_Radio_Button_Images/material/R_checked.png",
    ],
    [
        "image_resources/optionMode_Radio_Button_Images/strength/R_uncheckedBase.png",
        "image_resources/optionMode_Radio_Button_Images/strength/R_uncheckedOver.png",
        "image_resources/optionMode_Radio_Button_Images/strength/R_uncheckedDown.png",
        "image_resources/optionMode_Radio_Button_Images/strength/R_checked.png",
    ],
    [
        "image_resources/optionMode_Radio_Button_Images/resolution/R_uncheckedBase.png",
        "image_resources/optionMode_Radio_Button_Images/resolution/R_uncheckedOver.png",
        "image_resources/optionMode_Radio_Button_Images/resolution/R_uncheckedDown.png",
        "image_resources/optionMode_Radio_Button_Images/resolution/R_checked.png",
    ],
    [
        "image_resources/optionMode_Radio_Button_Images/movement/R_uncheckedBase.png",
        "image_resources/optionMode_Radio_Button_Images/movement/R_uncheckedOver.png",
        "image_resources/optionMode_Radio_Button_Images/movement/R_uncheckedDown.png",
        "image_resources/optionMode_Radio_Button_Images/movement/R_checked.png",
    ],
    [
        "image_resources/optionMode_Radio_Button_Images/supports/R_uncheckedBase.png",
        "image_resources/optionMode_Radio_Button_Images/supports/R_uncheckedOver.png",
        "image_resources/optionMode_Radio_Button_Images/supports/R_uncheckedDown.png",
        "image_resources/optionMode_Radio_Button_Images/supports/R_checked.png",
    ],
    [
        "image_resources/optionMode_Radio_Button_Images/adhesion/R_uncheckedBase.png",
        "image_resources/optionMode_Radio_Button_Images/adhesion/R_uncheckedOver.png",
        "image_resources/optionMode_Radio_Button_Images/adhesion/R_uncheckedDown.png",
        "image_resources/optionMode_Radio_Button_Images/adhesion/R_checked.png",
    ],
]

optionModeDefaultIndex = 0

geometryActionBackground = (
    "image_resources/geometryAction_Radio_Button_Images/background.png"
)
geometryActionNames = ["Translate", "Rotate", "Scale"]
geometryActionImages = [
    [
        "image_resources/geometryAction_Radio_Button_Images/translate/R_uncheckedBase.png",
        "image_resources/geometryAction_Radio_Button_Images/translate/R_uncheckedOver.png",
        "image_resources/geometryAction_Radio_Button_Images/translate/R_uncheckedDown.png",
        "image_resources/geometryAction_Radio_Button_Images/translate/R_checked.png",
    ],
    [
        "image_resources/geometryAction_Radio_Button_Images/rotate/R_uncheckedBase.png",
        "image_resources/geometryAction_Radio_Button_Images/rotate/R_uncheckedOver.png",
        "image_resources/geometryAction_Radio_Button_Images/rotate/R_uncheckedDown.png",
        "image_resources/geometryAction_Radio_Button_Images/rotate/R_checked.png",
    ],
    [
        "image_resources/geometryAction_Radio_Button_Images/scale/R_uncheckedBase.png",
        "image_resources/geometryAction_Radio_Button_Images/scale/R_uncheckedOver.png",
        "image_resources/geometryAction_Radio_Button_Images/scale/R_uncheckedDown.png",
        "image_resources/geometryAction_Radio_Button_Images/scale/R_checked.png",
    ],
]
geometryActionDefaultIndex = None
# View Mode Radio Button Variables
viewModeBackground = "image_resources/viewMode_Radio_Button_Images/background.png"
viewModeNames = ["Prepare", "Preview"]
viewModeImages = [
    [
        "image_resources/viewMode_Radio_Button_Images/prepare/R_uncheckedBase.png",
        "image_resources/viewMode_Radio_Button_Images/prepare/R_uncheckedOver.png",
        "image_resources/viewMode_Radio_Button_Images/prepare/R_uncheckedDown.png",
        "image_resources/viewMode_Radio_Button_Images/prepare/R_checked.png",
    ],
    [
        "image_resources/viewMode_Radio_Button_Images/preview/R_uncheckedBase.png",
        "image_resources/viewMode_Radio_Button_Images/preview/R_uncheckedOver.png",
        "image_resources/viewMode_Radio_Button_Images/preview/R_uncheckedDown.png",
        "image_resources/viewMode_Radio_Button_Images/preview/R_checked.png",
    ],
]
viewModeDefaultIndex = 0
viewModeState = "prepare"

def on_filament_profile_changed(new_profile_name):
    global current_profile_name, filamentType, filamentDiameter, softeningTemp, idleTemp, minNozzleTemp, maxNozzleTemp
    global enablePressureAdvance, chamberTemp, activateChamberTemp, nozzleFirstLayer, nozzleOtherLayers, bedFirstLayer, bedOtherLayers
    global nozzleTemp, initialNozzleTemp, bedTemp, initialBedTemp
    current_profile_name = new_profile_name
    prof = filament_profiles[current_profile_name]
    filamentType = prof.get("type", "PLA")
    filamentDiameter = prof.get("diameter", 1.75)
    softeningTemp = prof.get("softeningTemp", 45)
    idleTemp = prof.get("idleTemp", 0)
    minNozzleTemp = prof.get("minNozzleTemp", 190)
    maxNozzleTemp = prof.get("maxNozzleTemp", 240)
    enablePressureAdvance = prof.get("enablePressureAdvance", False)
    chamberTemp = prof.get("chamberTemp", 0)
    activateChamberTemp = prof.get("activateChamberTemp", False)
    nozzleFirstLayer = prof.get("nozzleFirstLayer", 220)
    nozzleOtherLayers = prof.get("nozzleOtherLayers", 220)
    bedFirstLayer = prof.get("bedFirstLayer", 55)
    bedOtherLayers = prof.get("bedOtherLayers", 55)
    
    # Backwards compatibility
    nozzleTemp = nozzleOtherLayers
    initialNozzleTemp = nozzleFirstLayer
    bedTemp = bedOtherLayers
    initialBedTemp = bedFirstLayer

    r2c1SettingsDeck.get_widget("material").set_text(filamentType)
    r3c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(filamentDiameter))
    r4c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(softeningTemp))
    r5c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(idleTemp))
    r6c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(minNozzleTemp))
    r7c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(maxNozzleTemp))
    if enablePressureAdvance:
        r8c1SettingsDeck.get_widget("material").check()
    else:
        r8c1SettingsDeck.get_widget("material").uncheck()
    r9c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(chamberTemp))
    if activateChamberTemp:
        r10c1SettingsDeck.get_widget("material").check()
    else:
        r10c1SettingsDeck.get_widget("material").uncheck()
    r11c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(nozzleFirstLayer))
    r12c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(nozzleOtherLayers))
    r13c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(bedFirstLayer))
    r14c1SettingsDeck.get_widget("material").entryBoxEditableLabel.set_text(str(bedOtherLayers))


# Define widget decks for all rows and columns of all settings menu layout states
defaultState = "material"
r0c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Filament Profile"),
    strength=Widget_Label("Infill %"),
    resolution=Widget_Label("Layer Height"),
    movement=Widget_Label("Print Speed"),
    supports=Widget_Label("Enable Supports"),
    adhesion=Widget_Label("Enable Brim"),
    printer=Widget_Label('Plate Shape'))
filamentProfileMenu = Drop_Down_Menu(list(filament_profiles.keys()), settingsBoard, "Upper", on_selection_changed=on_filament_profile_changed)
r0c1SettingsDeck = glooey.Deck(
    defaultState,
    material=filamentProfileMenu,
    strength=Entry_Box(str(infillPercentage), 0.0, 100.0, "%"),
    resolution=Entry_Box(str(layerHeight), 0.05, 2.0, "mm"),
    movement=Entry_Box(str(printSpeed), 5.0, 300.0, "mm/s"),
    supports=Checkbox(),
    adhesion=Checkbox(),
    printer=Drop_Down_Menu(['rectangular', 'circular'], settingsBoard, 'Upper'))
r1c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Save Profile Name"),
    strength=Widget_Label("Shell Thickness"),
    resolution=Widget_Label("Enable Non-Planar Tops"),
    movement=Widget_Label("    Initial Print Speed"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Widget_Label('X / Diameter'))
r1c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("(Auto-saves on change)"),
    strength=Entry_Box(str(shellThickness), 1, 10, "layers"),
    resolution=Checkbox(),
    movement=Entry_Box(str(initialPrintSpeed), 5.0, 300.0, "mm/s"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Entry_Box(str(buildPlateX), 10.0, 1000.0, 'mm'))
r2c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Type (PLA, PETG, ABS...)"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Widget_Label("Travel Speed"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Widget_Label('Y / Depth'))
r2c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label(filamentType),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Entry_Box(str(travelSpeed), 5.0, 300.0, "mm/s"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Entry_Box(str(buildPlateY), 10.0, 1000.0, 'mm'))
#
r3c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Diameter"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Widget_Label("    Initial Travel Speed"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Widget_Label('Z (Height)'))
r3c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(filamentDiameter), 1.0, 3.0, "mm"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Entry_Box(str(initialTravelSpeed), 5.0, 300.0, "mm/s"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Entry_Box(str(buildPlateZ), 10.0, 1000.0, 'mm'))
#
r4c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Softening Temperature"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Widget_Label("Enable Z-Hop When Travelling"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())
r4c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(softeningTemp), 20.0, 300.0, "°C"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Checkbox(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())
#
r5c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Idle Temperature"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Widget_Label("Enable Retraction"),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())
r5c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(idleTemp), 0.0, 300.0, "°C"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Checkbox(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())

r6c0MovementDeck = glooey.Deck( # This deck is nested so that it only becomes visible if retraction is checked
    defaultState,
    enabled=Widget_Label("    Retraction Distance"),
    disabled=Light_Gray_Background(),
)

r6c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Min Nozzle Temperature"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=r6c0MovementDeck,
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())

r6c1MovementDeck = glooey.Deck( # This deck is nested so that it only becomes visible if retraction is checked
    defaultState,
    enabled=Entry_Box(str(retractionDistance), 0.1, 10.0, "mm"),
    disabled=Light_Gray_Background(),
)

r6c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(minNozzleTemp), 100.0, 400.0, "°C"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=r6c1MovementDeck,
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())

#
r7c0MovementDeck = glooey.Deck( # This deck is nested so that it only becomes visible if retraction is checked
    defaultState,
    enabled=Widget_Label("    Retraction Speed"),
    disabled=Light_Gray_Background(),
)

r7c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label("Max Nozzle Temperature"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=r7c0MovementDeck,
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())
r7c1MovementDeck = glooey.Deck( # This deck is nested so that it only becomes visible if retraction is checked
    defaultState,
    enabled=Entry_Box(str(retractionSpeed), 5.0, 60.0, "mm/s"),
    disabled=Light_Gray_Background(),
)
r7c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(maxNozzleTemp), 100.0, 400.0, "°C"),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=r7c1MovementDeck,
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background(),
    printer=Light_Gray_Background())

r8c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label('Enable Pressure Advance'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r8c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Checkbox(),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r9c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label('Chamber Temperature'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r9c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(chamberTemp), 0.0, 200.0, '°C'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r10c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label('Activate Chamber Temp'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r10c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Checkbox(),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r11c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label('Nozzle Temp First Layer'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r11c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(nozzleFirstLayer), 100.0, 400.0, '°C'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r12c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label('Nozzle Temp Other Layers'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r12c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(nozzleOtherLayers), 100.0, 400.0, '°C'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r13c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label('Bed Temp First Layer'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r13c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(bedFirstLayer), 0.0, 200.0, '°C'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r14c0SettingsDeck = glooey.Deck(
    defaultState,
    material=Widget_Label('Bed Temp Other Layers'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())
r14c1SettingsDeck = glooey.Deck(
    defaultState,
    material=Entry_Box(str(bedOtherLayers), 0.0, 200.0, '°C'),
    strength=Light_Gray_Background(),
    resolution=Light_Gray_Background(),
    movement=Light_Gray_Background(),
    supports=Light_Gray_Background(),
    adhesion=Light_Gray_Background()
,
    printer=Light_Gray_Background())

r1c0SettingsDeck.get_widget("material").set_style(italic=True)
r1c0SettingsDeck.get_widget("movement").set_style(italic=True)
r3c0SettingsDeck.get_widget("material").set_style(italic=True)
r3c0SettingsDeck.get_widget("movement").set_style(italic=True)
r6c0SettingsDeck.get_widget("movement").get_widget("enabled").set_style(italic=True)
r7c0SettingsDeck.get_widget("movement").get_widget("enabled").set_style(italic=True)
r4c1SettingsDeck.get_widget("movement").check() # INITIALIZE Z HOP AS CHECKED BY DEFAULT
r5c1SettingsDeck.get_widget("movement").check() # INITIALIZE RETRACTION AS CHECKED BY DEFAULT
r6c0MovementDeck.set_state("enabled")
r6c1MovementDeck.set_state("enabled")
r7c0MovementDeck.set_state("enabled")
r7c1MovementDeck.set_state("enabled")
# Slice button deck
sliceButtonDeck = glooey.Deck(
    "B_slice",
    B_slice=Disableable_Unlabeled_Image_Button(
        "image_resources/Slice_Button_Images/slice/base.png",
        "image_resources/Slice_Button_Images/slice/over.png",
        "image_resources/Slice_Button_Images/slice/down.png",
        set_sliceFlag,
        [],
        "image_resources/Slice_Button_Images/slice/disabled.png",
    ),
    B_saveGcodeAs=Unlabeled_Image_Button(
        "image_resources/Slice_Button_Images/saveGcodeAs/base.png",
        "image_resources/Slice_Button_Images/saveGcodeAs/over.png",
        "image_resources/Slice_Button_Images/saveGcodeAs/down.png",
        save_gcode_as,
        [],
    ),
)
B_saveProject = Unlabeled_Image_Button(
    "image_resources/File_Button_Images/saveProject/base.png",
    "image_resources/File_Button_Images/saveProject/over.png",
    "image_resources/File_Button_Images/saveProject/down.png",
    save_project,
    [],
)
sliceButtonDeck.get_widget("B_slice").set_disabled(True) # Start out with the slice button disabled. Only enable it when there is something to slice
# R0 C0
I_logo = Custom_Image("image_resources/logo/logo.png")  # New
R_viewMode = Radio_Buttons(
    "Horizontal",
    False,
    False,
    viewModeBackground,
    viewModeNames,
    viewModeImages,
    viewModeDefaultIndex,
    None,
    toggle_viewMode_layout,
    [],
)

R_viewMode.set_disabled(True) # Start out with this disabled so the user can't switch to the "Preview" mode since there's nothing there initially

# R0 C1

# R1 C0
def run_calibration(*args):
    print("Calibration not implemented yet!")

B_calibration = Unlabeled_Image_Button(
    "image_resources/File_Button_Images/calibration/base.png",
    "image_resources/File_Button_Images/calibration/over.png",
    "image_resources/File_Button_Images/calibration/down.png",
    run_calibration,
    [],
)

plateShapeDropdown = Drop_Down_Menu(['rectangular', 'circular'], leftToolBarStack, 'Lower')
plateShapeDropdown.currentSelection = plateShapeDropdown.options.index(buildPlateShape) if buildPlateShape in plateShapeDropdown.options else 0

r2c1PlateEntry = Entry_Box(str(buildPlateX), 10.0, 1000.0, 'mm')
r3c1PlateEntry = Entry_Box(str(buildPlateY), 10.0, 1000.0, 'mm')
r4c1PlateEntry = Entry_Box(str(buildPlateZ), 10.0, 1000.0, 'mm')

r1c0PlateLabel = Widget_Label("Shape")
r2c0PlateLabel = Widget_Label("X (Width)")
r3c0PlateLabel = Widget_Label("Y (Depth)")
r4c0PlateLabel = Widget_Label("Z (Height)")

plateSettingsBackgroundDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=Custom_Image("image_resources/geometryActionPopUpBox_Images/background.png"))

r1c0PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=r1c0PlateLabel)
r1c1PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=plateShapeDropdown)

r2c0PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=r2c0PlateLabel)
r2c1PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=r2c1PlateEntry)

r3c0PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=r3c0PlateLabel)
r3c1PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=r3c1PlateEntry)

r4c0PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=r4c0PlateLabel)
r4c1PlateSettingsDeck = glooey.Deck("hidden", hidden=Widget_Label(""), active=r4c1PlateEntry)

def update_plate_settings_ui(selected_shape=None):
    if selected_shape is None:
        shape = plateShapeDropdown.options[plateShapeDropdown.currentSelection]
    else:
        shape = selected_shape
    if shape == "circular":
        r2c0PlateLabel.set_text("Radius")
        r3c0PlateSettingsDeck.set_state("hidden")
        r3c1PlateSettingsDeck.set_state("hidden")
    else:
        r2c0PlateLabel.set_text("X (Width)")
        r3c0PlateLabel.set_text("Y (Depth)")
        if plateSettingsBackgroundDeck.state == "active":
            r3c0PlateSettingsDeck.set_state("active")
            r3c1PlateSettingsDeck.set_state("active")
    update_values()

plateShapeDropdown.on_selection_changed = update_plate_settings_ui

def toggle_plate_settings_layout(*args):
    if plateSettingsBackgroundDeck.state == "hidden":
        plateSettingsBackgroundDeck.set_state("active")
        r1c0PlateSettingsDeck.set_state("active")
        r1c1PlateSettingsDeck.set_state("active")
        r2c0PlateSettingsDeck.set_state("active")
        r2c1PlateSettingsDeck.set_state("active")
        r3c0PlateSettingsDeck.set_state("active")
        r3c1PlateSettingsDeck.set_state("active")
        r4c0PlateSettingsDeck.set_state("active")
        r4c1PlateSettingsDeck.set_state("active")
        update_plate_settings_ui()
    else:
        plateSettingsBackgroundDeck.set_state("hidden")
        r1c0PlateSettingsDeck.set_state("hidden")
        r1c1PlateSettingsDeck.set_state("hidden")
        r2c0PlateSettingsDeck.set_state("hidden")
        r2c1PlateSettingsDeck.set_state("hidden")
        r3c0PlateSettingsDeck.set_state("hidden")
        r3c1PlateSettingsDeck.set_state("hidden")
        r4c0PlateSettingsDeck.set_state("hidden")
        r4c1PlateSettingsDeck.set_state("hidden")
        update_values()

B_plateSettings = Unlabeled_Image_Button(
    "image_resources/File_Button_Images/plateSettings/base.png",
    "image_resources/File_Button_Images/plateSettings/over.png",
    "image_resources/File_Button_Images/plateSettings/down.png",
    toggle_plate_settings_layout,
    [],
)

B_selectFile = Unlabeled_Image_Button(
    "image_resources/File_Button_Images/base.png",
    "image_resources/File_Button_Images/over.png",
    "image_resources/File_Button_Images/down.png",
    select_file,
    [],
)
R_geometryAction = Radio_Buttons(
    "Vertical",
    False,
    True,
    geometryActionBackground,
    geometryActionNames,
    geometryActionImages,
    geometryActionDefaultIndex,
    None,
    toggle_left_toolbar_layout,
    [],
)
# R1 C1
L_settingsTitle = Title_Label("Print Settings")
R_printMode = Radio_Buttons(
    "Horizontal",
    False,
    False,
    printModeBackground,
    printModeNames,
    printModeImages,
    printModeDefaultIndex,
    None,
    toggle_printMode_layout,
    [],
)
# Slicing Directions Box:
I_startingBox = Custom_Image(
    "image_resources/slicingDirectionBox_Images/startingBox/background.png"
)
B_numSlicingDirections = Disableable_Unlabeled_Image_Button(
    "image_resources/slicingDirectionBox_Images/startingBox/apply/base.png",
    "image_resources/slicingDirectionBox_Images/startingBox/apply/over.png",
    "image_resources/slicingDirectionBox_Images/startingBox/apply/down.png",
    set_numSlicingDirections,
    [],
    "image_resources/slicingDirectionBox_Images/startingBox/apply/disabled.png"
)
B_numSlicingDirections.set_disabled(True)
B_numSlicingDirections.D_variables['applied'] = False

I_slicingDirectionBox = Custom_Image(
    "image_resources/slicingDirectionBox_Images/background.png"
)

S_numSlicingDirections = Spin_Box(
    40, "2", 2, maxSlicingDirections, 1, "int", update_placeholder, ""
)

S_currentSlicingDirection = Spin_Box(
    40, "2", 2, int(numSlicingDirections) + 1, 1, "int", update_current_selection, ""
)
B_addNew = Unlabeled_Image_Button(
    "image_resources/slicingDirectionBox_Images/addNew/base.png",
    "image_resources/slicingDirectionBox_Images/addNew/over.png",
    "image_resources/slicingDirectionBox_Images/addNew/down.png",
    add_new_slicing_direction,
    [],
)
B_remove = Unlabeled_Image_Button(
    "image_resources/slicingDirectionBox_Images/remove/base.png",
    "image_resources/slicingDirectionBox_Images/remove/over.png",
    "image_resources/slicingDirectionBox_Images/remove/down.png",
    remove_slicing_direction,
    [],
)
B_removeAll = Unlabeled_Image_Button(
    "image_resources/slicingDirectionBox_Images/removeAll/base.png",
    "image_resources/slicingDirectionBox_Images/removeAll/over.png",
    "image_resources/slicingDirectionBox_Images/removeAll/down.png",
    remove_all_slicing_directions,
    [],
)

S_startingX = Spin_Box(
    80,
    "0.0",
    buildPlateBounds[0],
    buildPlateBounds[1],
    5.0,
    "float",
    update_starting_positions,
    "mm",
)
S_startingY = Spin_Box(
    80,
    "0.0",
    buildPlateBounds[0],
    buildPlateBounds[1],
    5.0,
    "float",
    update_starting_positions,
    "mm",
)
S_startingZ = Spin_Box(
    80,
    "0.0",
    0.0,
    250.0,
    5.0,
    "float",
    update_starting_positions,
    "mm",
)
S_theta = Spin_Box(80, "0.0", 0.0, 90.0, 15.0, "float", update_directions, "°")
S_phi = Spin_Box(
    80,
    "0.0",
    rotateBounds[0],
    rotateBounds[1],
    15.0,
    "float",
    update_directions,
    "°CCW",
)
lowerLine = Gray_Underline_Frame()
startingBoxWidgets = [I_startingBox, S_numSlicingDirections, B_numSlicingDirections]
slicingDirectionsBoxWidgets = [
    I_slicingDirectionBox,
    S_currentSlicingDirection,
    B_addNew,
    B_remove,
    B_removeAll,
    S_startingX,
    S_startingY,
    S_startingZ,
    S_theta,
    S_phi,
]
#
R_optionMode = Radio_Buttons(
    "Horizontal",
    False,
    False,
    optionModeBackground,
    optionModeNames,
    optionModeImages,
    optionModeDefaultIndex,
    11,
    toggle_settings_layout,
    [],
)

R_optionMode.D_variables['numSlicingDirections'] = 1
R_optionMode.D_variables['startingPositions'] = [[0.0, 0.0, 0.0]]
R_optionMode.D_variables['directions'] = [[0.0, 0.0]]
R_optionMode.D_variables['D_slicePlaneValidity'] = {'0': True}
# R2 C0
geometryActionPopUpBox = Custom_Image(
    "image_resources/geometryActionPopUpBox_Images/background.png"
)
# R2 C1

settings_are_enabled = True

def enable_all_settings():
    global settings_are_enabled
    if not settings_are_enabled:
        cycle_decks(0, 0)
        settings_are_enabled = True

def disable_all_settings():
    global settings_are_enabled
    if settings_are_enabled:
        set_settings_deck_states(True)
        settings_are_enabled = False

