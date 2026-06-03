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

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier1dModel, index: int) -> None:
        """
        操作対象のFourier1dModelと編集対象インデックスを受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier1dModelを保持する。
        self.model: Fourier1dModel = model

        # 無効化する周波数成分のインデックスを保持する。
        self.index: int = index

        # 編集前の実部の値を保持する。
        self.oldRealPart: float = self.model.realPart[index]

        # 編集前の虚部の値を保持する。
        self.oldImaginaryPart: float = self.model.imaginaryPart[index]

        # SAFE CODE AREA ˅
        # Undoでは元スペクトルではなく「編集直前のinteractive値」へ戻す必要があるため現在値を保存する。
        self.oldRealPart, self.oldImaginaryPart = self.model.getInteractiveSpectrumAtIndex(index)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定インデックスの編集前の実部と虚部を保存し、その周波数成分を無効化する。
        """

        # SAFE CODE AREA ˅
        # Redo時も直前状態を取り直し、連続操作後のUndo先が古くならないようにする。
        self.oldRealPart, self.oldImaginaryPart = self.model.getInteractiveSpectrumAtIndex(self.index)
        # Model本体に削除処理を任せ、逆変換結果もそこで更新させる。
        self.model.eraseSpectrumAtIndex(self.index)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定インデックスのスペクトル成分を編集前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        # 保存していたinteractive値を直接書き戻し、削除前の編集状態へ戻す。
        self.model.editSpectrumValueAtIndex(self.index, self.oldRealPart, self.oldImaginaryPart)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        # デバッグや履歴表示用に、対象indexと保存値を文字列化する。
        return f"Erase Spectrum at index {self.index}: ({self.oldRealPart} + {self.oldImaginaryPart}j)"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
