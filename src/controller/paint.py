#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ˅
from edit import Edit


# ˄


class Paint(Edit):
    # ˅
    
    # ˄

    # スライダーやUIからペンの大きさを変更した際に呼び出します。
    def setBrushSize(self, aSize):
        # ˅
        pass
        # ˄

    # なぞった場所を「どれくらいの値（強さ）に書き換えるか」を設定します。
    def setPaintValue(self, aValue):
        # ˅
        pass
        # ˄

    # MouseEventHandler から呼ばれ、現在設定されている brushSize と paintValue を使って、指定座標 (aX, aY) を中心とする円形（または矩形）の範囲の周波数データを書き換えます。
    def applyPaintFilter(self, aX, aY):
        # ˅
        pass
        # ˄

    # ˅
    
    # ˄


# ˅

# ˄
