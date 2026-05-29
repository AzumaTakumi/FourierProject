from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from PIL import Image

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class FourierRenderer(object):
    # GENERATED CODE AREA: class.header ˅
    """
    数値データを表示用画像に変換するクラスである。
    
    1次元データ、2次元画像データ、スペクトル、実部・虚部などを受け取り、表示や保存に利用できるPIL.Imageを生成する。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.setAccuracy ˅
    def setAccuracy(self, accuracy: float) -> None:
        """
        レンダリング設定（accuracy）を設定する。以後の画像生成処理に反映される。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setAccuracy ˄


    # GENERATED CODE AREA: method.setImageWidth ˅
    def setImageWidth(self, imageWidth: int) -> None:
        """
        レンダリング設定（imageWidth）を設定する。以後の画像生成処理に反映される。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setImageWidth ˄


    # GENERATED CODE AREA: method.setImageHeight ˅
    def setImageHeight(self, imageHeight: int) -> None:
        """
        レンダリング設定（imageHeight）を設定する。以後の画像生成処理に反映される。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setImageHeight ˄


    # GENERATED CODE AREA: method.imageFrom1dData ˅
    def imageFrom1dData(self, data: np.ndarray) -> Image.Image:
        """
        1次元配列データを可視化用Imageに変換して返す。波形/スペクトルなどの1Dデータ表示に用いる。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.imageFrom1dData ˄


    # GENERATED CODE AREA: method.imageFromSpectrum ˅
    def imageFromSpectrum(self, spectrum: np.ndarray) -> Image.Image:
        """
        スペクトル行列を可視化用に正規化/スケーリングし、Imageとして返す。パワースペクトル表示などに用いる。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.imageFromSpectrum ˄


    # GENERATED CODE AREA: method.imageFromParts ˅
    def imageFromParts(self, realPart: np.ndarray, imaginaryPart: np.ndarray) -> Image.Image:
        """
        実部/虚部から複素スペクトルの表示用画像を生成して返す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.imageFromParts ˄


    # GENERATED CODE AREA: method.normalize ˅
    def normalize(self, data: np.ndarray) -> np.ndarray:
        """
        可視化のためにデータを所定レンジへ正規化したndarrayを返す（例: min-max、logスケール等）。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.normalize ˄

