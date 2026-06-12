from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .fourier_1_d_model import Fourier1dModel
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class EditSpectrumValueAtIndexCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元スペクトルの指定インデックスの値を任意の実部・虚部に変更するCommandである。編集前の値を保存し、Undo時に元の値へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier1dModel, index: int, newRealPart: float, newImaginaryPart: float) -> None:
        """
        操作対象のFourier1dModel、編集対象インデックス、新しく設定する実部と虚部の値を受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier1dModelを保持する。
        self.model: Fourier1dModel = model

        # 値を変更する周波数成分のインデックスを保持する。
        self.index: int = index

        # 編集前の実部の値を保持する。
        self.oldRealPart: float = self.model.realPart[index]

        # 編集前の虚部の値を保持する。
        self.oldImaginaryPart: float = self.model.imaginaryPart[index]

        # 新しく設定する実部の値を保持する。
        self.newRealPart: float = newRealPart

        # 新しく設定する虚部の値を保持する。
        self.newImaginaryPart: float = newImaginaryPart

        # SAFE CODE AREA ˅
        # View通知では1Dスペクトルの部分更新として扱う。
        self.spectrumChangeKind: str = "1d"
        # Undo先は元スペクトルではなく編集直前のinteractive値なので、Modelから現在値を取得する。
        self.oldRealPart, self.oldImaginaryPart = self.model.getInteractiveSpectrumAtIndex(index)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定インデックスの編集前の実部と虚部を保存し、新しい実部と虚部の値を設定する。
        """

        # SAFE CODE AREA ˅
        # Redo時も直前のinteractive値を取り直し、Undoで戻す値を最新化する。
        self.oldRealPart, self.oldImaginaryPart = self.model.getInteractiveSpectrumAtIndex(self.index)
        # 指定された新しい実部・虚部をModelの編集用スペクトルへ反映する。
        self.model.editSpectrumValueAtIndex(self.index, self.newRealPart, self.newImaginaryPart)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定インデックスのスペクトル成分を編集前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        # 保存していた編集前の実部・虚部を直接書き戻す。
        self.model.editSpectrumValueAtIndex(self.index, self.oldRealPart, self.oldImaginaryPart)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        # デバッグや履歴表示用に、編集前後の複素値を文字列化する。
        return f"Edit Spectrum at index {self.index}: ({self.oldRealPart} + {self.oldImaginaryPart}j) -> ({self.newRealPart} + {self.newImaginaryPart}j)"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
