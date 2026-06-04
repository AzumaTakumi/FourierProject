from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from enum import Enum, auto

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class PaneType(Enum):
    # GENERATED CODE AREA: class.header ˅
    """
    FourierPaneModel の種類を表す列挙型である。
    
    各ペインが元データ、パワースペクトル、編集用パワースペクトル、逆変換結果のどれを表示するかを識別するために使用する。
    
    定義される値は以下である。
    
    - SOURCE_DATA
    - POWER_SPECTRUM
    - INTERACTIVE_POWER_SPECTRUM
    - INVERSE_DATA
    
    この列挙型を使うことで、ViewやControllerはペインの役割を文字列ではなく型安全な値として判定できる。
    """

    # SAFE CODE AREA ˅
    # 列挙値そのものは自動生成領域にあるため、SAFE内では補助メソッドを追加していない。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: enum.members ˅
    # 元データを表す表示領域を示す。1次元の場合は元波形、2次元の場合は元画像に対応する。
    SOURCE_DATA = auto()

    # フーリエ変換後のパワースペクトルを表す表示領域を示す。編集前のスペクトル表示に対応する。
    POWER_SPECTRUM = auto()

    # ユーザーが編集可能なパワースペクトルを表す表示領域を示す。1次元ではクリック編集、2次元ではペイント編集の対象となる。
    INTERACTIVE_POWER_SPECTRUM = auto()

    # 編集後スペクトルを逆フーリエ変換した結果を表す表示領域を示す。1次元では復元波形、2次元では復元画像に対応する。
    INVERSE_DATA = auto()

    # SAFE CODE AREA ˅
    # 追加のenum値は不要。既存4ペインだけをModel/View間の共通キーとして使う。
    pass
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: enum.members ˄
