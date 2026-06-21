from __future__ import annotations

# FIXED CODE AREA: module.imports ˅
import numpy as np
from PIL import Image
from .fourier_transform import FourierTransform
from .fourier_renderer import FourierRenderer
from .pane_type import PaneType

# FIXED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
from .snapshot import Snapshot
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
        # Rendererの生成メソッドとクラスメソッドの両方を同じ呼び方で使えるよう、インスタンスを保持する。
        self.renderer = FourierRenderer()
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.computeInverseData ˅
    def computeInverseData(self) -> None:
        """
        現在の（編集後を含む）スペクトルから逆フーリエ変換を行い、復元データを生成/更新する。
        """

        # SAFE CODE AREA ˅
        # 編集後の実部・虚部を複素スペクトルへ戻し、IFFTの入力として渡す。
        if self.interactiveRealPart is None or self.interactiveImaginaryPart is None:
            raise ValueError("Interactive Fourier data has not been computed.")
        self.engine.setIfftInputSpectrum(self.interactiveRealPart + 1j * self.interactiveImaginaryPart)
        # 逆変換結果はViewのInverse表示で利用する。
        self.inverseData = self.engine.inverseTransform()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.computeInverseData ˄


    # GENERATED CODE AREA: method.computeFourierData ˅
    def computeFourierData(self) -> None:
        """
        現在のsourceDataに対して2次元フーリエ変換を行い、realPart、imaginaryPart、powerSpectrumを生成または更新する。
        """

        # SAFE CODE AREA ˅
        # FourierTransformに元データを渡し、直近のFFT結果を計算させる。
        source_data = getattr(self, "sourceData", None)
        if source_data is None:
            raise ValueError("Source data has not been set.")
        self.engine.setFftInputSignal(source_data)
        self.engine.transform()
        # FFT結果の実部・虚部を分けて保持し、パワーは実部^2+虚部^2で計算する。
        self.realPart = self.engine.realPart()
        self.imaginaryPart = self.engine.imaginaryPart()
        self.powerSpectrum = np.square(self.realPart) + np.square(self.imaginaryPart)
        # 編集用スペクトルは元スペクトルとは別配列にして、編集が元データ側を壊さないようにする。
        self.interactiveRealPart = np.copy(self.realPart)
        self.interactiveImaginaryPart = np.copy(self.imaginaryPart)
        self.interactivePowerSpectrum = np.copy(self.powerSpectrum)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.computeFourierData ˄


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        編集用スペクトルを、フーリエ変換直後の元スペクトル状態に戻す。interactiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを元のrealPart、imaginaryPart、powerSpectrumに基づいて復元し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        # 子クラスが持つFFT結果を共通処理で扱えるよう、属性名で取得する。
        real_part = getattr(self, "realPart", None)
        imaginary_part = getattr(self, "imaginaryPart", None)
        power_spectrum = getattr(self, "powerSpectrum", None)
        if real_part is None or imaginary_part is None or power_spectrum is None:
            return
        # 編集用スペクトルを元スペクトルのコピーへ戻し、以降の編集が元スペクトルを変更しないようにする。
        self.interactiveRealPart = np.copy(real_part)
        self.interactiveImaginaryPart = np.copy(imaginary_part)
        self.interactivePowerSpectrum = np.copy(power_spectrum)
        # リセット後のスペクトルから復元データを作り直す。
        self.computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method.createSnapshot ˅
    def createSnapshot(self) -> Snapshot:
        """
        現在の1次元モデルの内部状態をSnapshotとして生成する。Undo対象操作の実行前に、sourceData、スペクトル情報、編集用スペクトル、逆変換結果を保存するために使用する。
        """

        # SAFE CODE AREA ˅
        # Undo時に参照共有で状態が壊れないよう、ndarrayはすべてcopyしてSnapshotへ入れる。
        return Snapshot(
            sourceData=np.copy(getattr(self, "sourceData", None)) if getattr(self, "sourceData", None) is not None else None,
            realPart=np.copy(getattr(self, "realPart", None)) if getattr(self, "realPart", None) is not None else None,
            imaginaryPart=np.copy(getattr(self, "imaginaryPart", None)) if getattr(self, "imaginaryPart", None) is not None else None,
            powerSpectrum=np.copy(getattr(self, "powerSpectrum", None)) if getattr(self, "powerSpectrum", None) is not None else None,
            interactiveRealPart=np.copy(getattr(self, "interactiveRealPart", None)) if getattr(self, "interactiveRealPart", None) is not None else None,
            interactiveImaginaryPart=np.copy(getattr(self, "interactiveImaginaryPart", None)) if getattr(self, "interactiveImaginaryPart", None) is not None else None,
            interactivePowerSpectrum=np.copy(getattr(self, "interactivePowerSpectrum", None)) if getattr(self, "interactivePowerSpectrum", None) is not None else None,
            inverseData=np.copy(getattr(self, "inverseData", None)) if getattr(self, "inverseData", None) is not None else None,
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.createSnapshot ˄


    # GENERATED CODE AREA: method.restoreSnapshot ˅
    def restoreSnapshot(self, snapshot: Snapshot) -> None:
        """
        指定されたSnapshotの内容を用いて、1次元モデルの内部状態を復元する。Undo処理などで、sourceData、スペクトル情報、編集用スペクトル、逆変換結果を以前の状態へ戻すために使用する。
        """

        # SAFE CODE AREA ˅
        # Snapshot内の配列も再度copyし、復元後のModel編集がSnapshot側へ影響しないようにする。
        self.sourceData = np.copy(snapshot.sourceData) if snapshot.sourceData is not None else None
        self.realPart = np.copy(snapshot.realPart) if snapshot.realPart is not None else None
        self.imaginaryPart = np.copy(snapshot.imaginaryPart) if snapshot.imaginaryPart is not None else None
        self.powerSpectrum = np.copy(snapshot.powerSpectrum) if snapshot.powerSpectrum is not None else None
        self.interactiveRealPart = np.copy(snapshot.interactiveRealPart) if snapshot.interactiveRealPart is not None else None
        self.interactiveImaginaryPart = np.copy(snapshot.interactiveImaginaryPart) if snapshot.interactiveImaginaryPart is not None else None
        self.interactivePowerSpectrum = np.copy(snapshot.interactivePowerSpectrum) if snapshot.interactivePowerSpectrum is not None else None
        self.inverseData = np.copy(snapshot.inverseData) if snapshot.inverseData is not None else None
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSnapshot ˄


    # FIXED CODE AREA: method.getData ˅
    def getData(self) -> dict[PaneType, np.ndarray | None]:
        """
        各表示領域に対応するデータを取得する。PaneTypeをキー、np.ndarrayを値とする辞書を返し、View側はこのデータを用いて元データ、パワースペクトル、編集用パワースペクトル、逆変換結果を描画する。
        """

        # SAFE CODE AREA ˅
        # Viewが4つの表示領域を同じ形式で取得できるよう、PaneTypeをキーにして現在データを返す。
        return {
            PaneType.SOURCE_DATA: getattr(self, "sourceData", None),
            PaneType.POWER_SPECTRUM: getattr(self, "powerSpectrum", None),
            PaneType.INTERACTIVE_POWER_SPECTRUM: getattr(self, "interactivePowerSpectrum", None),
            PaneType.INVERSE_DATA: getattr(self, "inverseData", None),
        }
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.getData ˄


    # FIXED CODE AREA: method.getImage ˅
    def getImage(self) -> dict[PaneType, Image.Image | None]:
        """
        各表示領域に対応する画像データを取得する。PaneTypeをキー、PIL.Imageを値とする辞書を返し、View側や保存処理で画像として扱う場合に利用する。
        """

        # SAFE CODE AREA ˅
        # getDataで取得した数値配列を、PaneTypeごとに適切な描画方法へ振り分ける。
        data_map = self.getData()
        image_map: dict[PaneType, Image.Image | None] = {}
        for pane_type, data in data_map.items():
            if data is None:
                # 未初期化ペインはView側で空表示にできるようNoneのまま返す。
                image_map[pane_type] = None
            elif getattr(data, "ndim", 0) == 1:
                # 1次元データは画像ではなく波形として折れ線描画する。
                image_map[pane_type] = self.renderer.imageFrom1dData(data)
            elif pane_type in [PaneType.SOURCE_DATA, PaneType.INVERSE_DATA]:
                # 元画像と逆変換画像は、画素値としてそのまま見える画像へ変換する。
                image_map[pane_type] = self.renderer.imageFromImageData(data)
            else:
                # スペクトル系ペインはlogスケール・fftshift込みのスペクトル画像として描画する。
                image_map[pane_type] = self.renderer.imageFromSpectrum(data)
        return image_map
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.getImage ˄

    # GENERATED CODE AREA: method.getSpectrumComponent ˅
    def getSpectrumComponent(self):
        """
        現在のModelに対応する編集用スペクトルコンポーネントを取得する。
        """

        # SAFE CODE AREA ˅
        # Fourier1dModel / Fourier2dModel がそれぞれ対応するComponentを返すため、
        # 親クラスでは実装せず子クラスへ処理を委譲する。
        raise NotImplementedError
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getSpectrumComponent ˄    

