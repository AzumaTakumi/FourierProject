import os
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import QFileDialog
from src.model import FourierModelContext

class ImageReader:
	"""2次元画像を処理するストラテジークラス。"""
	def read(self, aPath: str, aLoader) -> None:
		img = Image.open(aPath).convert("RGB")
		imageArray = np.array(img, dtype=np.float64)
		print(f"[判別結果] 2次元画像データ（解像度: {imageArray.shape[1]}x{imageArray.shape[0]}）")
		aLoader.process2DModel(imageArray)

class TextReader:
	"""1次元テキストを処理するストラテジークラス。"""
	def read(self, aPath: str, aLoader) -> None:
		signalData = np.loadtxt(aPath, dtype=np.float64)
		if signalData.size == 0:
			raise ValueError("Empty input file")
		print(f"[判別結果] 1次元信号データ（要素数: {len(signalData)}）")
		aLoader.process1DModel(signalData)

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
		currentDirectory = os.getcwd()
		filePath, _ = QFileDialog.getOpenFileName(
		 self.view,
		 "ファイルを開く",
		 currentDirectory,
		 "すべての対応形式 (*.jpg *.jpeg *.png *.csv *.txt);;画像データ(2次元データ) (*.jpg *.jpeg *.png);;テキストデータ(1次元データ) (*.csv *.txt)"
		)
		return filePath


class FileLoader(FileController):
	"""
	ポリモーフィズムで実現されたファイルローダー
	"""
	def __init__(self, aView) -> None:
		super().__init__(aView)
		self.model = FourierModelContext(lambda _change: None)

		# 1. エラー用のオブジェクトをあらかじめ生成しておく
		self.defaultReader = NullReader()

		# 2. 拡張子とReaderオブジェクトのマッピング
		self.readers = {
		 "": self.defaultReader, # キャンセル時（空文字）の対応
		 ".csv": TextReader(),
		 ".txt": TextReader(),
		 ".jpg": ImageReader(),
		 ".jpeg": ImageReader(),
		 ".png": ImageReader(),
		}

	def start(self) -> bool:
		"""ファイル選択プロセスを開始する。読み込みできた場合はTrue、キャンセル時はFalseを返す。"""
		selectedPath = self.openFileChooser()

		if not selectedPath:
			print("[情報] ファイル選択がキャンセルされました。")
			return False

		self.loadSignalData(selectedPath)
		return True

	def loadSignalData(self, aPath: str) -> None:
		"""
		メッセージの送信（ポリモーフィズム）だけで全ての分岐を処理する。
		"""

		_, fileExtension = os.path.splitext(aPath)

		reader = self.readers.get(fileExtension.lower(), self.defaultReader)

		reader.read(aPath, self)

	def process1DModel(self, aData: np.ndarray) -> None:
		"""1次元データをModelへ送信し、計算結果をViewに反映する"""
		self.model.set1dSourceData(aData)
		print("-> 1次元データをModelへ送信しました。")

	def process2DModel(self, aData: np.ndarray) -> None:
		"""2次元データをModelへ送信し、計算結果をViewに反映する"""
		self.model.set2dSourceData(aData)
		print("-> 2次元データをModelへ送信しました。")

