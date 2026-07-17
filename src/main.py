import sys
from PyQt6.QtWidgets import QApplication

from src.view.main_window_view import MainWindowView
from src.controller.file_controller import FileLoader
from src.controller.context_menu_controller import ContextMenuController
from src.controller.file_saver import FileSaver
from src.view.edit_dialog_1d_view import EditDialogView1d
from src.view.edit_dialog_view_2d import EditDialogView2d
from src.model.pane_type import PaneType
import numpy as np


def main() -> int:
    app = QApplication(sys.argv)

    view = MainWindowView()
    fileLoader = FileLoader(view)

    if not fileLoader.start():
            return 0

    view.display(fileLoader.model)

    fileSaver = FileSaver(view)

    editDialog1d = None
    editDialog2d = None

    def closeEditDialogs():
        nonlocal editDialog1d, editDialog2d

        for dialog in (editDialog1d, editDialog2d):
            if dialog is not None:
                dialog.close()
                dialog.deleteLater()

        editDialog1d = None
        editDialog2d = None

    def refreshAfterFileInput():
        closeEditDialogs()
        view.display(fileLoader.model)

    def openEditDialog():
        nonlocal editDialog1d, editDialog2d

        spectrumComponent = fileLoader.model.getSpectrumComponent()
        data = fileLoader.model.getData()

        spectrumComponent.renderAll(
            np.array(data[PaneType.INTERACTIVE_POWER_SPECTRUM])
        )

        if fileLoader.model.is1dModel():
            editDialog1d = EditDialogView1d(
                modelContext=fileLoader.model,
                spectrumComponent=spectrumComponent,
            )
            editDialog1d.show()
            return

        if fileLoader.model.is2dModel():
            editDialog2d = EditDialogView2d(
                modelContext=fileLoader.model,
                spectrumComponent=spectrumComponent,
            )
            editDialog2d.show()
            return


    contextMenuController = ContextMenuController(
        parent=view,
        fileLoader=fileLoader,
        fileSaver=fileSaver,
        openEditViewCallback=openEditDialog,
        refreshViewCallback=refreshAfterFileInput,
    )

    view.setContextMenuController(contextMenuController)


    def onSpectrumChanged(change):
        images = fileLoader.model.getImage()

        if view.getSpectrumComponent() is not None:
            view.getSpectrumComponent().renderDirtyRegion(change)
            view.updateRestoredDataImage(images[PaneType.INVERSE_DATA])

        if editDialog1d is not None and editDialog1d.spectrumComponent is not None:
            editDialog1d.spectrumComponent.renderDirtyRegion(change)

        if editDialog2d is not None and editDialog2d.spectrumComponent is not None:
            editDialog2d.spectrumComponent.renderDirtyRegion(change)

    fileLoader.model.spectrumChangedListener = onSpectrumChanged

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
