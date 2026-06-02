from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np
from .fourier_2_d_model import Fourier2dModel
from .snapshot import Snapshot
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class Set2dSourceDataCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    2次元モデルに新しい元データを設定するCommandである。実行前の状態をSnapshotとして保存し、Undo時には読み込み前の状態に戻す。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, model: Fourier2dModel, newSourceData: np.ndarray) -> None:
        """
        操作対象のFourier2dModelと新しい2次元元データを受け取り、Commandを初期化する。
        """

        # 操作対象となるFourier2dModelを保持する。
        self.model: Fourier2dModel = model

        # 新しい2次元データを設定する前のModel状態を保持する。
        self.oldSnapshot: Snapshot = model.createSnapshot()

        # 新しく設定する2次元元データを保持する。
        self.newSourceData: np.ndarray = newSourceData

        # SAFE CODE AREA ˅
        self.newSourceData = np.copy(newSourceData)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        現在のModel状態をSnapshotとして保存した後、新しい2次元元データをModelに設定する。
        """

        # SAFE CODE AREA ˅
        self.oldSnapshot = self.model.createSnapshot()
        self.model.setSourceData(self.newSourceData)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldSnapshotを用いて、2次元元データ設定前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        self.model.restoreSnapshot(self.oldSnapshot)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        return "Set 2D Source Data"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
