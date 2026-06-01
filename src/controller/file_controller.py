import os
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import QFileDialog

class ImageReader:
	"""2次元画像を処理するストラテジークラス。"""
	def read(self, aPath: str, aLoader) -> None:
		img = Image.open(aPath).convert("RGB")
		image_array = np.array(img, dtype=np.float64)
		print(f"[判別結果] 2次元画像データ（解像度: {image_array.shape[1]}x{image_array.shape[0]}）")
		aLoader.process2DModel(image_array)

class TextReader:
	"""1次元テキストを処理するストラテジークラス。"""
	def read(self, aPath: str, aLoader) -> None:
		signal_data = np.loadtxt(aPath, dtype=np.float64)
		print(f"[判別結果] 1次元信号データ（要素数: {len(signal_data)}）")
		aLoader.process1DModel(signal_data)

class NullReader:
	"""未対応の拡張子や、キャンセル時に呼び出される身代わりクラス。"""
	def read(self, aPath: str, aLoader) -> None:
		print(f"[エラー] 未対応のファイル形式、または選択がキャンセルされました: {aPath}")


class FileController:
	"""ファイル操作を管理する抽象コントローラークラス。"""
	def __init__(self, aView) -> None:
		self.view = aView

	def openFileChooser(self) -> str:
		"""Finderをポップアップ表示します。キャンセル時は空文字("")が返ります。"""
		current_directory = os.getcwd()
		file_path, _ = QFileDialog.getOpenFileName(
			self.view,
			"ファイルを開く",
			current_directory,
			"すべての対応形式 (*.png *.bmp *.csv *.txt);;画像ファイル (*.png *.bmp);;テキストデータ (*.csv *.txt)"
		)
		return file_path


class FileLoader(FileController):
	"""
	ポリモーフィズムで実現されたファイルローダー
	"""
	def __init__(self, aView) -> None:
		super().__init__(aView)
		
		# 1. エラー用のオブジェクトをあらかじめ生成しておく
		self.default_reader = NullReader()
		
		# 2. 拡張子とReaderオブジェクトのマッピング
		self.readers = {
			"": self.default_reader, # キャンセル時（空文字）の対応
			".csv": TextReader(),
			".txt": TextReader(),
			".png": ImageReader(),
			".bmp": ImageReader()
		}

	def start(self) -> None:
		"""ファイル選択プロセスを開始する。"""
		selected_path = self.openFileChooser()
		self.loadSignalData(selected_path)

	def loadSignalData(self, aPath: str) -> None:
		"""
		メッセージの送信（ポリモーフィズム）だけで全ての分岐を処理する。
		"""
		# 拡張子を切り出す
		_, file_extension = os.path.splitext(aPath)
		
		# 辞書からReaderを取得。もし登録のない拡張子なら、エラー用Reader（default_reader）を返す。
		reader = self.readers.get(file_extension.lower(), self.default_reader)
		
		# 信頼してメッセージを送る。相手の正体が何であれ、if文なしで1行で完結。
		reader.read(aPath, self)

	def process1DModel(self, aData: np.ndarray) -> None:
		# modelオブジェクトが持つ「データセット用関数」に、NumPy配列をいれる
		# self.model.Fourier1dModel.setSourceData(aData)　modelの関数が決まったらここのコメントアウトを取る
		print("-> 1次元データをModelへデータを送信しました。")
        
	def process2DModel(self, aData: np.ndarray) -> None:
		# modelオブジェクトが持つ「データセット用関数」に、NumPy配列を入れる。
		# self.model.Fourier1dModel.setSourceData(aData)  modelの関数が決まったらここのコメントアウトを取る
		print("-> 2次元データをModelへデータを送信しました。")
		