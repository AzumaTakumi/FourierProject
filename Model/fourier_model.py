from __future__ import annotations

# FIXED CODE AREA: module.imports ˅
import numpy as np
from .fourier_transform import FourierTransform
from .fourier_renderer import FourierRenderer
from .pane_type import PaneType

# FIXED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class FourierModel(object):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元モデルと2次元モデルに共通する抽象的なフーリエモデルである。
    
    Fourier1dModel と Fourier2dModel の親クラスとして、計算処理を担当する FourierTransform を保持し、表示用データの取得、画像データの取得、編集用スペクトルのリセットなど、1Dと2Dに共通する操作を定義する。
    
    このクラス自体は具体的な元データの次元を持たず、1次元固有・2次元固有の処理は子クラスで実装する。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self) -> None:
        """
        FourierModelを初期化する。計算処理を担当するFourierTransformを受け取り、共通状態を初期化する。
        """

        # 計算処理を担当するCalculationEngine。フーリエ変換/逆変換などの実処理を委譲する。
        self.engine: FourierTransform = FourierTransform()

        # SAFE CODE AREA ˅
        self.renderer: FourierRenderer = FourierRenderer()
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        編集用スペクトルを、フーリエ変換直後の元スペクトル状態に戻す。interactiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを元のrealPart、imaginaryPart、powerSpectrumに基づいて復元し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        real_part = getattr(self, "realPart", None)
        imaginary_part = getattr(self, "imaginaryPart", None)
        power_spectrum = getattr(self, "powerSpectrum", None)
        self.interactiveRealPart = np.copy(real_part) if real_part is not None else None
        self.interactiveImaginaryPart = np.copy(imaginary_part) if imaginary_part is not None else None
        self.interactivePowerSpectrum = np.copy(power_spectrum) if power_spectrum is not None else None
        try:
            self._computeInverseData()
        except AttributeError:
            pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method.getData ˅
    def getData(self) -> dict:
        """
        各表示領域に対応するデータを取得する。PaneTypeをキー、np.ndarrayを値とする辞書を返し、View側はこのデータを用いて元データ、パワースペクトル、編集用パワースペクトル、逆変換結果を描画する。
        """

        # SAFE CODE AREA ˅
        return {
            PaneType.SOURCE_DATA: getattr(self, "sourceData", None),
            PaneType.POWER_SPECTRUM: getattr(self, "powerSpectrum", None),
            PaneType.INTERACTIVE_POWER_SPECTRUM: getattr(self, "interactivePowerSpectrum", None),
            PaneType.INVERSE_DATA: getattr(self, "inverseData", None),
        }
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getData ˄


    # GENERATED CODE AREA: method.getImage ˅
    def getImage(self) -> dict:
        """
        各表示領域に対応する画像データを取得する。PaneTypeをキー、PIL.Imageを値とする辞書を返し、View側や保存処理で画像として扱う場合に利用する。
        """

        # SAFE CODE AREA ˅
        data_map = self.getData()
        image_map: dict = {}
        render_1d = self.renderer.imageFrom1dData
        render_2d = self.renderer.imageFromSpectrum
        renderers = {1: render_1d}
        for pane_type, data in data_map.items():
            renderer = renderers.get(getattr(data, "ndim", 0), render_2d)
            image_map[pane_type] = ((lambda: renderer(data)), (lambda: None))[data is None]()
        return image_map
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getImage ˄

