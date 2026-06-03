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
    def computeFourierData(self) -> None:
        # 自動生成された公開メソッド名から、実際のFFT計算処理へ委譲する。
        self._computeFourierData()

    def computeInverseData(self) -> None:
        # 編集用スペクトルを元にした逆変換処理へ委譲する。
        self._computeInverseData()

    def getInteractiveSpectrumAtPosition(self, row: int, col: int, radius: int) -> tuple:
        # 2D編集CommandがUndo用の現在値を取得できるよう、内部取得処理を公開する。
        return self._getInteractiveSpectrumAtPosition(row, col, radius)

    def getSpectrumRectForPositions(self, positions: list[tuple[int, int]], radius: int) -> tuple[int, int, int, int] | None:
        # 線分編集CommandがUndo用の矩形を保存できるよう、複数ブラシをすべて含む矩形を返す。
        return self._spectrumRectForPositions(positions, radius)

    def getInteractiveSpectrumAtRect(self, rowStart: int, rowStop: int, colStart: int, colStop: int) -> tuple:
        # 一括編集CommandがUndo用に矩形範囲の編集前スペクトルを保存できるようにする。
        return self._getInteractiveSpectrumAtRect(rowStart, rowStop, colStart, colStop)

    def eraseSpectrumAtPositions(self, positions: list[tuple[int, int]], radius: int) -> None:
        # 複数ブラシ位置をまとめて消去し、逆FFTは全点の編集が終わった後に1回だけ行う。
        if not self._hasInteractiveSpectrum():
            return
        points = self._normalizeSpectrumPositions(positions)
        if not points:
            return
        radius = max(0, int(radius))

        for row, col in points:
            r0, r1, c0, c1 = self._spectrumRect(row, col, radius)
            mask = self._circleMask(row, col, radius, r0, r1, c0, c1)

            real_view = self.interactiveRealPart[r0:r1, c0:c1]
            imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]
            power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]

            real_view[mask] = 0
            imag_view[mask] = 0
            power_view[mask] = 0

        self._computeInverseData()

    def paintRgbSpectrumAtPositions(self, positions: list[tuple[int, int]], radius: int, rgbColor: list) -> None:
        # 複数ブラシ位置をまとめてRGBペイントし、逆FFTは全点の編集が終わった後に1回だけ行う。
        if not self._hasInteractiveSpectrum():
            return
        points = self._normalizeSpectrumPositions(positions)
        if not points:
            return
        radius = max(0, int(radius))
        color = self._normalizePaintColor(rgbColor)

        for row, col in points:
            r0, r1, c0, c1 = self._spectrumRect(row, col, radius)
            mask = self._circleMask(row, col, radius, r0, r1, c0, c1)

            real_view = self.interactiveRealPart[r0:r1, c0:c1]
            imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]

            if real_view.ndim == 3:
                channels = real_view.shape[-1]
                if color.size < channels:
                    raise ValueError("RGBスペクトル編集には3つの色成分が必要です。")
                real_view[mask] = color[:channels].astype(real_view.dtype, copy=False)
            else:
                real_view[mask] = float(np.mean(color[:3]))
            imag_view[mask] = 0

            power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]
            power_view[mask] = np.square(real_view[mask]) + np.square(imag_view[mask])

        self._computeInverseData()

    def restoreInteractiveSpectrumAtRect(
        self,
        rowStart: int,
        rowStop: int,
        colStart: int,
        colStop: int,
        realPart: np.ndarray,
        imaginaryPart: np.ndarray,
    ) -> None:
        # 一括編集CommandのUndoで、保存した矩形範囲を1回で戻し、逆FFTも最後に1回だけ行う。
        rect = self._normalizeRect(rowStart, rowStop, colStart, colStop)
        if rect is None:
            return
        r0, r1, c0, c1 = rect

        real_view = self.interactiveRealPart[r0:r1, c0:c1]
        imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]
        real_view[...] = np.asarray(realPart)
        imag_view[...] = np.asarray(imaginaryPart)

        power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]
        power_view[...] = np.square(real_view) + np.square(imag_view)
        self._computeInverseData()

    def _hasInteractiveSpectrum(self) -> bool:
        # 編集対象となる実部・虚部・パワースペクトルがそろっているかを確認する。
        try:
            real_shape = self.interactiveRealPart.shape
            imag_shape = self.interactiveImaginaryPart.shape
            power_shape = self.interactivePowerSpectrum.shape
        except Exception:
            return False
        return real_shape == imag_shape == power_shape and len(real_shape) >= 2

    def _normalizeSpectrumPositions(self, positions: list[tuple[int, int]]) -> list[tuple[int, int]]:
        # 入力された複数座標を配列範囲内へ丸め、連続する重複点を取り除く。
        if not self._hasInteractiveSpectrum():
            return []
        height, width = self.interactiveRealPart.shape[:2]
        points: list[tuple[int, int]] = []
        for row, col in positions:
            normalized = (
                int(np.clip(row, 0, max(height - 1, 0))),
                int(np.clip(col, 0, max(width - 1, 0))),
            )
            if not points or points[-1] != normalized:
                points.append(normalized)
        return points

    def _normalizeRect(self, rowStart: int, rowStop: int, colStart: int, colStop: int) -> tuple[int, int, int, int] | None:
        # 矩形範囲を現在スペクトル配列の有効範囲へ丸める。
        if not self._hasInteractiveSpectrum():
            return None
        height, width = self.interactiveRealPart.shape[:2]
        r0 = int(np.clip(rowStart, 0, height))
        r1 = int(np.clip(rowStop, r0, height))
        c0 = int(np.clip(colStart, 0, width))
        c1 = int(np.clip(colStop, c0, width))
        if r1 <= r0 or c1 <= c0:
            return None
        return r0, r1, c0, c1

    def _spectrumRect(self, row: int, col: int, radius: int) -> tuple[int, int, int, int]:
        # 1つの円形ブラシを含む最小矩形を計算する。
        height, width = self.interactiveRealPart.shape[:2]
        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))
        return (
            max(0, row - radius),
            min(height, row + radius + 1),
            max(0, col - radius),
            min(width, col + radius + 1),
        )

    def _spectrumRectForPositions(self, positions: list[tuple[int, int]], radius: int) -> tuple[int, int, int, int] | None:
        # 複数の円形ブラシをすべて含むUndo保存用矩形を計算する。
        if not self._hasInteractiveSpectrum():
            return None
        points = self._normalizeSpectrumPositions(positions)
        if not points:
            return None
        rects = [self._spectrumRect(row, col, radius) for row, col in points]
        return (
            min(rect[0] for rect in rects),
            max(rect[1] for rect in rects),
            min(rect[2] for rect in rects),
            max(rect[3] for rect in rects),
        )

    def _circleMask(self, row: int, col: int, radius: int, r0: int, r1: int, c0: int, c1: int) -> np.ndarray:
        # 矩形の中で円形ブラシに含まれる画素だけをTrueにする。
        rr, cc = np.ogrid[r0:r1, c0:c1]
        return (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2

    def _normalizePaintColor(self, rgbColor: list) -> np.ndarray:
        # RGB指定を1次元のfloat配列へ変換し、空指定を明示的なエラーにする。
        color = np.asarray(rgbColor, dtype=float).reshape(-1)
        try:
            _ = color[0]
        except IndexError as exc:
            raise ValueError("rgbColor が空です。少なくとも1つ以上の数値を指定してください。空配列は塗りつぶし値に変換できません。") from exc
        return color

    def _getInteractiveSpectrumAtRect(self, rowStart: int, rowStop: int, colStart: int, colStop: int) -> tuple:
        # Undo用に矩形範囲の実部・虚部をcopyして返す。
        rect = self._normalizeRect(rowStart, rowStop, colStart, colStop)
        if rect is None:
            return (np.array([]), np.array([]))
        r0, r1, c0, c1 = rect
        return (
            np.copy(self.interactiveRealPart[r0:r1, c0:c1]),
            np.copy(self.interactiveImaginaryPart[r0:r1, c0:c1]),
        )
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
        # 初期画像が渡された場合は、通常の設定処理を通してFFTと逆変換まで初期化する。
        if sourceData is not None:
            self.setSourceData(sourceData)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.setSourceData ˅
    def setSourceData(self, sourceData: np.ndarray) -> None:
        """
        2次元の元データを設定または更新する。設定後、フーリエ変換結果、パワースペクトル、編集用スペクトル、逆変換結果を再計算できる状態にする。
        """

        # SAFE CODE AREA ˅
        # 画像処理で扱いやすいよう、入力をfloat配列へ変換する。
        data = np.asarray(sourceData, dtype=float)
        # グレースケール画像は2次元、RGB画像は高さ・幅・3チャンネルの3次元配列だけを受け付ける。
        if data.ndim not in (2, 3):
            raise ValueError("Fourier2dModel sourceData must be a 2D grayscale or 3D RGB array.")
        if data.ndim == 3 and data.shape[-1] != 3:
            raise ValueError("Fourier2dModel only supports RGB arrays with 3 channels.")
        if data.shape[0] == 0 or data.shape[1] == 0:
            raise ValueError("Fourier2dModel sourceData height and width must not be empty.")

        # 呼び出し元の配列変更がModel内部へ影響しないようコピーして保持する。
        self.sourceData = data.copy()
        # 元画像の変更に合わせてFFT結果を作り直し、編集用スペクトルを元状態に戻す。
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
        # 指定名の配列が存在する場合だけfillし、未初期化のフィールドはそのままにする。
        for name in (
            "realPart",
            "imaginaryPart",
            "powerSpectrum",
            "interactiveRealPart",
            "interactiveImaginaryPart",
            "interactivePowerSpectrum",
            "inverseData",
        ):
            array = getattr(self, name, None)
            if array is not None:
                array.fill(value)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._fill ˄


    # GENERATED CODE AREA: method._computeFourierData ˅
    def _computeFourierData(self) -> None:
        """
        現在のsourceDataに対して2次元フーリエ変換を行い、realPart、imaginaryPart、powerSpectrumを生成または更新する。
        """

        # SAFE CODE AREA ˅
        # FourierTransformへ元画像を渡し、2次元FFTを実行する。
        self.engine.setFftInputSignal(self.sourceData)
        self.engine.transform()
        # FFT結果を実部・虚部へ分離し、表示用のパワースペクトルを計算する。
        self.realPart = self.engine.realPart()
        self.imaginaryPart = self.engine.imaginaryPart()
        self.powerSpectrum = np.square(self.realPart) + np.square(self.imaginaryPart)
        # 編集用スペクトルは元スペクトルと別配列にして、消しゴムやペイントの変更を分離する。
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
        # 編集済みの実部・虚部を複素スペクトルに戻してIFFT入力にする。
        self.engine.setIfftInputSpectrum(self.interactiveRealPart + 1j * self.interactiveImaginaryPart)
        # 逆変換結果はInverse画像表示に利用する。
        self.inverseData = self.engine.inverseTransform()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._computeInverseData ˄


    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˅
    def eraseSpectrumAtPosition(self, row: int, col: int, radius: int) -> None:
        """
        指定された行、列、半径に対応する2次元スペクトル範囲を無効化する。interactiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを更新し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        # 単一点編集も一括編集経路へ通し、処理内容と逆FFTの呼び方を統一する。
        self.eraseSpectrumAtPositions([(row, col)], radius)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˅
    def paintRgbSpectrumAtPosition(self, row: int, col: int, radius: int, rgbColor: list) -> None:
        """
        指定された行、列、半径に対応する2次元スペクトル範囲を、RGB色に基づいて編集する。編集結果をinteractiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumに反映し、必要に応じて逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        # 単一点ペイントも一括編集経路へ通し、処理内容と逆FFTの呼び方を統一する。
        self.paintRgbSpectrumAtPositions([(row, col)], radius, rgbColor)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.restoreInteractiveSpectrumAtPosition ˅
    def restoreInteractiveSpectrumAtPosition(self, row: int, col: int, radius: int, realPart: np.ndarray, imaginaryPart: np.ndarray) -> None:
        """
        Undo操作で値を戻す際に使用する。restoreSpectrumAtPosition(row, col, radius)で戻す操作は不適切であり、本来戻す可能性がある値と異なるため、この操作を追加した。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        # Undo対象のスペクトルが無い場合は、復元処理を行わず戻る。
        try:
            height, width = self.interactiveRealPart.shape[:2]
            _ = self.interactiveImaginaryPart.shape
            _ = self.interactivePowerSpectrum.shape
        except Exception:
            return

        # 保存時と同じ座標・半径になるよう、範囲外の値を丸める。
        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))

        # 復元対象の矩形範囲と、その中の円形マスクを再構成する。
        r0 = max(0, row - radius)
        r1 = min(height, row + radius + 1)
        c0 = max(0, col - radius)
        c1 = min(width, col + radius + 1)

        rr, cc = np.ogrid[r0:r1, c0:c1]
        mask = (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2

        real_view = self.interactiveRealPart[r0:r1, c0:c1]
        imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]

        # Commandが保存していた編集前の実部・虚部を配列化する。
        old_real = np.asarray(realPart)
        old_imag = np.asarray(imaginaryPart)

        # 保存値が矩形全体なら一括代入し、マスク部分だけならマスク代入で復元する。
        try:
            real_view[...] = old_real
            imag_view[...] = old_imag
        except ValueError:
            real_view[mask] = old_real
            imag_view[mask] = old_imag

        # 復元後の実部・虚部に合わせてパワースペクトルを再計算する。
        power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]
        power_view[...] = np.square(real_view) + np.square(imag_view)

        # Undo結果をInverse画像にも反映する。
        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreInteractiveSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.dataColorImage ˅
    def dataColorImage(self) -> np.ndarray:
        """
        動作確認用のカラー画像サンプルデータを生成して返す。
        """

        # SAFE CODE AREA ˅
        # 横方向に赤、縦方向に緑、周期模様に青を割り当てたRGBサンプルを作る。
        y, x = np.mgrid[0:128, 0:128]
        red = (x / 127.0) * 255.0
        green = (y / 127.0) * 255.0
        blue = ((np.sin(x / 8.0) + np.cos(y / 10.0) + 2.0) / 4.0) * 255.0
        return np.stack((red, green, blue), axis=-1)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataColorImage ˄


    # GENERATED CODE AREA: method.dataGrayScaleImage ˅
    def dataGrayScaleImage(self) -> np.ndarray:
        """
        動作確認用のグレースケール画像サンプルデータを生成して返す。
        """

        # SAFE CODE AREA ˅
        # 横方向と縦方向に異なる周期成分を持つ、FFT確認用のグレースケール画像を作る。
        y, x = np.mgrid[0:128, 0:128]
        return (
            127.5
            + 60.0 * np.sin(2.0 * np.pi * x / 24.0)
            + 40.0 * np.cos(2.0 * np.pi * y / 32.0)
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.dataGrayScaleImage ˄


    # GENERATED CODE AREA: method.createSnapshot ˅
    def createSnapshot(self) -> Snapshot:
        """
        現在の2次元モデルの内部状態をSnapshotとして生成する。Undo対象操作の実行前に、sourceData、スペクトル情報、編集用スペクトル、逆変換結果を保存するために使用する。
        """

        # SAFE CODE AREA ˅
        # Undo時に配列参照が共有されないよう、Model内の状態をすべてcopyして保存する。
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
        # Snapshot側の配列を再度copyし、復元後の編集が保存済み状態へ影響しないようにする。
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
        2次元の編集用スペクトルを、フーリエ変換直後の元スペクトル状態に戻す。編集によって変更されたinteractiveRealPart、interactiveImaginaryPart、interactivePowerSpectrumを初期状態に戻し、逆変換結果を再計算する。
        """

        # SAFE CODE AREA ˅
        # FFT結果が無い場合は、リセット対象がまだ存在しないため何もしない。
        if self.realPart is None or self.imaginaryPart is None or self.powerSpectrum is None:
            return
        # 編集用スペクトルをFFT直後の元スペクトルのコピーへ戻す。
        self.interactiveRealPart = np.copy(self.realPart)
        self.interactiveImaginaryPart = np.copy(self.imaginaryPart)
        self.interactivePowerSpectrum = np.copy(self.powerSpectrum)
        
        # 元スペクトルから復元画像を再計算する。
        self._computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method._getInteractiveSpectrumAtPosition ˅
    def _getInteractiveSpectrumAtPosition(self, row: int, col: int, radius: int) -> tuple:
        """
        指定された行、列、半径に対応する編集用スペクトルの範囲を取得する。CommandがUndo用に編集前の実部と虚部の範囲を保存する際に利用する。
        """

        # SAFE CODE AREA ˅
        # Undo用に取得する編集用スペクトルが未初期化なら、空配列を返してCommand側で無効操作にする。
        try:
            height, width = self.interactiveRealPart.shape[:2]
            _ = self.interactiveImaginaryPart.shape
        except Exception:
            return (np.array([]), np.array([]))

        # 保存対象の座標と半径を実際の配列範囲へ丸める。
        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))

        # 編集操作と同じ矩形範囲・円形マスクを作り、保存対象を正確に一致させる。
        r0 = max(0, row - radius)
        r1 = min(height, row + radius + 1)
        c0 = max(0, col - radius)
        c1 = min(width, col + radius + 1)

        rr, cc = np.ogrid[r0:r1, c0:c1]
        mask = (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2

        # マスク範囲の実部・虚部をcopyし、後続の編集でUndo用データが変わらないようにする。
        real_part = np.copy(self.interactiveRealPart[r0:r1, c0:c1][mask])
        imaginary_part = np.copy(self.interactiveImaginaryPart[r0:r1, c0:c1][mask])
        return (real_part, imaginary_part)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._getInteractiveSpectrumAtPosition ˄
