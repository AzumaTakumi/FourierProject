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
    # 0除算判定などで使う閾値。
    accuracy: float = 1.0e-12
    # 1D描画時の出力画像幅。
    imageWidth: int = 512
    # 1D描画時の出力画像高さ。
    imageHeight: int = 256

    @classmethod
    def imageFromImageData(cls, data: np.ndarray) -> Image.Image:
        array = np.asarray(data)
        if np.iscomplexobj(array):
            array = np.real(array)
        array = np.nan_to_num(array.astype(float, copy=False))

        if array.size == 0:
            return Image.new("L", (1, 1), 0)

        if np.max(array) <= 1.0 and np.min(array) >= 0.0:
            array = array * 255.0
        array = np.clip(array, 0.0, 255.0).astype(np.uint8)

        if array.ndim == 2:
            return Image.fromarray(array, "L")
        if array.ndim == 3 and array.shape[-1] == 3:
            return Image.fromarray(array, "RGB")
        if array.ndim == 3 and array.shape[-1] == 1:
            return Image.fromarray(np.squeeze(array, axis=-1), "L")
        return cls.imageFromSpectrum(array)
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.setAccuracy ˅
    @classmethod
    def setAccuracy(cls, accuracy: float) -> None:
        """
        レンダリング設定（accuracy）を設定する。以後の画像生成処理に反映される。
        """

        # SAFE CODE AREA ˅
        # 入力をfloatへ変換して設定する。
        cls.accuracy = float(accuracy)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.setAccuracy ˄


    # FIXED CODE AREA: method.setImageWidth ˅
    @classmethod
    def setImageWidth(cls, imageWidth: int) -> None:
        """
        レンダリング設定（imageWidth）を設定する。以後の画像生成処理に反映される。
        """

        # SAFE CODE AREA ˅
        # 入力を整数化して画像幅へ設定する。
        cls.imageWidth = int(imageWidth)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.setImageWidth ˄


    # FIXED CODE AREA: method.setImageHeight ˅
    @classmethod
    def setImageHeight(cls, imageHeight: int) -> None:
        """
        レンダリング設定（imageHeight）を設定する。以後の画像生成処理に反映される。
        """

        # SAFE CODE AREA ˅
        # 入力を整数化して画像高さへ設定する。
        cls.imageHeight = int(imageHeight)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.setImageHeight ˄


    # FIXED CODE AREA: method.imageFrom1dData ˅
    @classmethod
    def imageFrom1dData(cls, data: np.ndarray) -> Image.Image:
        """
        1次元配列データを可視化用Imageに変換して返す。波形/スペクトルなどの1Dデータ表示に用いる。
        """

        # SAFE CODE AREA ˅
        # 描画用の数値配列に変換する（複素数は絶対値、NaN/Inf は数値化）。
        array = np.asarray(data)
        complex_mask = float(np.iscomplexobj(array))
        array = np.abs(array) * complex_mask + array * (1.0 - complex_mask)
        values = np.nan_to_num(array.astype(float, copy=False)).reshape(-1)

        # 出力画像サイズを取得し、白背景のグレースケール画像を作成する。
        width = max(1, int(getattr(cls, "imageWidth", 512)))
        height = max(1, int(getattr(cls, "imageHeight", 256)))
        image = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(image)

        # 目盛り表示用の描画領域（余白を含む）を決める。
        margin_left = 48
        margin_right = 12
        margin_top = 12
        margin_bottom = 26
        plot_left = margin_left
        plot_top = margin_top
        plot_right = max(plot_left + 1, width - margin_right - 1)
        plot_bottom = max(plot_top + 1, height - margin_bottom - 1)
        plot_width = plot_right - plot_left + 1
        plot_height = plot_bottom - plot_top + 1

        # 値域を求め、一定値データでも 0 除算しないよう安全な分母を作る。
        min_value = float(np.min(values))
        max_value = float(np.max(values))
        span = max_value - min_value
        flat_mask = float(abs(span) <= getattr(cls, "accuracy", 1.0e-12))
        safe_span = span + flat_mask
        normalized = (values - min_value) / safe_span
        scaled = (1.0 - normalized) * (plot_height - 1) + plot_top
        center = np.full(values.shape, plot_top + (plot_height // 2), dtype=float)
        # 一定値データは中央線、それ以外は正規化値に応じた波形位置を使う。
        y_values = center * flat_mask + scaled * (1.0 - flat_mask)

        # 軸枠と目盛りを描画する。
        draw.rectangle((plot_left, plot_top, plot_right, plot_bottom), outline=180, width=1)
        x_ticks = 5
        y_ticks = 4
        for i in range(x_ticks + 1):
            tick_ratio = i / x_ticks
            x = int(round(plot_left + tick_ratio * (plot_width - 1)))
            draw.line((x, plot_bottom, x, plot_bottom + 4), fill=120, width=1)
            sample_index = int(round(tick_ratio * (values.size - 1)))
            draw.text((x - 10, plot_bottom + 6), str(sample_index), fill=120)

        for i in range(y_ticks + 1):
            tick_ratio = i / y_ticks
            y = int(round(plot_top + tick_ratio * (plot_height - 1)))
            draw.line((plot_left - 4, y, plot_left, y), fill=120, width=1)
            label_value = max_value - (span * tick_ratio)
            draw.text((4, y - 6), f"{label_value:.2g}", fill=120)

        # サンプル点を横方向に等間隔配置し、点列として描画する。
        x_values = np.linspace(plot_left, plot_right, num=values.size)
        points = [(int(round(x)), int(round(y))) for x, y in zip(x_values, y_values)]
        {True: lambda: draw.point(points[0], fill=0), False: lambda: draw.line(points, fill=0, width=2)}[
            len(points) == 1
        ]()
        return image
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.imageFrom1dData ˄


    # FIXED CODE AREA: method.imageFromSpectrum ˅
    @classmethod
    def imageFromSpectrum(cls, spectrum: np.ndarray) -> Image.Image:
        """
        スペクトル行列を可視化用に正規化/スケーリングし、Imageとして返す。パワースペクトル表示などに用いる。
        """

        # SAFE CODE AREA ˅
        # 複素数を扱える表示配列へ変換し、log1p でダイナミックレンジを圧縮する。
        base = np.asarray(spectrum)
        complex_mask = float(np.iscomplexobj(base))
        base = np.abs(base) * complex_mask + base * (1.0 - complex_mask)
        array = np.nan_to_num(base.astype(float, copy=False))
        if array.ndim >= 2:
            array = np.fft.fftshift(array, axes=(0, 1))
        array = np.log1p(np.abs(array))
        channel_size = int(np.shape(array)[-1])
        # 1Dは折れ線描画、2D/3Dは画像化の経路に振り分ける。
        render_mode = {1: "line", 2: "image", 3: "image"}[array.ndim]
        line_renderer = lambda: cls.imageFrom1dData(array)
        image_renderer = lambda: Image.fromarray(
            {"RGB": cls.normalize(array), "L": np.squeeze(cls.normalize(array))}[{3: "RGB"}.get(channel_size, "L")],
            {3: "RGB"}.get(channel_size, "L")
        )
        return {"line": line_renderer, "image": image_renderer}[render_mode]()
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.imageFromSpectrum ˄


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
    def normalize(cls, data: np.ndarray) -> np.ndarray:
        """
        可視化のためにデータを所定レンジへ正規化したndarrayを返す（例: min-max、logスケール等）。
        """

        # SAFE CODE AREA ˅
        # 複素数やNaN/Infを含む入力を、正規化可能な実数配列へ変換する。
        array = np.asarray(data)
        complex_mask = float(np.iscomplexobj(array))
        array = np.abs(array) * complex_mask + array * (1.0 - complex_mask)
        array = np.nan_to_num(array.astype(float, copy=False))

        # 最小値・最大値から正規化準備を行う。
        min_value = float(np.min(array))
        max_value = float(np.max(array))

        # 値域が極小の場合も安全に扱い、0〜255の uint8 にスケーリングする。
        span = max_value - min_value
        flat_mask = float(abs(span) <= getattr(cls, "accuracy", 1.0e-12))
        safe_span = span + flat_mask
        normalized = (array - min_value) / safe_span
        scaled = np.clip(normalized * 255.0, 0, 255) * (1.0 - flat_mask)
        return scaled.astype(np.uint8)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.normalize ˄
