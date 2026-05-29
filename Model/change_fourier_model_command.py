from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .fourier_model import FourierModel
from .fourier_model_context import FourierModelContext
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

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

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, context: FourierModelContext, newModel: FourierModel) -> None:
        """
        操作対象のFourierModelContextと差し替え後のFourierModelを受け取り、Commandを初期化する。
        """

        # 現在のModelを管理するFourierModelContextを保持する。
        self.context: FourierModelContext = None

        # 差し替え前のFourierModelを保持する。
        self.oldModel: FourierModel = None

        # 差し替え後のFourierModelを保持する。
        self.newModel: FourierModel = None

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        現在のModelをoldModelとして保存し、contextのcurrentModelをnewModelへ差し替える。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        contextのcurrentModelをoldModelへ戻す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        このCommandの内容を説明する文字列を返す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄

