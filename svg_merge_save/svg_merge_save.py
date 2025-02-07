from krita import Krita, Extension, InfoObject
from PyQt5.QtWidgets import QFileDialog

def find_vector_layers(layer, vector_layers):
    """ Recursively find all vector layers, even inside groups. """
    if layer.type() == 'grouplayer':  # If it's a group, search inside it
        for child in layer.childNodes():
            find_vector_layers(child, vector_layers)
    elif layer.type() == 'vectorlayer':  # If it's a vector layer, add it
        vector_layers.append(layer)

class ExportVectorLayersExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.krita = Krita.instance()

    def setup(self):
        """Setup method (does nothing here)"""
        pass

    def createActions(self, window):
        """Creates the menu action inside Krita's File menu"""
        if window is None:
            print("[ERROR] Krita window is not ready yet.")
            return

        action = window.createAction("export_vector_svg", "Export Vector Layers as Flat SVG", "file")
        action.triggered.connect(self.merge_all_vector_layers_and_export)

    def merge_all_vector_layers_and_export(self):
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc:
            print("No active document found.")
            return

        root = doc.rootNode()
        vector_layers = []

        # Recursively find all vector layers (including inside groups)
        for layer in root.childNodes():
            find_vector_layers(layer, vector_layers)

        if len(vector_layers) < 2:
            print("Not enough vector layers to merge.")
            return

        # Create a new group layer
        group_layer = doc.createGroupLayer("Merged Vector Layers")
        root.addChildNode(group_layer, None)  # Add group at the top level

        doc.refreshProjection()

        copied_layers = []

        # Copy vector layers into the new group (leave originals untouched)
        for layer in vector_layers:
            layer_copy = layer.duplicate()  # Create a duplicate
            layer_copy.setName(layer.name() + " (Copy)")  # Rename to avoid conflicts
            group_layer.addChildNode(layer_copy, None)  # Add copy to the group
            copied_layers.append(layer_copy)

        doc.refreshProjection()

        # Merge copied layers from top to bottom
        while len(group_layer.childNodes()) > 1:
            top_layer = group_layer.childNodes()[-1]  # Get the topmost layer
            below_layer = group_layer.childNodes()[-2] if len(group_layer.childNodes()) > 1 else None

            if below_layer:
                top_layer.mergeDown()
                doc.refreshProjection()

        # Get the final merged vector layer
        merged_layer = group_layer.childNodes()[0] if group_layer.childNodes() else None

        if merged_layer:
            print("All vector layers successfully merged into a single layer inside the group.")
            print("Original layers remain unchanged.")

            # Prompt the user for an SVG filename
            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix("svg")
            save_path, _ = file_dialog.getSaveFileName(None, "Save Merged Vector Layer as SVG", "", "SVG Files (*.svg)")

            # Validate file
            if save_path:
                # Convert the layer to an SVG XML string
                svg = merged_layer.toSvg()
                try:
                    # Try and save the SVG
                    with open(save_path, "w") as file:
                        file.writelines(svg)
                    file.close()
                    print(f"SVG exported successfully: {save_path}")

                    # Delete the Merged Group After Export**
                    group_layer.remove()
                    print("Temporary 'Merged Vector Layers' group removed.")
                except Exception as e:
                    print(f"ERROR: SVG export failed. {str(e)}")
            else:
                print("SVG export cancelled.")

        else:
            print("Error: No merged vector layer found.")

# Register the extension
Krita.instance().addExtension(ExportVectorLayersExtension(Krita.instance()))
