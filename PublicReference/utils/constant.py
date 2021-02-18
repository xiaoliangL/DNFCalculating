import multiprocessing
import queue
import threading
import time
import os
import math

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl

from PublicReference import logger
from .calc_core import CalcData
from .common import format_time
from .minheap import MinHeap, MinHeapWithQueue, batch_size
from .producer_consumer import producer, producer_data, thread_num, thread_task
from .copy import *

#100级史诗套数据
防具套装 = ["古代祭祀的神圣仪式", "遗忘魔法师的馈赠", "天堂舞姬", "死亡阴影", "皇家裁决者宣言", "龙血玄黄", "贫瘠沙漠的遗产", "炙炎之盛宴", "擎天战甲", "噩梦：地狱之路", "传奇铁匠-封神", "荆棘漫天", "永恒不息之路", "命运歧路", "大自然的呼吸"]
首饰套装 = ["上古尘封术士", "破晓曦光", "幸运三角", "精灵使的权能"]
特殊套装 = ["军神的隐秘遗产", "灵宝：世间真理", "时间战争的残骸", "能量主宰"]
上链左套装 = ["深渊窥视者", "圣者的黄昏", "坎坷命运", "吞噬愤怒"]
镯下右套装 = ["黑魔法探求者", "时空旅行者", "穿透命运的呐喊", "狂乱追随者"]
环鞋指套装 = ["地狱求道者", "次元旅行者", "天命无常", "悲剧的残骸"]

部位列表 = ["上衣", "头肩", "下装", "腰带", "鞋", "手镯", "项链", "戒指", "耳环", "辅助装备", "魔法石", "武器"]
部位字典 = {"上衣":0, "头肩":1, "下装":2, "腰带":3, "鞋":4, "手镯":5, "项链":6, "戒指":7, "耳环":8, "辅助装备":9, "魔法石":10, "武器":11}

颜色 = {'神话':'#E0502F', '史诗':'#FFB400', '传说':'#FF7800'}

总套装列表 = [防具套装, 首饰套装, 特殊套装, 上链左套装, 镯下右套装, 环鞋指套装]
所有套装列表 = 防具套装 + 首饰套装 + 特殊套装 + 上链左套装 + 镯下右套装 + 环鞋指套装

#部分控件样式
按钮样式 = 'QPushButton{font-size:12px;color:white;background-color:rgba(70,134,197,0.8);border:1px;border-radius:10px} QPushButton:hover{background-color:rgba(65,105,225,0.8)}'
按钮样式2 = 'QPushButton{background-color:rgba(0,0,0,0);border:1px;border-radius:5px} QPushButton:hover{background-color:rgba(252,224,0,0.2)}'
按钮样式3 = 'QPushButton{font-size:13px;color:white;background-color:rgba(255,255,255,0.1);border:1px;border-radius:5px} QPushButton:hover{background-color:rgba(65,105,225,0.5)}'
不可点击按钮样式 = 'QPushButton{font-size:12px;color:white;background-color:grey;border:1px;border-radius:10px}'

复选框样式 = "QCheckBox{font-size:12px;color:white;background-color:rgba(70,134,197,0.8);border:1px;border-radius:3px} QCheckBox:hover{background-color:rgba(65,105,225,0.8)}"
不可勾选复选框样式 = "QCheckBox{font-size:12px;color:white;background-color:grey;border:1px;border-radius:3px} QCheckBox:hover{background-color:rgba(65,105,225,0.8)}"

标签样式 = "QLabel{font-size:12px;color:white}"

下拉框样式 = '''QComboBox{font-size:12px;color:white;background-color:rgba(70,134,197,0.8);border:1px;border-radius:5px;} QComboBox:hover{background-color:rgba(65,105,225,0.8)} QComboBox QAbstractItemView::item {height: 18px;background-color:white} 
QComboBox QAbstractItemView::item:hover,QComboBox QAbstractItemView::item:focus {background-color:rgba(65,105,225,0.5);color:black}
QComboBox QScrollBar{
    background: white !important
}
QComboBox QScrollBar::handle{
    background: rgb(220,220,220) !important
}
'''
不可选择下拉框样式 = "QComboBox{font-size:12px;color:white;background-color:grey;border:1px;border-radius:5px;}  QComboBox QAbstractItemView::item {height: 18px;}"
滚动条样式 = '''/*QScrollBar Style*/
/*纵向滚动条*/
QScrollBar {
    background: transparent; /*背景透明*/
    width: 10px; /*宽度*/
    margin: 0px 0px 0px 0px; /**/
    padding-top: 5px; /*距离上面12px*/
    padding-bottom: 5px; /*距离底部12px*/
}
/*纵向滚动条上面的滑块*/
QScrollBar::handle {
    background: rgba(245,245,245,50);
    width: 10px;
    border-radius: 5px;
    border: none;
}
/*纵向滚动条下部分块*/
QScrollBar::add-page:vertical {
    width: 10px;
    background: transparent;
}
/*横向滚动条后面部分块*/
QScrollBar::add-page:horizontal {
    height: 10px;
    background: transparent;
}
/*纵向滚动条上面部分块*/
QScrollBar::sub-page:vertical {
    width: 10px;
    background: transparent;
}
/*横向滚动条左部分块*/
QScrollBar::sub-page:horizontal {
    height: 10px;
    background: transparent;
}
/*纵向滚动条顶部三角形位置*/
QScrollBar::sub-line:vertical {
    height: 12px;
    width: 10px;
    background: transparent;
    subcontrol-position: top;
}
/*横向滚动条左侧三角形位置*/
QScrollBar::sub-line:horizontal {
    height: 10px;
    width: 12px;
    background: transparent;
    subcontrol-position: left;
}
/*纵向滚动条下面三角形部分*/
QScrollBar::add-line:vertical {
    height: 12px;
    width: 10px;
    background: transparent;
    subcontrol-position: bottom;
}
/*横向滚动条右边的三角形部分*/
QScrollBar::add-line:horizontal {
    height: 10px;
    width: 12px;
    background: transparent;
    subcontrol-position: right;
}
'''

class MyQComboBox(QComboBox):
    def __init__(self, win):
        super().__init__(win)
        self.setView(QListView())
        self.setStyleSheet(下拉框样式)

