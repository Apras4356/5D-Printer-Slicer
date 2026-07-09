import re

def update_widget_functions():
    with open('widget_functions.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace the settings deck definitions (lines ~1660 to ~1750)
    # Find start and end
    start_str = 'r0c0SettingsDeck = glooey.Deck('
    end_str = 'r7c1SettingsDeck = glooey.Deck('
    start_idx = content.find(start_str)
    
    # find the end of r7c1SettingsDeck
    end_idx = content.find(')', content.find(end_str)) + 1
    
    decks = []
    
    decks.append('''r0c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Filament Profile'), strength=Widget_Label('Infill %'), resolution=Widget_Label('Layer Height'), movement=Widget_Label('Print Speed'), supports=Widget_Label('Enable Supports'), adhesion=Widget_Label('Enable Brim'))
r0c1SettingsDeck = glooey.Deck(defaultState, material=Light_Gray_Background(), strength=Entry_Box(str(infillPercentage), 0.0, 100.0, '%'), resolution=Entry_Box(str(layerHeight), 0.05, 2.0, 'mm'), movement=Entry_Box(str(printSpeed), 5.0, 300.0, 'mm/s'), supports=Checkbox(), adhesion=Checkbox())

r1c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('    Save Profile Name:'), strength=Widget_Label('Shell Thickness'), resolution=Widget_Label('Enable Non-Planar Tops'), movement=Widget_Label('    Initial Print Speed'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r1c1SettingsDeck = glooey.Deck(defaultState, material=Widget_Label(''), strength=Entry_Box(str(shellThickness), 1, 10, 'layers'), resolution=Checkbox(), movement=Entry_Box(str(initialPrintSpeed), 5.0, 300.0, 'mm/s'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r2c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Type (PLA, PETG, etc)'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Widget_Label('Travel Speed'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r2c1SettingsDeck = glooey.Deck(defaultState, material=Widget_Label(''), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Entry_Box(str(travelSpeed), 5.0, 300.0, 'mm/s'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r3c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Diameter'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Widget_Label('    Initial Travel Speed'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r3c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(filamentDiameter), 1.0, 3.0, 'mm'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Entry_Box(str(initialTravelSpeed), 5.0, 300.0, 'mm/s'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r4c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Softening Temperature'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Widget_Label('Enable Z-Hop When Travelling'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r4c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(softeningTemp), 20.0, 300.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Checkbox(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r5c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Idle Temperature'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Widget_Label('Enable Retraction'), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r5c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(idleTemp), 0.0, 300.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Checkbox(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r6c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Min Nozzle Temperature'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r6c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(minNozzleTemp), 100.0, 400.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r7c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Max Nozzle Temperature'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r7c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(maxNozzleTemp), 100.0, 400.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r8c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Enable Pressure Advance'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r8c1SettingsDeck = glooey.Deck(defaultState, material=Checkbox(), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r9c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Chamber Temperature'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r9c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(chamberTemp), 0.0, 200.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r10c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Activate Chamber Temp'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r10c1SettingsDeck = glooey.Deck(defaultState, material=Checkbox(), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r11c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Nozzle Temp First Layer'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r11c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(nozzleFirstLayer), 100.0, 400.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r12c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Nozzle Temp Other Layers'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r12c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(nozzleOtherLayers), 100.0, 400.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r13c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Bed Temp First Layer'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r13c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(bedFirstLayer), 0.0, 200.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())

r14c0SettingsDeck = glooey.Deck(defaultState, material=Widget_Label('Bed Temp Other Layers'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
r14c1SettingsDeck = glooey.Deck(defaultState, material=Entry_Box(str(bedOtherLayers), 0.0, 200.0, '°C'), strength=Light_Gray_Background(), resolution=Light_Gray_Background(), movement=Light_Gray_Background(), supports=Light_Gray_Background(), adhesion=Light_Gray_Background())
''')

    new_content = content[:start_idx] + '\n'.join(decks) + content[end_idx:]

    with open('widget_functions.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    update_widget_functions()
