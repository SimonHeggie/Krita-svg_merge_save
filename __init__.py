from krita import Extension, Krita
from PyQt5.QtWidgets import QAction, QFileDialog
from .merge_svg_layers import merge_all_vector_layers_and_export

class MergeSvgExtension(Extension):
    """ Krita Extension to merge vector layers and export as an SVG """

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        """ Setup the extension (no special setup needed). """
        pass

    def createActions(self, window):
        """ Adds a menu action to Krita. """
        action = window.createAction("merge_svg_layers", "Merge & Export SVG", "tools/scripts")
        action.triggered.connect(self.run_script)

    def run_script(self):
        """ Runs the main script when the menu action is clicked. """
        merge_all_vector_layers_and_export()

Krita.instance().addExtension(MergeSvgExtension(Krita.instance()))
