from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_2_d_model import Fourier2dModel
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class EraseSpectrumAtPositionsCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    2次元スペクトルの指定位置周辺の成分を無効化するCommandである。指定された行、列、半径に基づいて編集範囲を決定し、Undo時に元の値へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # 線分上の複数点を1つのCommandとして扱い、execute/undo時の逆FFT回数を抑える。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier2dModel, positions: list[tuple[int, int]], radius: int) -> None:
        """
        操作対象のFourier2dModel、編集対象位置、編集半径を受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier2dModelを保持する。
        self.model: Fourier2dModel = model

        # 編集対象範囲の半径を保持する。
        self.radius: int = 0

        # 編集前の範囲に対応する実部配列を保持する。
        self.oldRealPart: np.ndarray = np.array([])

        # 編集前の範囲に対応する虚部配列を保持する。
        self.oldImaginaryPart: np.ndarray = np.array([])

        self.positions: list[tuple[int, int]] = []

        self.rect: tuple[int, int, int, int] = (0, 0, 0, 0)

        # SAFE CODE AREA ˅
        # View通知では2Dスペクトルの矩形部分更新として扱う。
        self.spectrumChangeKind: str = "2d"
        # 自動生成の初期値を実際の引数で上書きし、操作対象Modelを保持する。
        # 呼び出し元のリスト変更がCommand内部へ影響しないよう、座標を整数tupleとしてコピーする。
        self.positions = [(int(row), int(col)) for row, col in positions]
        self.radius = max(0, int(radius))
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        指定範囲の編集前の実部と虚部を保存し、その範囲のスペクトル成分を無効化する。
        """

        # SAFE CODE AREA ˅
        # 複数ブラシをすべて含む矩形だけを保存し、Undo用データ量を必要範囲に絞る。
        self.rect = self.model.getSpectrumRectForPositions(self.positions, self.radius)
        self.oldRealPart, self.oldImaginaryPart = self.model.getInteractiveSpectrumAtRect(*self.rect)

        # Modelの一括消去を呼ぶため、線分上の点数に関係なく逆FFTは1回だけ実行される。
        self.model.eraseSpectrumAtPositions(self.positions, self.radius)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldRealPartとoldImaginaryPartを用いて、指定範囲のスペクトル成分を編集前の状態に戻す。
        """

        # SAFE CODE AREA ˅
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
        return f"Erase Spectrum at {len(self.positions)} positions with radius {self.radius}"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
