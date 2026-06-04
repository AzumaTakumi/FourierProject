from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class SpectrumEditCommand(object):
    # GENERATED CODE AREA: class.header ˅
    # SAFE CODE AREA ˅
    # 具象Commandがexecute/undo/descriptionを実装するための共通インターフェースとして使う。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        Commandが表す編集操作を実行する。
        """

        # SAFE CODE AREA ˅
        # 基底クラスでは処理を持たない。具象Command側で編集内容を実装する。
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        Commandが表す編集操作を取り消し、実行前の状態に戻す。
        """

        # SAFE CODE AREA ˅
        # 基底クラスでは処理を持たない。具象Command側で取り消し処理を実装する。
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        「このコマンドが何をする操作なのか」を文字列で返す。
        """

        # SAFE CODE AREA ˅
        # 基底クラスでは説明を持たない。具象Command側で履歴表示用文字列を返す。
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
