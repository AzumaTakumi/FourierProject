from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_model import FourierModel

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
    # 追加メソッドは定義しない。処理本体は各生成メソッド内のSAFE CODE AREAへ記述する。
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
        self.computeFourierData()
        self.resetSpectrum()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setSourceData ˄


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


    # GENERATED CODE AREA: method._normalizeSpectrumPositions ˅
    def _normalizeSpectrumPositions(self, positions: list) -> list:
        """
        複数座標を配列範囲内へ丸める
        """

        # SAFE CODE AREA ˅
        # 入力された複数座標を配列範囲内へ丸め、連続する重複点を取り除く。
        if not self._hasInteractiveSpectrum():
            return []
        height, width = self.interactiveRealPart.shape[:2]
        points = []
        for row, col in positions:
            normalized = (
                int(np.clip(row, 0, max(height - 1, 0))),
                int(np.clip(col, 0, max(width - 1, 0))),
            )
            if not points or points[-1] != normalized:
                points.append(normalized)
        return points
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._normalizeSpectrumPositions ˄


    # GENERATED CODE AREA: method._normalizeRect ˅
    def _normalizeRect(self, rowStart: int, rowStop: int, colStart: int, colStop: int) -> tuple:
        """
        矩形範囲を配列範囲内へ丸める
        """

        # SAFE CODE AREA ˅
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
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._normalizeRect ˄


    # GENERATED CODE AREA: method._circleMask ˅
    def _circleMask(self, row: int, col: int, radius: int, r0: int, r1: int, c0: int, c1: int) -> np.ndarray:
        """
        矩形内の円形ブラシマスクを作る
        """

        # SAFE CODE AREA ˅
        # 矩形の中で円形ブラシに含まれる画素だけをTrueにする。
        rr, cc = np.ogrid[r0:r1, c0:c1]
        return (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._circleMask ˄


    # GENERATED CODE AREA: method._normalizePaintColor ˅
    def _normalizePaintColor(self, rgbColor: list) -> np.ndarray:
        # SAFE CODE AREA ˅
        # RGB指定を1次元のfloat配列へ変換し、空指定を明示的なエラーにする。
        color = np.asarray(rgbColor, dtype=float).reshape(-1)
        try:
            _ = color[0]
        except IndexError as exc:
            raise ValueError("rgbColor が空です。少なくとも1つ以上の数値を指定してください。空配列は塗りつぶし値に変換できません。") from exc
        return color
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._normalizePaintColor ˄


    # GENERATED CODE AREA: method.getSpectrumRectForPositions ˅
    def getSpectrumRectForPositions(self, positions: list, radius: int) -> tuple:
        """
        複数ブラシ位置を含むUndo用の現在値を取得する
        """

        # SAFE CODE AREA ˅
        # 複数の円形ブラシをすべて含むUndo保存用矩形を計算する。
        if not self._hasInteractiveSpectrum():
            return None
        points = self._normalizeSpectrumPositions(positions)
        if not points:
            return None
        height, width = self.interactiveRealPart.shape[:2]
        radius = max(0, int(radius))
        rects = []
        for row, col in points:
            rects.append((
                max(0, row - radius),
                min(height, row + radius + 1),
                max(0, col - radius),
                min(width, col + radius + 1),
            ))
        return (
            min(rect[0] for rect in rects),
            max(rect[1] for rect in rects),
            min(rect[2] for rect in rects),
            max(rect[3] for rect in rects),
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getSpectrumRectForPositions ˄


    # GENERATED CODE AREA: method.getInteractiveSpectrumAtRect ˅
    def getInteractiveSpectrumAtRect(self, rowStart: int, rowStop: int, colStart: int, colStop: int) -> tuple:
        """
        一括編集CommandがUndoように矩形範囲を保存する
        """

        # SAFE CODE AREA ˅
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
    # GENERATED CODE AREA: method.getInteractiveSpectrumAtRect ˄


    # GENERATED CODE AREA: method._hasInteractiveSpectrum ˅
    def _hasInteractiveSpectrum(self) -> bool:
        """
        編集対象スペクトルが初期化済みかを確認する
        """

        # SAFE CODE AREA ˅
        # 編集対象となる実部・虚部・パワースペクトルがそろっているかを確認する。
        try:
            real_shape = self.interactiveRealPart.shape
            imag_shape = self.interactiveImaginaryPart.shape
            power_shape = self.interactivePowerSpectrum.shape
        except Exception:
            return False
        return real_shape == imag_shape == power_shape and len(real_shape) >= 2
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._hasInteractiveSpectrum ˄


    # GENERATED CODE AREA: method.eraseSpectrumAtPositions ˅
    def eraseSpectrumAtPositions(self, positions: list, radius: int) -> None:
        """
        複数点をまとめて消去し、逆FFTを最後に1回だけ行う
        """

        # SAFE CODE AREA ˅
        # 複数ブラシ位置をまとめて消去し、逆FFTは全点の編集が終わった後に1回だけ行う。
        if not self._hasInteractiveSpectrum():
            return
        points = self._normalizeSpectrumPositions(positions)
        if not points:
            return
        height, width = self.interactiveRealPart.shape[:2]
        radius = max(0, int(radius))

        for row, col in points:
            r0 = max(0, row - radius)
            r1 = min(height, row + radius + 1)
            c0 = max(0, col - radius)
            c1 = min(width, col + radius + 1)
            mask = self._circleMask(row, col, radius, r0, r1, c0, c1)

            real_view = self.interactiveRealPart[r0:r1, c0:c1]
            imag_view = self.interactiveImaginaryPart[r0:r1, c0:c1]
            power_view = self.interactivePowerSpectrum[r0:r1, c0:c1]

            real_view[mask] = 0
            imag_view[mask] = 0
            power_view[mask] = 0

        self.computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtPositions ˄


    # GENERATED CODE AREA: method.paintRgbSpectrumAtPositions ˅
    def paintRgbSpectrumAtPositions(self, positions: list, radius: int, rgbColor: list) -> None:
        """
        複数点をまとめてRGBペイントし、逆FFTを最後に1回だけ行う
        """

        # SAFE CODE AREA ˅
        # 複数ブラシ位置をまとめてRGBペイントし、逆FFTは全点の編集が終わった後に1回だけ行う。
        if not self._hasInteractiveSpectrum():
            return
        points = self._normalizeSpectrumPositions(positions)
        if not points:
            return
        height, width = self.interactiveRealPart.shape[:2]
        radius = max(0, int(radius))
        color = self._normalizePaintColor(rgbColor)

        for row, col in points:
            r0 = max(0, row - radius)
            r1 = min(height, row + radius + 1)
            c0 = max(0, col - radius)
            c1 = min(width, col + radius + 1)
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

        self.computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.paintRgbSpectrumAtPositions ˄


    # GENERATED CODE AREA: method.restoreInteractiveSpectrumAtRect ˅
    def restoreInteractiveSpectrumAtRect(self, rowStart: int, rowStop: int, colStart: int, colStop: int, realPart: np.ndarray, imaginaryPart: np.ndarray) -> None:
        """
        一括編集CommandのUndoで矩形範囲をまとめて戻す
        """

        # SAFE CODE AREA ˅
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
        self.computeInverseData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreInteractiveSpectrumAtRect ˄

