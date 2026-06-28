import sys
from PyQt6.QtWidgets import QApplication

from src.view.main_window_view import MainWindowView
from src.controller.file_controller import FileLoader
from src.controller.context_menu_controller import ContextMenuController

def main() -> int:
    app = QApplication(sys.argv)

    view = MainWindowView()
    file_loader = FileLoader(view)

    file_loader.start()

    view.display(file_loader.model)

    

    context_menu_controller = ContextMenuController(
        parent=view,
        fileLoader=file_loader,
        refreshViewCallback=lambda: view.display(file_loader.model),
    )
    view.setContextMenuController(context_menu_controller)



    file_loader.model.spectrumChangedListener = (
        view.getSpectrumComponent().renderDirtyRegion
    )

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())