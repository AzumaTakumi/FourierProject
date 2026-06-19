import sys
from PyQt6.QtWidgets import QApplication
# 1. 読み込むViewを FourierView から MainWindowView（およびコンポーネント）に変更
from src.view.main_window_view import MainWindowView, Interactive2dSpectrumComponent
from src.controller.file_controller import FileLoader

def main() -> int:
    """
    アプリケーションのメインプログラムです。
    """
    app = QApplication(sys.argv)
    
    # 2. 編集可能な2次元スペクトルコンポーネントを生成
    spectrum_component = Interactive2dSpectrumComponent()
    
    # 3. 本命の MainWindowView を生成（引数にコンポーネントを渡す）
    view = MainWindowView(spectrum_component)
    
    # ※ 注意：MainWindowViewの画面表示は、データを流し込む `view.display(...)` 内で
    # self.show() が呼ばれる設計になっているため、ここでは一旦 view.show() をコメントアウト、
    # もしくは仮表示させておきます。
    # view.show() 

    # 4. Controllerを生成（引数に新しいViewを渡して紐付ける）
    file_loader = FileLoader(view)
    
    # 5. Controller側でファイル選択画面を表示・処理させる
    file_loader.start()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())