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

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self) -> None:
        # まとめて管理するSpectrumEditCommandのリストを保持する。
        self.commands: list[SpectrumEditCommand] = []

        # SAFE CODE AREA ˅
        # 子Command追加時に、View通知用の変更種別を引き継ぐ。
        self.spectrumChangeKind: str = "full"
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.add ˅
    def add(self, command: SpectrumEditCommand) -> None:
        """
        指定されたSpectrumEditCommandをcommandsに追加する。
        """

        # SAFE CODE AREA ˅
        # ドラッグ中に発生した個別編集Commandを順序付きで保持する。
        self.commands.append(command)
        self.spectrumChangeKind = command.spectrumChangeKind
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.add ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        commandsに保持されたCommandを順に実行する。
        """

        # SAFE CODE AREA ˅
        # Redo時は、ドラッグ中に行われた編集と同じ順番で再実行する。
        for command in self.commands:
            command.execute()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        commandsに保持されたCommandを実行時と逆順に取り消す。
        """

        # SAFE CODE AREA ˅
        # Undo時は最後に行った編集から逆順に戻し、ドラッグ前の状態へ戻す。
        for command in reversed(self.commands):
            command.undo()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        このCompositeCommandの内容を説明する文字列を返す。
        """

        # SAFE CODE AREA ˅
        # デバッグや履歴表示用に、まとめられたCommand数を返す。
        return f"Composite Command: {len(self.commands)} sub-commands"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
