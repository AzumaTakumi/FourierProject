from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .fourier_1_d_model import Fourier1dModel
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class EraseSpectrumAtIndexCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元スペクトルの指定インデックスの成分を無効化するCommandである。編集前の値を保存し、Undo時に元の値へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier1dModel, index: int) -> None:
        """
        操作対象のFourier1dModelと編集対象インデックスを受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier1dModelを保持する。
        self.model: Fourier1dModel = None

        # 無効化する周波数成分のインデックスを保持する。
        self.index: int = 0

        # 編集前の実部の値を保持する。
        self.oldRealPart: float = 0.0

        # 編集前の虚部の値を保持する。
        self.oldImaginaryPart: float = 0.0

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定インデックスの編集前の実部と虚部を保存し、その周波数成分を無効化する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定インデックスのスペクトル成分を編集前の状態に戻す。
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

