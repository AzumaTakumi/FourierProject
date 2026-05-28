import sys
from PyQt6.QtWidgets import QApplication
from src.view.fourier_view import FourierView
from src.controller.file_controller import FileLoader

def main() -> int:
	"""
	アプリケーションのメインプログラム。
	"""
	app = QApplication(sys.argv)
	
	# 1. View（画面）を生成
	view = FourierView()
	view.show()
	
	# 2. Controllerを生成（引数にViewを渡して紐付ける）
	file_loader = FileLoader(view)
	
	# 3. Controller側でファイル選択画面を表示・処理させる
	file_loader.start()
	
	return app.exec()

if __name__ == "__main__":
	sys.exit(main())