from __future__ import annotations

# FIXED CODE AREA: module.imports ˅
from typing import TYPE_CHECKING
from .fourier_model import FourierModel
from .spectrum_edit_command import SpectrumEditCommand

if TYPE_CHECKING:
    from .fourier_model_context import FourierModelContext

# FIXED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class ChangeFourierModelCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    現在使用しているFourierModelを別のFourierModelへ差し替えるCommandである。1次元モデルと2次元モデルを切り替える場合に使用し、Undo時には差し替え前のModelへ戻す。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, context: FourierModelContext, newModel: FourierModel) -> None:
        """
        操作対象のFourierModelContextと差し替え後のFourierModelを受け取り、Commandを初期化する。
        """

        # 現在のModelを管理するFourierModelContextを保持する。
        self.context: FourierModelContext = context

        # 差し替え前のFourierModelを保持する。
        self.oldModel: FourierModel = context.currentModel

        # 差し替え後のFourierModelを保持する。
        self.newModel: FourierModel = newModel

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        現在のModelをoldModelとして保存し、contextのcurrentModelをnewModelへ差し替える。
        """

        # SAFE CODE AREA ˅
        self.context.currentModel = self.newModel
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        contextのcurrentModelをoldModelへ戻す。
        """

        # SAFE CODE AREA ˅
        self.context.currentModel = self.oldModel
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        このCommandの内容を説明する文字列を返す。
        """

        # SAFE CODE AREA ˅
        return f"Change FourierModel: {self.oldModel} -> {self.newModel}"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄

