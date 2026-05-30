from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_model import FourierModel
from .snapshot import Snapshot

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class Fourier2dModel(FourierModel):
    # GENERATED CODE AREA: class.header ˅
    """
    2次元画像データを扱うモデルである。
    
    画像の輝度行列またはRGB画像配列をsourceDataとして保持し、フーリエ変換結果の実部・虚部・パワースペクトル、編集用スペクトル、逆変換結果を管理する。
    
    ユーザー操作によりスペクトルが編集されると、編集用スペクトルを更新し、逆フーリエ変換によって復元画像データを再計算する。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, sourceData: np.ndarray | None = None) -> None:
        """
        Fourier2dModelを初期化する。必要に応じてsourceDataを受け取り、内部状態として各スペクトル、編集用スペクトル、逆変換結果を初期化する。
        """

        # FourierModelの初期化を行う。
        super().__init__()

        # 入力となる2次元ソースデータ（元画像/元行列）。フーリエ変換の計算元として保持する。
        self.sourceData: np.ndarray | None = sourceData

        # 2次元フーリエ変換結果の実部。engine計算結果を保持し、描画用データ生成に利用する。
        self.realPart: np.ndarray | None = None

        # 2次元フーリエ変換結果の虚部。engine計算結果を保持し、描画用データ生成に利用する。
        self.imaginaryPart: np.ndarray | None = None

        # 2次元フーリエ変換結果のパワースペクトル（振幅^2等）。可視化の主対象となるスペクトル強度を保持する。
        self.powerSpectrum: np.ndarray | None = None

        # インタラクティブ操作（周波数成分の除去/復元等）を反映した実部。UI編集後の状態を保持する。
        self.interactiveRealPart: np.ndarray | None = None

        # インタラクティブ操作（周波数成分の除去/復元等）を反映した虚部。UI編集後の状態を保持する。
        self.interactiveImaginaryPart: np.ndarray | None = None

        # インタラクティブ操作を反映したパワースペクトル。編集後スペクトルの可視化および逆変換入力に利用する。
        self.interactivePowerSpectrum: np.ndarray | None = None

        # 編集用スペクトルを逆フーリエ変換して得られた2次元画像データ。左下の復元画像表示に利用され、スペクトル編集が行われるたびに更新される。
        self.inverseData: np.ndarray | None = None

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.setSourceData ˅
    def setSourceData(self, sourceData: np.ndarray) -> None:
        """
        2次元の元データを設定または更新する。設定後、フーリエ変換結果、パワースペクトル、編集用スペクトル、逆変換結果を再計算できる状態にする。
        """

        # SAFE CODE AREA ˅
        self.sourceData = sourceData
        self._computeFourierData()
        self.resetSpectrum()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setSourceData ˄


    # GENERATED CODE AREA: method._fill ˅
    def _fill(self, value: float) -> None:
        """
        指定したndarray全体を同一値で埋めるユーティリティ。初期化やマスク生成に利用する。
        """

        # SAFE CODE AREA ˅
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._fill ˄


    # GENERATED CODE AREA: method._computeFourierData ˅
    def _computeFourierData(self) -> None:
        """
        現在のsourceDataに対して2次元フーリエ変換を行い、realPart、imaginaryPart、powerSpectrumを生成または更新する。
        """

        # SAFE CODE AREA ˅
        self.engine.setFftInputSignal(self.sourceData)
        self.engine.transform()
        self.realPart = self.engine.realPart()
        self.imaginaryPart = self.engine.imaginaryPart()
        self.powerSpectrum = np.square(self.realPart) + np.square(self.imaginaryPart)
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
        self.engine.setIfftInputSpectrum(self.interactiveRealPart + 1j * self.interactiveImaginaryPart)
        self.inverseData = self.engine.inverseTransform()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._computeInverseData ˄


    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˅
    def eraseSpectrumAtPosition(self, row: int, col: int, radius: int) -> None:
        """
        指定された行、列、半径に対応する2次元スペクトル範囲を無効化する。interactiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを更新し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        try:
            height, width = self.interactiveRealPart.shape[:2]
            _ = self.interactiveImaginaryPart.shape
            _ = self.interactivePowerSpectrum.shape
        except Exception:
            return

        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))

        r0 = max(0, row - radius)
        r1 = min(height, row + radius + 1)
        c0 = max(0, col - radius)
        c1 = min(width, col + radius + 1)

        rr, cc = np.ogrid[r0:r1, c0:c1]
        mask = (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2

        real_view = self.interactiveRealPart[r0:r1, c0:c1]
        imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]
        real_view[mask] = 0
        imag_view[mask] = 0

        power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]
        power_view[mask] = 0

        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˅
    def paintRgbSpectrumAtPosition(self, row: int, col: int, radius: int, rgbColor: list) -> None:
        """
        指定された行、列、半径に対応する2次元スペクトル範囲を、RGB色に基づいて編集する。編集結果をinteractiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumに反映し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        try:
            height, width = self.interactiveRealPart.shape[:2]
            _ = self.interactiveImaginaryPart.shape
            _ = self.interactivePowerSpectrum.shape
        except Exception:
            return

        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))

        r0 = max(0, row - radius)
        r1 = min(height, row + radius + 1)
        c0 = max(0, col - radius)
        c1 = min(width, col + radius + 1)

        rr, cc = np.ogrid[r0:r1, c0:c1]
        mask = (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2

        real_view = self.interactiveRealPart[r0:r1, c0:c1]
        imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]

        color = np.asarray(rgbColor, dtype=real_view.dtype).reshape(-1)
        try:
            _ = color[0]
        except IndexError as exc:
            raise ValueError("rgbColor が空です。少なくとも1つ以上の数値を指定してください。空配列は塗りつぶし値に変換できません。") from exc
        paint_scalar = float(np.mean(color[:3]))
        real_view[mask] = paint_scalar
        imag_view[mask] = 0

        power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]
        power_view[mask] = np.square(real_view[mask]) + np.square(imag_view[mask])

        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.restoreInteractiveSpectrumAtPosition ˅
    def restoreInteractiveSpectrumAtPosition(self, row: int, col: int, radius: int, realPart: np.ndarray, imaginaryPart: np.ndarray) -> None:
        """
        Undo操作で値を戻す際に使用する。restoreSpectrumAtPosition(row, col, radius)で戻す操作は不適切であり、本来戻す可能性がある値と異なるため、この操作を追加した。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        try:
            height, width = self.interactiveRealPart.shape[:2]
            _ = self.interactiveImaginaryPart.shape
            _ = self.interactivePowerSpectrum.shape
        except Exception:
            return

        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))

        r0 = max(0, row - radius)
        r1 = min(height, row + radius + 1)
        c0 = max(0, col - radius)
        c1 = min(width, col + radius + 1)

        rr, cc = np.ogrid[r0:r1, c0:c1]
        mask = (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2

        real_view = self.interactiveRealPart[r0:r1, c0:c1]
        imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]

        old_real = np.asarray(realPart)
        old_imag = np.asarray(imaginaryPart)

        try:
            real_view[...] = old_real
            imag_view[...] = old_imag
        except ValueError:
            real_view[mask] = old_real
            imag_view[mask] = old_imag

        power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]
        power_view[...] = np.square(real_view) + np.square(imag_view)

        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreInteractiveSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.dataColorImage ˅
    def dataColorImage(self) -> np.ndarray:
        """
        動作確認用のカラー画像サンプルデータを生成して返す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataColorImage ˄


    # GENERATED CODE AREA: method.dataGrayScaleImage ˅
    def dataGrayScaleImage(self) -> np.ndarray:
        """
        動作確認用のグレースケール画像サンプルデータを生成して返す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataGrayScaleImage ˄


    # GENERATED CODE AREA: method.createSnapshot ˅
    def createSnapshot(self) -> Snapshot:
        """
        現在の2次元モデルの内部状態をSnapshotとして生成する。Undo対象操作の実行前に、sourceData、スペクトル情報、編集用スペクトル、逆変換結果を保存するために使用する。
        """

        # SAFE CODE AREA ˅
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
        指定されたSnapshotの内容を用いて、2次元モデルの内部状態を復元する。Undo処理などで、sourceData、スペクトル情報、編集用スペクトル、逆変換結果を以前の状態へ戻すために使用する。
        """

        # SAFE CODE AREA ˅
        self.sourceData = snapshot.sourceData
        self.realPart = snapshot.realPart
        self.imaginaryPart = snapshot.imaginaryPart
        self.powerSpectrum = snapshot.powerSpectrum
        self.interactiveRealPart = snapshot.interactiveRealPart
        self.interactiveImaginaryPart = snapshot.interactiveImaginaryPart
        self.interactivePowerSpectrum = snapshot.interactivePowerSpectrum
        self.inverseData = snapshot.inverseData
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSnapshot ˄


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        2次元の編集用スペクトルを、フーリエ変換直後の元スペクトル状態に戻す。編集によって変更されたinteractiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを初期状態に戻し、逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        self.interactiveRealPart = np.copy(self.realPart)
        self.interactiveImaginaryPart = np.copy(self.imaginaryPart)
        self.interactivePowerSpectrum = np.copy(self.powerSpectrum)
        
        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method._getInteractiveSpectrumAtPosition ˅
    def _getInteractiveSpectrumAtPosition(self, row: int, col: int, radius: int) -> tuple:
        """
        指定された行、列、半径に対応する編集用スペクトルの範囲を取得する。CommandがUndo用に編集前の実部と虚部の範囲を保存する際に利用する。
        """

        # SAFE CODE AREA ˅
        try:
            height, width = self.interactiveRealPart.shape[:2]
            _ = self.interactiveImaginaryPart.shape
        except Exception:
            return (np.array([]), np.array([]))

        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))

        r0 = max(0, row - radius)
        r1 = min(height, row + radius + 1)
        c0 = max(0, col - radius)
        c1 = min(width, col + radius + 1)

        rr, cc = np.ogrid[r0:r1, c0:c1]
        mask = (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2

        real_part = np.copy(self.interactiveRealPart[r0:r1, c0:c1][mask])
        imaginary_part = np.copy(self.interactiveImaginaryPart[r0:r1, c0:c1][mask])
        return (real_part, imaginary_part)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._getInteractiveSpectrumAtPosition ˄
