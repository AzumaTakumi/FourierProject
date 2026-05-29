from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_1_d_model import Fourier1dModel
from .snapshot import Snapshot
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class Set1dSourceDataCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元モデルに新しい元データを設定するCommandである。実行前の状態をSnapshotとして保存し、Undo時には読み込み前の状態に戻す。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier1dModel, newSourceData: np.ndarray) -> None:
        """
        操作対象のFourier1dModelと新しい1次元元データを受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier1dModelを保持する。
        self.model: Fourier1dModel = None

        # 新しい1次元データを設定する前のModel状態を保持する。
        self.oldSnapshot: Snapshot = None

        # 新しく設定する1次元元データを保持する。
        self.newSourceData: np.ndarray = None

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        現在のModel状態をSnapshotとして保存した後、新しい1次元元データをModelに設定する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldSnapshotを用いて、1次元元データ設定前の状態に戻す。
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

