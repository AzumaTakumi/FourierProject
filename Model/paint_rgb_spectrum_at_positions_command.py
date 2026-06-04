from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_2_d_model import Fourier2dModel
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class PaintRgbSpectrumAtPositionsCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    2次元スペクトルの指定位置周辺をRGB色に基づいてペイント編集するCommandである。編集前の値を保存し、Undo時に元の値へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # 線分上の複数点を1つのCommandとして扱い、execute/undo時の逆FFT回数を抑える。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier2dModel, positions: list[tuple[int, int]], radius: int, rgbColor: list[float]) -> None:
        """
        操作対象のFourier2dModel、編集対象位置、編集半径、RGB色を受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier2dModelを保持する。
        self.model: Fourier2dModel = None

        # 編集対象範囲の半径を保持する。
        self.radius: int = 0

        # ペイントに使用するRGB色を保持する。
        self.rgbColor: list[float] = []

        # 編集前の範囲に対応する実部配列を保持する。
        self.oldRealPart: np.ndarray = None

        # 編集前の範囲に対応する虚部配列を保持する。
        self.oldImaginaryPart: np.ndarray = None

        self.positions: list[tuple[int, int]] = []

        self.rect: tuple[int, int, int, int] | None = None

        # SAFE CODE AREA ˅
        # 自動生成の初期値を実際の引数で上書きし、操作対象Modelを保持する。
        self.model = model
        # 呼び出し元のリスト変更がCommand内部へ影響しないよう、座標とRGB値をコピーする。
        self.positions = [(int(row), int(col)) for row, col in positions]
        self.radius = max(0, int(radius))
        self.rgbColor = list(rgbColor)
        self.rect = None
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定範囲の編集前の実部と虚部を保存し、RGB色に基づいてスペクトルを編集する。
        """

        # SAFE CODE AREA ˅
        # 複数ブラシをすべて含む矩形だけを保存し、Undo用データ量を必要範囲に絞る。
        self.rect = self.model.getSpectrumRectForPositions(self.positions, self.radius)
        if self.rect is None:
            self.oldRealPart = None
            self.oldImaginaryPart = None
            return

        self.oldRealPart, self.oldImaginaryPart = self.model.getInteractiveSpectrumAtRect(*self.rect)
        if self.oldRealPart.size == 0 or self.oldImaginaryPart.size == 0:
            self.oldRealPart = None
            self.oldImaginaryPart = None
            return

        # Modelの一括ペイントを呼ぶため、線分上の点数に関係なく逆FFTは1回だけ実行される。
        self.model.paintRgbSpectrumAtPositions(self.positions, self.radius, self.rgbColor)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定範囲のスペクトル成分を編集前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        # executeで有効な保存値が作られていない場合は取り消し対象がない。
        if self.rect is None or self.oldRealPart is None or self.oldImaginaryPart is None:
            return
        # 保存矩形を1回で戻すため、Undo時の逆FFTも1回だけで済む。
        self.model.restoreInteractiveSpectrumAtRect(*self.rect, self.oldRealPart, self.oldImaginaryPart)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        # デバッグや履歴表示用に、編集点数と半径を文字列化する。
        return f"Paint RGB Spectrum at {len(self.positions)} positions with radius {self.radius}"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
