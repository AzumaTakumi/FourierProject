from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_2_d_model import Fourier2dModel
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class EraseSpectrumAtPositionCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    2次元スペクトルの指定位置周辺の成分を無効化するCommandである。指定された行、列、半径に基づいて編集範囲を決定し、Undo時に元の値へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier2dModel, row: int, col: int, radius: int) -> None:
        """
        操作対象のFourier2dModel、編集対象位置、編集半径を受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier2dModelを保持する。
        self.model: Fourier2dModel = model

        # 編集対象の中心行を保持する。
        self.row: int = row

        # 編集対象の中心列を保持する。
        self.col: int = col

        # 編集対象範囲の半径を保持する。
        self.radius: int = radius

        # 編集前の範囲に対応する実部配列を保持する。
        self.oldRealPart: np.ndarray = None

        # 編集前の範囲に対応する虚部配列を保持する。
        self.oldImaginaryPart: np.ndarray = None

        # SAFE CODE AREA ˅
        # UIからの入力を配列アクセスで使える整数へそろえ、負の半径を防ぐ。
        self.row = int(row)
        self.col = int(col)
        self.radius = max(0, int(radius))
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定範囲の編集前の実部と虚部を保存し、その範囲のスペクトル成分を無効化する。
        """

        # SAFE CODE AREA ˅
        # Undo用に、消去前の円形ブラシ範囲の実部・虚部を保存する。
        self.oldRealPart, self.oldImaginaryPart = self.model._getInteractiveSpectrumAtPosition(
            self.row, self.col, self.radius
        )
        # 編集対象がない場合は無効Commandとして扱い、Undoでも何もしないようNoneにする。
        if self.oldRealPart.size == 0 or self.oldImaginaryPart.size == 0:
            self.oldRealPart = None
            self.oldImaginaryPart = None
            return
        # Model本体に消去処理を任せ、逆変換の再計算もそこで行う。
        self.model.eraseSpectrumAtPosition(self.row, self.col, self.radius)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定範囲のスペクトル成分を編集前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        # executeで有効な保存値が作られていない場合は取り消し対象がない。
        if self.oldRealPart is None or self.oldImaginaryPart is None:
            return
        # 保存していた円形ブラシ範囲の値をModelへ書き戻す。
        self.model.restoreInteractiveSpectrumAtPosition(
            self.row,
            self.col,
            self.radius,
            self.oldRealPart,
            self.oldImaginaryPart,
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        # デバッグや履歴表示用に、編集中心と半径を文字列化する。
        return f"Erase Spectrum at position ({self.row}, {self.col}) with radius {self.radius}"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
