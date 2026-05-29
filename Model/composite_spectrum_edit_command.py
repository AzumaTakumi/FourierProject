from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class CompositeSpectrumEditCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    複数のSpectrumEditCommandを1つの編集操作としてまとめるCommandである。ドラッグ操作中に発生した複数のペイント編集や消しゴム編集を、Undo上は1回分の操作として扱うために使用する。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.add ˅
    def add(self, command: SpectrumEditCommand) -> None:
        """
        指定されたSpectrumEditCommandをcommandsに追加する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.add ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        commandsに保持されたCommandを順に実行する。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        commandsに保持されたCommandを実行時と逆順に取り消す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        このCompositeCommandの内容を説明する文字列を返す。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄

