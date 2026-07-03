import sys
from PyQt6.QtWidgets import QApplication

from src.view.main_window_view import MainWindowView
from src.controller.file_controller import FileLoader
from src.controller.context_menu_controller import ContextMenuController
from src.view.edit_dialog_view_2d import EditDialogView2d
from src.model.pane_type import PaneType
import numpy as np


def main() -> int:
    app = QApplication(sys.argv)

    view = MainWindowView()
    file_loader = FileLoader(view)

    file_loader.start()

    view.display(file_loader.model)


    edit_dialog_2d = None

    def clear_edit_dialog_2d():
        nonlocal edit_dialog_2d
        edit_dialog_2d = None

    def open_edit_dialog_2d():
        nonlocal edit_dialog_2d

        spectrum_component = file_loader.model.getSpectrumComponent()
        images = file_loader.model.getImage()

        spectrum_component.renderAll(
            np.array(images[PaneType.INTERACTIVE_POWER_SPECTRUM])
        )

        edit_dialog_2d = EditDialogView2d(
            modelContext=file_loader.model,
            spectrumComponent=spectrum_component,
        )
        edit_dialog_2d.show()

    

    context_menu_controller = ContextMenuController(
        parent=view,
        fileLoader=file_loader,
        openEditViewCallback=open_edit_dialog_2d,
        refreshViewCallback=lambda: view.display(file_loader.model),
    )

    view.setContextMenuController(context_menu_controller)


    def on_spectrum_changed(change):
        images = file_loader.model.getImage()
        spectrum = np.array(images[PaneType.INTERACTIVE_POWER_SPECTRUM])

        if view.getSpectrumComponent() is not None:
            view.getSpectrumComponent().renderAll(spectrum)
            view._refreshImages()

        if edit_dialog_2d is not None and edit_dialog_2d.spectrumComponent is not None:
            edit_dialog_2d.spectrumComponent.renderAll(spectrum)

    file_loader.model.spectrumChangedListener = on_spectrum_changed

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())