from krita import Krita

def find_vector_layers(layer, vector_layers):
    """ Recursively find all vector layers, even inside groups. """
    if layer.type() == 'grouplayer':  # If it's a group, search inside it
        for child in layer.childNodes():
            find_vector_layers(child, vector_layers)
    elif layer.type() == 'vectorlayer':  # If it's a vector layer, add it
        vector_layers.append(layer)

def merge_all_vector_layers():
    app = Krita.instance()
    doc = app.activeDocument()

    if not doc:
        print("No active document found.")
        return

    root = doc.rootNode()
    vector_layers = []
    
    # Recursively find all vector layers
    for layer in root.childNodes():
        find_vector_layers(layer, vector_layers)

    if len(vector_layers) < 2:
        print("Not enough vector layers to merge.")
        return

    # Create a new group layer
    group_layer = doc.createGroupLayer("Merged Vector Layers")
    root.addChildNode(group_layer, None)  # Add group at the top level

    doc.refreshProjection()

    # Move vector layers into the group (Reparenting)
    for layer in vector_layers:
        parent = layer.parentNode()
        if parent:  # Remove from its current parent
            parent.removeChildNode(layer)
        group_layer.addChildNode(layer, None)  # Move inside the group

    doc.refreshProjection()

    # Merge layers inside the group from top to bottom
    while len(group_layer.childNodes()) > 1:
        top_layer = group_layer.childNodes()[-1]  # Get the topmost layer
        below_layer = group_layer.childNodes()[-2] if len(group_layer.childNodes()) > 1 else None

        if below_layer:
            top_layer.mergeDown()
            doc.refreshProjection()

    print("All vector layers successfully merged into a single layer inside the group.")

merge_all_vector_layers()
