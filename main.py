# coding=utf-8
import libBridge
choice = -1
while choice != 1 and choice != 2:
    choice = input("""选择工作模式：
1.下载网易云单曲
2.下载网易云歌单
>>> """)
if choice == 1:
    songID = input("请输入歌曲ID：")
    libBridge.dloadBeatmapFromID(songID)
elif choice == 2:
    playlistID = input("请输入歌单ID：")
    libBridge.dloadBeatmapFromPlaylist(playlistID)

