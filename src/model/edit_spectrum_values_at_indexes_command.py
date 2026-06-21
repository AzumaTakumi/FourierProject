from __future__ import annotations

import numpy as np

from .fourier_1_d_model import Fourier1dModel
from .spectrum_edit_command import SpectrumEditCommand


class EditSpectrumValuesAtIndexesCommand(SpectrumEditCommand):
    """
    1次元スペクトルの複数インデックスをまとめて変更するCommandである。
    """

    def __init__(
        self,
        model: Fourier1dModel,
        indexes: list[int],
        newRealParts: np.ndarray,
        newImaginaryParts: np.ndarray,
    ) -> None:
        self.model: Fourier1dModel = model
        self.indexes: list[int] = [int(index) for index in indexes]
        self.oldRealParts: np.ndarray = np.array([])
        self.oldImaginaryParts: np.ndarray = np.array([])
        self.newRealParts: np.ndarray = np.asarray(newRealParts, dtype=float).copy()
        self.newImaginaryParts: np.ndarray = np.asarray(newImaginaryParts, dtype=float).copy()

        # View通知では1Dスペクトルの部分更新として扱う。
        self.spectrumChangeKind: str = "1d"

    def execute(self) -> None:
        # Undoで戻す値は、実行直前のinteractive値として保存する。
        old_values = [self.model.getInteractiveSpectrumAtIndex(index) for index in self.indexes]
        self.oldRealParts = np.asarray([real_part for real_part, _ in old_values], dtype=float)
        self.oldImaginaryParts = np.asarray([imaginary_part for _, imaginary_part in old_values], dtype=float)

        self.model.editSpectrumValuesAtIndexes(self.indexes, self.newRealParts, self.newImaginaryParts)

    def undo(self) -> None:
        self.model.editSpectrumValuesAtIndexes(self.indexes, self.oldRealParts, self.oldImaginaryParts)

    def description(self) -> str:
        return f"Edit Spectrum at {len(self.indexes)} indexes"
