from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_model import FourierModel

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
    # 追加メソッドは定義しない。処理本体は各生成メソッド内のSAFE CODE AREAへ記述する。
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
        self.computeFourierData()
        self.resetSpectrum()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setSourceData ˄


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


    # GENERATED CODE AREA: method._validateIndex ˅
    def _validateIndex(self, index: int) -> None:
        """
        1Dスペクトルindexの範囲チェック
        """

        # SAFE CODE AREA ˅
        # FFTが未計算の場合は編集対象が存在しないため、編集操作を拒否する。
        if self.interactiveRealPart is None or self.interactiveImaginaryPart is None:
            raise ValueError("Fourier data has not been computed.")
        # Pythonの負数インデックスは許可しつつ、配列サイズ外のアクセスは明示的に例外にする。
        if not -self.interactiveRealPart.size <= index < self.interactiveRealPart.size:
            raise IndexError(f"Spectrum index out of range: {index}")
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._validateIndex ˄


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
        self.computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˄


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
        self.computeInverseData()
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
        self.computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSpectrumAtIndex ˄


    # FIXED CODE AREA: method.getInteractiveSpectrumAtIndex ˅
    def getInteractiveSpectrumAtIndex(self, index: int) -> tuple[float, float]:
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
    # FIXED CODE AREA: method.getInteractiveSpectrumAtIndex ˄
