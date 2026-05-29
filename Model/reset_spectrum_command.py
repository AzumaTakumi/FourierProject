from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .fourier_model import FourierModel
from .snapshot import Snapshot
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class ResetSpectrumCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    編集用スペクトル全体を、フーリエ変換直後の元スペクトル状態に戻すCommandである。Undo時にはリセット前の編集状態へ戻せるようにする。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, model: FourierModel) -> None:
        """
        操作対象のFourierModelを受け取り、Commandを初期化する。
        """

        # 操作対象となるFourierModelを保持する。
        self.model: FourierModel = None

        # スペクトルリセット前のModel状態を保持する。
        self.oldSnapshot: Snapshot = None

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        現在のModel状態をSnapshotとして保存した後、編集用スペクトルを元スペクトル状態へ戻す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        保存しておいたoldSnapshotを用いて、スペクトルリセット前の状態に戻す。
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

