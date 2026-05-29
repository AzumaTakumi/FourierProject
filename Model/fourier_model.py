from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .fourier_transform import FourierTransform

# GENERATED CODE AREA: module.imports ˄

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

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, engine: FourierTransform) -> None:
        """
        FourierModelを初期化する。計算処理を担当するFourierTransformを受け取り、共通状態を初期化する。
        """

        # 計算処理を担当するCalculationEngine。フーリエ変換/逆変換などの実処理を委譲する。
        self.engine: FourierTransform = None

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        編集用スペクトルを、フーリエ変換直後の元スペクトル状態に戻す。interactiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを元のrealPart、imaginaryPart、powerSpectrumに基づいて復元し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method.getData ˅
    def getData(self) -> dict:
        """
        各表示領域に対応するデータを取得する。PaneTypeをキー、np.ndarrayを値とする辞書を返し、View側はこのデータを用いて元データ、パワースペクトル、編集用パワースペクトル、逆変換結果を描画する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getData ˄


    # GENERATED CODE AREA: method.getImage ˅
    def getImage(self) -> dict:
        """
        各表示領域に対応する画像データを取得する。PaneTypeをキー、PIL.Imageを値とする辞書を返し、View側や保存処理で画像として扱う場合に利用する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getImage ˄

