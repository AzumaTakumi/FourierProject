# ここのクラスの管理は結果出力画面を作成するときに変更をお願いします。現在は仮にコードを書いています。

from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class FourierView(QMainWindow):
	"""
	アプリケーションのメインウィンドウ（View）を表示するクラス。
	"""
	def __init__(self) -> None:
		super().__init__()
		self.setupUI()

	def setupUI(self) -> None:
		"""
		画面の初期レイアウトを構築する。
		"""
		self.setWindowTitle("フーリエ変換信号処理アプリケーション")
		self.resize(800, 600)
		
		# メインコンテンツエリアの配置
		central_widget = QWidget(self)
		layout = QVBoxLayout(central_widget)
		
		label = QLabel("ここに画像やスペクトルが表示される予定。", central_widget)
		layout.addWidget(label)
		
		self.setCentralWidget(central_widget)
