from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from PIL import Image

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
from PIL import ImageDraw
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

    # GENERATED CODE AREA: method.imageFromImageData ˅
    def imageFromImageData(self, data: np.ndarray) -> Image.Image:
        """
        Source/Inverse用の画素データをPIL.Imageへ変換する
        """

        # SAFE CODE AREA ˅
        # SOURCE/INVERSE用の画像データは、スペクトル表示ではなく実際の画素値として描画する。
        array = np.asarray(data)
        # IFFT結果などで複素数が渡ってきた場合も、表示に使う実部だけを取り出す。
        array = np.real(array)
        # NaNやInfを画素化できる数値へ置き換える。
        array = np.nan_to_num(array.astype(float, copy=False))

        # 0〜1正規化画像は8bit画像として表示できるよう0〜255へ拡大する。
        normalizedMask = float(np.max(array) <= 1.0 and np.min(array) >= 0.0)
        array = array * (1.0 + 254.0 * normalizedMask)
        # 表示画像として扱えるよう、画素値を8bit範囲へ丸める。
        array = np.clip(array, 0.0, 255.0).astype(np.uint8)

        # 配列形状に応じて、グレースケールまたはRGBのPIL.Imageへ変換する。
        channelSize = int(np.shape(array + np.zeros((1, 1, 1), dtype=array.dtype))[-1])
        renderMode = {2: "L2", 3: {3: "RGB", 1: "L1"}.get(channelSize, "SPECTRUM")}.get(array.ndim, "SPECTRUM")
        return {
            "L2": lambda: Image.fromarray(array, "L"),
            "L1": lambda: Image.fromarray(np.squeeze(array, axis=-1), "L"),
            "RGB": lambda: Image.fromarray(array, "RGB"),
            "SPECTRUM": lambda: type(self).imageFromSpectrum(array),
        }[renderMode]()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.imageFromImageData ˄


    # FIXED CODE AREA: method.imageFrom1dData ˅
    @classmethod
    def imageFrom1dData(cls, data: np.ndarray) -> Image.Image:
        """
        1次元配列データを可視化用Imageに変換して返す。波形/スペクトルなどの1Dデータ表示に用いる。
        """

        # SAFE CODE AREA ˅
        # 1D波形表示ではIFFT結果の符号を保つため、複素数は実部として描画する。
        array = np.asarray(data)
        values = np.nan_to_num(np.real(array).astype(float, copy=False)).reshape(-1)

        # 1D表示用の固定サイズで、白背景のグレースケール画像を作成する。
        width = 512
        height = 256
        image = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(image)

        # 目盛り表示用の描画領域（余白を含む）を決める。
        marginLeft = 48
        marginRight = 12
        marginTop = 12
        marginBottom = 26
        plotLeft = marginLeft
        plotTop = marginTop
        plotRight = max(plotLeft + 1, width - marginRight - 1)
        plotBottom = max(plotTop + 1, height - marginBottom - 1)
        plotWidth = plotRight - plotLeft + 1
        plotHeight = plotBottom - plotTop + 1

        # 値域を求め、一定値データでも 0 除算しないよう安全な分母を作る。
        minValue = float(np.min(values))
        maxValue = float(np.max(values))
        span = maxValue - minValue
        flatMask = float(abs(span) <= 1.0e-12)
        safeSpan = span + flatMask
        normalized = (values - minValue) / safeSpan
        scaled = (1.0 - normalized) * (plotHeight - 1) + plotTop
        center = np.full(values.shape, plotTop + (plotHeight // 2), dtype=float)
        # 一定値データは中央線、それ以外は正規化値に応じた波形位置を使う。
        yValues = center * flatMask + scaled * (1.0 - flatMask)

        # 軸枠と目盛りを描画する。
        draw.rectangle((plotLeft, plotTop, plotRight, plotBottom), outline=180, width=1)
        xTicks = 5
        yTicks = 4
        for i in range(xTicks + 1):
            tickRatio = i / xTicks
            x = int(round(plotLeft + tickRatio * (plotWidth - 1)))
            draw.line((x, plotBottom, x, plotBottom + 4), fill=120, width=1)
            sampleIndex = int(round(tickRatio * (values.size - 1)))
            draw.text((x - 10, plotBottom + 6), str(sampleIndex), fill=120)

        for i in range(yTicks + 1):
            tickRatio = i / yTicks
            y = int(round(plotTop + tickRatio * (plotHeight - 1)))
            draw.line((plotLeft - 4, y, plotLeft, y), fill=120, width=1)
            labelValue = maxValue - (span * tickRatio)
            draw.text((4, y - 6), f"{labelValue:.2g}", fill=120)

        # サンプル点を横方向に等間隔配置し、点列として描画する。
        xValues = np.linspace(plotLeft, plotRight, num=values.size)
        points = [(int(round(x)), int(round(y))) for x, y in zip(xValues, yValues)]
        {True: lambda: draw.point(points[0], fill=0), False: lambda: draw.line(points, fill=0, width=2)}[
            len(points) == 1
        ]()
        return image
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.imageFrom1dData ˄

    @classmethod
    def imageFrom1dStemData(cls, data: np.ndarray) -> Image.Image:
        """
        1次元スペクトルを離散成分として縦棒表示する。
        """

        array = np.asarray(data)
        values = np.nan_to_num(np.real(array).astype(float, copy=False)).reshape(-1)

        width = 512
        height = 256
        image = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(image)

        marginLeft = 48
        marginRight = 12
        marginTop = 12
        marginBottom = 26
        plotLeft = marginLeft
        plotTop = marginTop
        plotRight = max(plotLeft + 1, width - marginRight - 1)
        plotBottom = max(plotTop + 1, height - marginBottom - 1)
        plotWidth = plotRight - plotLeft + 1
        plotHeight = plotBottom - plotTop + 1

        minValue = min(0.0, float(np.min(values)))
        maxValue = max(0.0, float(np.max(values)))
        span = maxValue - minValue
        flatMask = float(abs(span) <= 1.0e-12)
        safeSpan = span + flatMask

        normalized = (values - minValue) / safeSpan
        yValues = (1.0 - normalized) * (plotHeight - 1) + plotTop
        baselineNormalized = (0.0 - minValue) / safeSpan
        baseline = int(round((1.0 - baselineNormalized) * (plotHeight - 1) + plotTop))

        draw.rectangle((plotLeft, plotTop, plotRight, plotBottom), outline=180, width=1)
        xTicks = 5
        yTicks = 4
        for i in range(xTicks + 1):
            tickRatio = i / xTicks
            x = int(round(plotLeft + tickRatio * (plotWidth - 1)))
            draw.line((x, plotBottom, x, plotBottom + 4), fill=120, width=1)
            sampleIndex = int(round(tickRatio * (values.size - 1)))
            draw.text((x - 10, plotBottom + 6), str(sampleIndex), fill=120)

        for i in range(yTicks + 1):
            tickRatio = i / yTicks
            y = int(round(plotTop + tickRatio * (plotHeight - 1)))
            draw.line((plotLeft - 4, y, plotLeft, y), fill=120, width=1)
            labelValue = maxValue - (span * tickRatio)
            draw.text((4, y - 6), f"{labelValue:.2g}", fill=120)

        xValues = np.linspace(plotLeft, plotRight, num=values.size)
        for x, y in zip(xValues, yValues):
            px = int(round(x))
            py = int(round(y))
            draw.line((px, baseline, px, py), fill=0, width=2)
            draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=0)

        return image


    # FIXED CODE AREA: method.imageFromSpectrum ˅
    @classmethod
    def imageFromSpectrum(cls, spectrum: np.ndarray, valueRange: tuple[float, float] | None = None) -> Image.Image:
        """
        スペクトル行列を可視化用に正規化/スケーリングし、Imageとして返す。パワースペクトル表示などに用いる。
        """

        # SAFE CODE AREA ˅
        array = cls.spectrumDisplayArray(spectrum)
        # 1Dスペクトルは離散成分として縦棒描画、2D/3Dは画像化の経路に振り分ける。
        renderMode = {1: "stem"}.get(array.ndim, "image")
        stemRenderer = lambda: cls.imageFrom1dStemData(array)
        imageRenderer = lambda: Image.fromarray(cls.normalize(np.squeeze(array), valueRange), "L")
        return {"stem": stemRenderer, "image": imageRenderer}[renderMode]()
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.imageFromSpectrum ˄

    @classmethod
    def spectrumDisplayArray(cls, spectrum: np.ndarray) -> np.ndarray:
        """
        スペクトルを表示用の対数強度配列へ変換する。
        """

        base = np.asarray(spectrum)
        base = {True: np.abs, False: np.real}[np.iscomplexobj(base)](base)
        array = np.nan_to_num(base.astype(float, copy=False))
        # 2次元以上では低周波成分を中央に寄せ、スペクトル画像として見やすくする。
        array = {1: lambda value: value}.get(
            array.ndim,
            lambda value: np.fft.fftshift(value, axes=(0, 1)),
        )(array)
        # 強い直流成分だけで表示が潰れないよう、対数スケールで圧縮する。
        array = np.log1p(np.abs(array))
        # RGB画像由来のスペクトルは3チャンネル配列だが、表示では色ではなく強度として扱う。
        return {3: lambda value: np.mean(value, axis=2)}.get(
            array.ndim,
            lambda value: value,
        )(array)

    @classmethod
    def displayRangeFromSpectrum(cls, spectrum: np.ndarray) -> tuple[float, float]:
        """
        現在のスペクトル表示に使う固定レンジを返す。
        """

        array = np.asarray(cls.spectrumDisplayArray(spectrum))
        return float(np.min(array)), float(np.max(array))


    # FIXED CODE AREA: method.imageFromParts ˅
    @classmethod
    def imageFromParts(cls, realPart: np.ndarray, imaginaryPart: np.ndarray) -> Image.Image:
        """
        実部/虚部から複素スペクトルの表示用画像を生成して返す。
        """

        # SAFE CODE AREA ˅
        # パワー値（実部^2 + 虚部^2）を可視化対象として画像化する。
        return cls.imageFromSpectrum(np.square(realPart) + np.square(imaginaryPart))
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.imageFromParts ˄


    # FIXED CODE AREA: method.normalize ˅
    @classmethod
    def normalize(cls, data: np.ndarray, valueRange: tuple[float, float] | None = None) -> np.ndarray:
        """
        可視化のためにデータを所定レンジへ正規化したndarrayを返す（例: min-max、logスケール等）。
        """

        # SAFE CODE AREA ˅
        # 複素数やNaN/Infを含む入力を、正規化可能な実数配列へ変換する。
        array = np.asarray(data)
        array = {True: np.abs, False: np.real}[np.iscomplexobj(array)](array)
        array = np.nan_to_num(array.astype(float, copy=False))

        # 最小値・最大値から正規化準備を行う。
        minValue, maxValue = {
            True: lambda: valueRange,
            False: lambda: (float(np.min(array)), float(np.max(array))),
        }[valueRange is not None]()

        # 値域が極小の場合も安全に扱い、0〜255の uint8 にスケーリングする。
        span = maxValue - minValue
        flatMask = float(abs(span) <= 1.0e-12)
        safeSpan = span + flatMask
        normalized = (array - minValue) / safeSpan
        scaled = np.clip(normalized * 255.0, 0, 255) * (1.0 - flatMask)
        return scaled.astype(np.uint8)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.normalize ˄
