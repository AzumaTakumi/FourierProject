from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .fourier_1_d_model import Fourier1dModel
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class RestoreSpectrumAtIndexCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元スペクトルの指定インデックスの成分を、フーリエ変換直後の元スペクトル値に戻すCommandである。Undo時には復元前の値へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier1dModel, index: int) -> None:
        """
        操作対象のFourier1dModelと復元対象インデックスを受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier1dModelを保持する。
        self.model: Fourier1dModel = None

        # 元スペクトル値に戻す周波数成分のインデックスを保持する。
        self.index: int = 0

        # 復元前の実部の値を保持する。
        self.oldRealPart: float = 0.0

        # 復元前の虚部の値を保持する。
        self.oldImaginaryPart: float = 0.0

        # SAFE CODE AREA ˅
        self.model = model
        self.index = index
        self.oldRealPart, self.oldImaginaryPart = self.model._getInteractiveSpectrumAtIndex(index)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定インデックスの編集前の実部と虚部を保存し、その成分を元のフーリエ変換結果に戻す。
        """

        # SAFE CODE AREA ˅
        self.oldRealPart, self.oldImaginaryPart = self.model._getInteractiveSpectrumAtIndex(self.index)
        self.model.restoreSpectrumAtIndex(self.index)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定インデックスのスペクトル成分を復元前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        self.model.editSpectrumValueAtIndex(self.index, self.oldRealPart, self.oldImaginaryPart)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        return f"Restore Spectrum at index {self.index}"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
