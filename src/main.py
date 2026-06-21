import sys
from PyQt6.QtWidgets import QApplication
# 1. 読み込むViewを FourierView から MainWindowView（およびコンポーネント）に変更

from src.view.main_window_view import MainWindowView
from src.controller.file_controller import FileLoader

def main() -> int:
    """
    アプリケーションのメインプログラムです。
    """
    app = QApplication(sys.argv)

    view = MainWindowView()
    file_loader = FileLoader(view)

    file_loader.model.spectrumChangedListener = lambda change: view.display(file_loader.model)

    file_loader.start()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())