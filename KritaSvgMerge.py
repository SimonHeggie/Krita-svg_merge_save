from krita import Krita, Node
from PyQt5.QtCore import QTimer

timer = QTimer()
timer.setInterval(150)  # Delay to avoid freezing
timer.setSingleShot(True)

def set_blend(mode):
    doc = Krita.instance().activeDocument()
    if not doc:
        return
    node: Node = doc.activeNode()
    if node:
        node.setBlendingMode(mode)

def merge_and_continue():
    doc = Krita.instance().activeDocument()
    if not doc:
        print("No active document.")
        return

    node: Node = doc.activeNode()
    if not node or node.type() != "vectorlayer":
        print("Please select a vector layer before running the script.")
        return

    if len([layer for layer in doc.topLevelNodes() if layer.type() == "vectorlayer"]) <= 1:
        print("Only one vector layer left. Stopping.")
        return  # Stop when only one vector layer remains

    bm = node.blendingMode()
    node.mergeDown()  # Merge with layer below

    timer.timeout.connect(lambda x=bm: set_blend(x))
    timer.start()

    # Call itself again after the delay
    timer.timeout.connect(merge_and_continue)

# Start the process
merge_and_continue()
