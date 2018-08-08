# coding=utf-8
import os

import libBridge
choice = -1
while choice != 1 and choice != 2:
    choice = libBridge.input_gbk_numbersonly("""选择工作模式：
1.下载网易云单曲
2.下载网易云歌单
>>> """)
if choice == 1:
    songID = libBridge.input_gbk_numbersonly("请输入歌曲ID：")
    libBridge.dloadBeatmapFromID(songID)
elif choice == 2:
    playlistID = libBridge.input_gbk_numbersonly("请输入歌单ID：")
    libBridge.dloadBeatmapFromPlaylist(playlistID)
os.system("pause")