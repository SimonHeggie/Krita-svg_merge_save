from krita import Krita
from PyQt5.QtWidgets import QFileDialog

def find_vector_layers(layer, vector_layers):
    """ Recursively find all vector layers, even inside groups. """
    if layer.type() == 'grouplayer':  
        for child in layer.childNodes():
            find_vector_layers(child, vector_layers)
    elif layer.type() == 'vectorlayer':  
        vector_layers.append(layer)

def merge_all_vector_layers_and_export():
    """ Merges all vector layers in Krita and exports them as a single SVG. """
    app = Krita.instance()
    doc = app.activeDocument()

    if not doc:
        print("No active document found.")
        return

    root = doc.rootNode()
    vector_layers = []
    
    for layer in root.childNodes():
        find_vector_layers(layer, vector_layers)

    if len(vector_layers) < 2:
        print("Not enough vector layers to merge.")
        return

    group_layer = doc.createGroupLayer("Merged Vector Layers")
    root.addChildNode(group_layer, None)  

    doc.refreshProjection()

    copied_layers = []

    for layer in vector_layers:
        layer_copy = layer.duplicate()
        layer_copy.setName(layer.name() + " (Copy)")  
        group_layer.addChildNode(layer_copy, None)  
        copied_layers.append(layer_copy)

    doc.refreshProjection()

    while len(group_layer.childNodes()) > 1:
        top_layer = group_layer.childNodes()[-1]
        below_layer = group_layer.childNodes()[-2] if len(group_layer.childNodes()) > 1 else None

        if below_layer:
            top_layer.mergeDown()
            doc.refreshProjection()

    merged_layer = group_layer.childNodes()[0] if group_layer.childNodes() else None

    if merged_layer:
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix("svg")
        save_path, _ = file_dialog.getSaveFileName(None, "Save Merged Vector Layer as SVG", "", "SVG Files (*.svg)")
        save_path = ''.join(save_path)

        if save_path:
            svg = merged_layer.toSvg()
            try:
                with open(save_path, "w") as file:
                    file.writelines(svg)
                print(f"SVG exported successfully: {save_path}")
            except Exception as e:
                print(f"ERROR: SVG export failed. {e}")

        else:
            print("SVG export cancelled.")

        print("Removing temporary merged layer group...")
        root.removeChildNode(group_layer)  
        doc.refreshProjection()
        print("Temporary merged group deleted.")

    else:
        print("Error: No merged vector layer found.")
