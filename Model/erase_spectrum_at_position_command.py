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

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier2dModel, row: int, col: int, radius: int) -> None:
        """
        操作対象のFourier2dModel、編集対象位置、編集半径を受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier2dModelを保持する。
        self.model: Fourier2dModel = None

        # 編集対象の中心行を保持する。
        self.row: int = 0

        # 編集対象の中心列を保持する。
        self.col: int = 0

        # 編集対象範囲の半径を保持する。
        self.radius: int = 0

        # 編集前の範囲に対応する実部配列を保持する。
        self.oldRealPart: np.ndarray = None

        # 編集前の範囲に対応する虚部配列を保持する。
        self.oldImaginaryPart: np.ndarray = None

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定範囲の編集前の実部と虚部を保存し、その範囲のスペクトル成分を無効化する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定範囲のスペクトル成分を編集前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄

