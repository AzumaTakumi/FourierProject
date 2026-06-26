import sys
from PyQt6.QtWidgets import QApplication

from src.view.main_window_view import MainWindowView
from src.controller.file_controller import FileLoader

def main() -> int:
    app = QApplication(sys.argv)

    view = MainWindowView()
    file_loader = FileLoader(view)

    file_loader.start()

    view.display(file_loader.model)
    file_loader.model.spectrumChangedListener = (
        view.getSpectrumComponent().renderDirtyRegion
    )

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())