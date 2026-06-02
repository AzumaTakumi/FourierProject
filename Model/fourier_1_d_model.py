from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_model import FourierModel
from .snapshot import Snapshot

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class Fourier1dModel(FourierModel):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元信号データを扱うモデルである。
    
    波形やサンプル信号などの1次元配列を sourceData として保持し、フーリエ変換結果の実部・虚部・スペクトル、編集用スペクトル、逆変換結果を管理する。
    
    元データが設定されると、FourierTransform によってフーリエ変換を行い、右上のパワースペクトル表示と右下の編集用スペクトル表示を生成する。ユーザーが周波数軸上の成分をクリックして有効・無効を切り替えると、編集用スペクトルを更新し、そのたびに逆フーリエ変換を行って左下の復元波形を更新する。
    """

    # SAFE CODE AREA ˅
    def computeFourierData(self) -> None:
        # 自動生成された公開メソッド名から、実際の計算処理を行う内部メソッドへ委譲する。
        self._computeFourierData()

    def computeInverseData(self) -> None:
        # 編集用スペクトルを使った逆変換処理を内部メソッドへ委譲する。
        self._computeInverseData()

    def getInteractiveSpectrumAtIndex(self, index: int) -> tuple:
        # CommandがUndo用に現在値を取得できるよう、内部取得処理を公開する。
        return self._getInteractiveSpectrumAtIndex(index)
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, sourceData: np.ndarray = np.array([])) -> None:
        """
        Fourier1dModelを初期化する。必要に応じてsourceDataを受け取り、内部状態（スペクトル/表示用データ）を初期化する。
        """

        # FourierModelの初期化を行う。
        super().__init__()

        # 入力となる1次元ソースデータ。フーリエ変換の計算元として保持する。
        self.sourceData: np.ndarray = sourceData

        # 1次元フーリエ変換結果の実部。表示および編集処理の基礎データ。
        self.realPart: np.ndarray | None = None

        # 1次元フーリエ変換結果の虚部。表示および編集処理の基礎データ。
        self.imaginaryPart: np.ndarray | None = None

        # 1次元フーリエ変換結果のパワースペクトル。周波数強度の可視化に利用する。
        self.powerSpectrum: np.ndarray | None = None

        # インタラクティブ操作を反映した1次元スペクトル実部。編集後の状態を保持する。
        self.interactiveRealPart: np.ndarray | None = None

        # インタラクティブ操作を反映した1次元スペクトル虚部。編集後の状態を保持する。
        self.interactiveImaginaryPart: np.ndarray | None = None

        # インタラクティブ操作を反映した1次元パワースペクトル。編集後スペクトルの可視化および逆変換入力に利用する。
        self.interactivePowerSpectrum: np.ndarray | None = None

        # 編集用スペクトルを逆フーリエ変換して得られた1次元データ。左下の復元波形表示に利用され、スペクトル編集が行われるたびに更新される。
        self.inverseData: np.ndarray | None = None

        # SAFE CODE AREA ˅
        # 初期データが渡された場合は、通常のデータ設定経路を通してFFTと逆変換まで初期化する。
        if sourceData is not None and np.asarray(sourceData).size > 0:
            self.setSourceData(sourceData)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.setSourceData ˅
    def setSourceData(self, sourceData: np.ndarray) -> None:
        """
        1次元の元データを設定または更新する。設定後、フーリエ変換結果、パワースペクトル、編集用スペクトル、逆変換結果を再計算できる状態にする。
        """

        # SAFE CODE AREA ˅
        # FFT対象として扱えるよう、入力をfloatの1次元配列へ正規化する。
        data = np.asarray(sourceData, dtype=float)
        if data.ndim != 1:
            raise ValueError("Fourier1dModel sourceData must be a 1-dimensional array.")
        if data.size == 0:
            raise ValueError("Fourier1dModel sourceData must not be empty.")

        # 呼び出し元の配列変更がModel内部へ影響しないようコピーして保持する。
        self.sourceData = data.copy()
        # 元データの変更に合わせてFFT結果を作り直し、編集用スペクトルを初期状態へ戻す。
        self._computeFourierData()
        self.resetSpectrum()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setSourceData ˄


    # GENERATED CODE AREA: method._computeFourierData ˅
    def _computeFourierData(self) -> None:
        """
        現在のsourceDataに対してフーリエ変換を行い、realPart、imaginaryPart、powerSpectrumを生成または更新する。
        """

        # SAFE CODE AREA ˅
        # FourierTransformに元信号を渡し、直近のFFT結果を計算させる。
        self.engine.setFftInputSignal(self.sourceData)
        self.engine.transform()
        # FFT結果の実部・虚部を分けて保持し、パワーは実部^2+虚部^2で計算する。
        self.realPart = self.engine.realPart()
        self.imaginaryPart = self.engine.imaginaryPart()
        self.powerSpectrum = np.square(self.realPart) + np.square(self.imaginaryPart)
        # 編集用スペクトルは元スペクトルとは別配列にして、編集が元データ側を壊さないようにする。
        self.interactiveRealPart, self.interactiveImaginaryPart = np.copy(self.realPart), np.copy(self.imaginaryPart)
        self.interactivePowerSpectrum = np.copy(self.powerSpectrum)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._computeFourierData ˄


    # GENERATED CODE AREA: method._computeInverseData ˅
    def _computeInverseData(self) -> None:
        """
        現在の（編集後を含む）スペクトルから逆フーリエ変換を行い、復元データを生成/更新する。
        """

        # SAFE CODE AREA ˅
        # 編集後の実部・虚部を複素スペクトルへ戻し、IFFTの入力として渡す。
        self.engine.setIfftInputSpectrum(self.interactiveRealPart + 1j * self.interactiveImaginaryPart)
        # 逆変換結果はViewのInverse表示で利用する。
        self.inverseData = self.engine.inverseTransform()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._computeInverseData ˄


    # GENERATED CODE AREA: method.eraseSpectrumAtIndex ˅
    def eraseSpectrumAtIndex(self, index: int) -> None:
        """
        指定されたインデックスの周波数成分を無効化する。interactiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを更新し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        # 存在しない周波数インデックスへ編集しないよう先に検証する。
        self._validateIndex(index)
        # 指定成分の実部・虚部を0にし、その成分の強度表示も0にする。
        self.interactiveRealPart[index] = 0
        self.interactiveImaginaryPart[index] = 0
        self.interactivePowerSpectrum[index] = 0
        # 編集後スペクトルをすぐ逆変換し、Inverse表示を最新化する。
        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtIndex ˄


    # GENERATED CODE AREA: method.restoreSpectrumAtIndex ˅
    def restoreSpectrumAtIndex(self, index: int) -> None:
        """
        指定されたインデックスの周波数成分を、フーリエ変換直後の元スペクトル値に戻す。interactiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを更新し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        # 指定成分が配列範囲内にあることを確認してから復元する。
        self._validateIndex(index)
        # 編集用スペクトルだけをFFT直後の元スペクトル値へ戻す。
        self.interactiveRealPart[index] = self.realPart[index]
        self.interactiveImaginaryPart[index] = self.imaginaryPart[index]
        self.interactivePowerSpectrum[index] = self.powerSpectrum[index]
        # 復元した周波数成分を反映した逆変換結果を再計算する。
        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSpectrumAtIndex ˄


    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˅
    def editSpectrumValueAtIndex(self, index: int, realPart: float, imaginaryPart: float) -> None:
        """
        指定されたインデックスの編集用スペクトル値を、指定された実部と虚部の値に変更する。任意の値への編集や、Undo時の値復元に利用される。
        """

        # SAFE CODE AREA ˅
        # 直接入力やUndoから渡された値で、編集用スペクトルの1成分を書き換える。
        self._validateIndex(index)
        self.interactiveRealPart[index] = realPart
        self.interactiveImaginaryPart[index] = imaginaryPart
        # 表示用パワースペクトルも同じ値に合わせて更新する。
        self.interactivePowerSpectrum[index] = realPart**2 + imaginaryPart**2
        # 直接編集後の復元波形を即座に更新する。
        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˄


    # GENERATED CODE AREA: method.dataChirpSignal ˅
    def dataChirpSignal(self) -> np.ndarray:
        """
        周波数が時間とともに変化するチャープ信号のサンプルデータを生成して返す。
        """

        # SAFE CODE AREA ˅
        # 0秒から1秒までの等間隔サンプルを作り、時間とともに周波数が上がる波を生成する。
        t = np.linspace(0.0, 1.0, 512, endpoint=False)
        return np.sin(2.0 * np.pi * (4.0 * t + 24.0 * t * t))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataChirpSignal ˄


    # GENERATED CODE AREA: method.dataSawtoothWave ˅
    def dataSawtoothWave(self) -> np.ndarray:
        """
        のこぎり波のサンプルデータを生成して返す。
        """

        # SAFE CODE AREA ˅
        # cycles回分の線形増加を小数部として取り出し、-1から1ののこぎり波へ変換する。
        t = np.linspace(0.0, 1.0, 512, endpoint=False)
        cycles = 6.0
        return 2.0 * (cycles * t - np.floor(0.5 + cycles * t))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataSawtoothWave ˄


    # GENERATED CODE AREA: method.dataSquareWave ˅
    def dataSquareWave(self) -> np.ndarray:
        """
        矩形波のサンプルデータを生成して返す。
        """

        # SAFE CODE AREA ˅
        # 正弦波の符号だけを使い、値が1または-1になる矩形波を作る。
        t = np.linspace(0.0, 1.0, 512, endpoint=False)
        return np.where(np.sin(2.0 * np.pi * 6.0 * t) >= 0.0, 1.0, -1.0)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataSquareWave ˄


    # GENERATED CODE AREA: method.dataSampleWave ˅
    def dataSampleWave(self) -> np.ndarray:
        """
        動作確認用の1次元サンプル波形データを生成して返す。
        """

        # SAFE CODE AREA ˅
        # 複数の周波数成分を合成し、スペクトル編集の効果が見えやすいサンプル波形を作る。
        t = np.linspace(0.0, 1.0, 512, endpoint=False)
        return (
            np.sin(2.0 * np.pi * 5.0 * t)
            + 0.5 * np.sin(2.0 * np.pi * 17.0 * t)
            + 0.25 * np.sin(2.0 * np.pi * 43.0 * t)
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataSampleWave ˄


    # GENERATED CODE AREA: method.createSnapshot ˅
    def createSnapshot(self) -> Snapshot:
        """
        現在の1次元モデルの内部状態をSnapshotとして生成する。Undo対象操作の実行前に、sourceData、スペクトル情報、編集用スペクトル、逆変換結果を保存するために使用する。
        """

        # SAFE CODE AREA ˅
        # Undo時に参照共有で状態が壊れないよう、ndarrayはすべてcopyしてSnapshotへ入れる。
        return Snapshot(
            sourceData=np.copy(self.sourceData) if self.sourceData is not None else None,
            realPart=np.copy(self.realPart) if self.realPart is not None else None,
            imaginaryPart=np.copy(self.imaginaryPart) if self.imaginaryPart is not None else None,
            powerSpectrum=np.copy(self.powerSpectrum) if self.powerSpectrum is not None else None,
            interactiveRealPart=np.copy(self.interactiveRealPart) if self.interactiveRealPart is not None else None,
            interactiveImaginaryPart=np.copy(self.interactiveImaginaryPart) if self.interactiveImaginaryPart is not None else None,
            interactivePowerSpectrum=np.copy(self.interactivePowerSpectrum) if self.interactivePowerSpectrum is not None else None,
            inverseData=np.copy(self.inverseData) if self.inverseData is not None else None
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


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        1次元の編集用スペクトルを、フーリエ変換直後の元スペクトル状態に戻す。編集によって変更されたinteractiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを初期状態に戻し、逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        # FFT結果がまだ無い状態ではリセット対象がないため何もしない。
        if self.realPart is None or self.imaginaryPart is None or self.powerSpectrum is None:
            return
        # 編集用スペクトルを元スペクトルのコピーで置き換え、編集履歴の影響を取り除く。
        self.interactiveRealPart = np.copy(self.realPart)
        self.interactiveImaginaryPart = np.copy(self.imaginaryPart)
        self.interactivePowerSpectrum = np.copy(self.powerSpectrum)
        # リセット後のスペクトルから復元波形を作り直す。
        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method._getInteractiveSpectrumAtIndex ˅
    def _getInteractiveSpectrumAtIndex(self, index: int) -> tuple:
        """
        指定された周波数インデックスにおける編集用スペクトルの値を取得する。CommandがUndo用に編集前の実部と虚部を保存する際に利用する。
        """

        # SAFE CODE AREA ˅
        # CommandがUndo前の現在値を保持できるよう、編集用スペクトルから実部・虚部を返す。
        self._validateIndex(index)
        return (
            self.interactiveRealPart[index],
            self.interactiveImaginaryPart[index]
        )
        # SAFE CODE AREA ˄

    # SAFE CODE AREA ˅
    def _validateIndex(self, index: int) -> None:
        # FFTが未計算の場合は編集対象が存在しないため、編集操作を拒否する。
        if self.interactiveRealPart is None or self.interactiveImaginaryPart is None:
            raise ValueError("Fourier data has not been computed.")
        # Pythonの負数インデックスは許可しつつ、配列サイズ外のアクセスは明示的に例外にする。
        if not -self.interactiveRealPart.size <= index < self.interactiveRealPart.size:
            raise IndexError(f"Spectrum index out of range: {index}")
    # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._getInteractiveSpectrumAtIndex ˄
