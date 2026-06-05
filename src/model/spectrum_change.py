from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class SpectrumChange(object):
    # GENERATED CODE AREA: class.header ˅
    """
    スペクトル変更通知でViewへ渡す変更情報の共通クラスである。1次元および2次元の変更情報を扱うための基底的な役割を持つ。
    """

    # SAFE CODE AREA ˅
    # 1D/2D変更通知クラスを同じ型として扱うための基底クラスで、共通状態は持たない。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: class.body ˅
    # SAFE CODE AREA ˅
    # 具体的な通知データはSpectrum1dChange/Spectrum2dChange側のdataclassフィールドで保持する。
    pass
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.body ˄
