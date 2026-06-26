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
        # 具体Model側でPaneTypeごとの描画関数を設定する。
        self.imageRenderers = {}
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.computeInverseData ˅
    def computeInverseData(self) -> None:
        """
        現在の（編集後を含む）スペクトルから逆フーリエ変換を行い、復元データを生成/更新する。
        """

        # SAFE CODE AREA ˅
        # 編集後の実部・虚部を複素スペクトルへ戻し、IFFTの入力として渡す。
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
        source_data = self.sourceData
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
        real_part = self.realPart
        imaginary_part = self.imaginaryPart
        power_spectrum = self.powerSpectrum
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
            sourceData=np.copy(self.sourceData),
            realPart=np.copy(self.realPart),
            imaginaryPart=np.copy(self.imaginaryPart),
            powerSpectrum=np.copy(self.powerSpectrum),
            interactiveRealPart=np.copy(self.interactiveRealPart),
            interactiveImaginaryPart=np.copy(self.interactiveImaginaryPart),
            interactivePowerSpectrum=np.copy(self.interactivePowerSpectrum),
            inverseData=np.copy(self.inverseData),
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
        self.sourceData = np.copy(snapshot.sourceData)
        self.realPart = np.copy(snapshot.realPart)
        self.imaginaryPart = np.copy(snapshot.imaginaryPart)
        self.powerSpectrum = np.copy(snapshot.powerSpectrum)
        self.interactiveRealPart = np.copy(snapshot.interactiveRealPart)
        self.interactiveImaginaryPart = np.copy(snapshot.interactiveImaginaryPart)
        self.interactivePowerSpectrum = np.copy(snapshot.interactivePowerSpectrum)
        self.inverseData = np.copy(snapshot.inverseData)
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
            PaneType.SOURCE_DATA: self.sourceData,
            PaneType.POWER_SPECTRUM: self.powerSpectrum,
            PaneType.INTERACTIVE_POWER_SPECTRUM: self.interactivePowerSpectrum,
            PaneType.INVERSE_DATA: self.inverseData,
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
        return {
            pane_type: None if data is None else self.imageRenderers[pane_type](data)
            for pane_type, data in data_map.items()
        }
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
