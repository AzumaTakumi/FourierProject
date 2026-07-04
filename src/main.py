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
    file_loader = FileLoader(view)

    if not file_loader.start():
            return 0

    view.display(file_loader.model)

    file_saver = FileSaver(view)

    edit_dialog_1d = None
    edit_dialog_2d = None

    def open_edit_dialog():
        nonlocal edit_dialog_1d, edit_dialog_2d

        spectrum_component = file_loader.model.getSpectrumComponent()
        data = file_loader.model.getData()

        spectrum_component.renderAll(
            np.array(data[PaneType.INTERACTIVE_POWER_SPECTRUM])
        )

        if file_loader.model.is1dModel():
            edit_dialog_1d = EditDialogView1d(
                modelContext=file_loader.model,
                spectrum_component=spectrum_component,
            )
            edit_dialog_1d.show()
            return

        if file_loader.model.is2dModel():
            edit_dialog_2d = EditDialogView2d(
                modelContext=file_loader.model,
                spectrumComponent=spectrum_component,
            )
            edit_dialog_2d.show()
            return


    context_menu_controller = ContextMenuController(
        parent=view,
        fileLoader=file_loader,
        fileSaver=file_saver,
        openEditViewCallback=open_edit_dialog,
        refreshViewCallback=lambda: view.display(file_loader.model),
    )

    view.setContextMenuController(context_menu_controller)


    def on_spectrum_changed(change):
        images = file_loader.model.getImage()

        if view.getSpectrumComponent() is not None:
            view.getSpectrumComponent().renderDirtyRegion(change)
            view.updateRestoredDataImage(images[PaneType.INVERSE_DATA])

        if edit_dialog_1d is not None and edit_dialog_1d.spectrum_component is not None:
            edit_dialog_1d.spectrum_component.renderDirtyRegion(change)

        if edit_dialog_2d is not None and edit_dialog_2d.spectrumComponent is not None:
            edit_dialog_2d.spectrumComponent.renderDirtyRegion(change)

    file_loader.model.spectrumChangedListener = on_spectrum_changed

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
