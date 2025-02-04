from krita import Krita

def merge_all_vector_layers():
    app = Krita.instance()
    doc = app.activeDocument()

    if not doc:
        print("No active document found.")
        return

    root = doc.rootNode()
    vector_layers = [layer for layer in root.childNodes() if layer.type() == "vectorlayer"]

    if len(vector_layers) < 2:
        print("Not enough vector layers to merge.")
        return

    # Create a new group layer
    group_layer = doc.createGroupLayer("Merged Vector Layers")
    root.addChildNode(group_layer, None)  # Add group at the top level

    doc.refreshProjection()

    # Move vector layers into the group (Reparenting)
    for layer in vector_layers:
        root.removeChildNode(layer)  # Ensure it's detached first
        group_layer.addChildNode(layer, None)  # Move inside the group
    
    doc.refreshProjection()

    # Merge layers inside the group from top to bottom
    while len(group_layer.childNodes()) > 1:
        top_layer = group_layer.childNodes()[-1]  # Get the topmost layer
        top_layer.mergeDown()
        doc.refreshProjection()

    print("All vector layers successfully merged into a single layer inside the group.")

merge_all_vector_layers()
