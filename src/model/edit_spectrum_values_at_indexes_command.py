from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .fourier_1_d_model import Fourier1dModel
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
import numpy as np
# SAFE CODE AREA ˄

class EditSpectrumValuesAtIndexesCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元スペクトルの指定インデックスの値を任意の実部・虚部に変更するCommandである。編集前の値を保存し、Undo時に元の値へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(
        self,
        model: Fourier1dModel,
        indexes: list[int],
        newRealParts: np.ndarray,
        newImaginaryParts: np.ndarray,
    ) -> None:
        """
        操作対象のFourier1dModel、編集対象インデックス列、新しく設定する実部列と虚部列を受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier1dModelを保持する。
        self.model: Fourier1dModel = model

        # 値を変更する複数の周波数成分インデックスを保持する。
        self.indexes: list[int] = [int(value) for value in np.atleast_1d(indexes)]

        # 編集前の先頭インデックスの実部の値を保持する。
        self.oldRealPart: float = 0.0

        # 編集前の先頭インデックスの虚部の値を保持する。
        self.oldImaginaryPart: float = 0.0

        # 編集前の実部の値を保持する。
        self.oldRealParts: np.ndarray = np.array([])

        # 編集前の虚部の値を保持する。
        self.oldImaginaryParts: np.ndarray = np.array([])

        # 新しく設定する実部の値を保持する。
        new_real_parts = np.asarray(newRealParts, dtype=float)
        self.newRealParts: np.ndarray = (
            new_real_parts.reshape(1) if new_real_parts.ndim == 0 else new_real_parts.copy()
        )
        self.newRealPart: float = float(self.newRealParts[0]) if self.newRealParts.size else 0.0

        # 新しく設定する虚部の値を保持する。
        new_imaginary_parts = np.asarray(newImaginaryParts, dtype=float)
        self.newImaginaryParts: np.ndarray = (
            new_imaginary_parts.reshape(1) if new_imaginary_parts.ndim == 0 else new_imaginary_parts.copy()
        )
        self.newImaginaryPart: float = float(self.newImaginaryParts[0]) if self.newImaginaryParts.size else 0.0

        # 該当コマンド実行による影響範囲を示す
        self.spectrumChangeKind: str = "1d"

        # SAFE CODE AREA ˅
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定インデックスの編集前の実部と虚部を保存し、新しい実部と虚部の値を設定する。
        """

        # SAFE CODE AREA ˅
        # Undoで戻す値は、実行直前のinteractive値として保存する。
        old_values = [self.model.getInteractiveSpectrumAtIndex(index) for index in self.indexes]
        self.oldRealParts = np.asarray([real_part for real_part, _ in old_values], dtype=float)
        self.oldImaginaryParts = np.asarray([imaginary_part for _, imaginary_part in old_values], dtype=float)
        self.oldRealPart = float(self.oldRealParts[0]) if self.oldRealParts.size else 0.0
        self.oldImaginaryPart = float(self.oldImaginaryParts[0]) if self.oldImaginaryParts.size else 0.0

        self.model.editSpectrumValuesAtIndexes(self.indexes, self.newRealParts, self.newImaginaryParts)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定インデックスのスペクトル成分を編集前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        self.model.editSpectrumValuesAtIndexes(self.indexes, self.oldRealParts, self.oldImaginaryParts)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        return f"Edit Spectrum at {len(self.indexes)} indexes"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
