# coding=utf-8
import cloudMusicAPI
import json
import requests
import langid
import difflib
import os
# from requests import adapters

# Experimental Code!!!
# requests.adapters.DEFAULT_RETRIES = 5

# Resources
debugFlag = 0
debugObject = ""
urlBloodCatQuery_Base = "https://bloodcat.com/osu/?mod=json&q="
urlBloodCatDload_Base = "https://bloodcat.com/osu/s/"
urlCloudMusicPlaylist_Base = "http://music.163.com/api/playlist/detail?id="
fileName_Base = ".osz"
strCookie = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzM3NzUxNzQsImlwIjoiMTgyLjIwMC4xMjkuMTQzIiwidWEiOjMzNjIwMTI5NTd9.9JwsQIDDgcVVOIC4PX4-OEVIN1PVsXScyST5WAGLquY"
strUA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
sessionBloodCat = ""

# Override print() for CMD users
def print_gbk(str):
    print(str.decode("utf-8").encode("gbk"))

# Override input() for CMD users
def input_gbk_numbersonly(str):
    return int(raw_input(str.decode("utf-8").encode("gbk")))

#检查并设置User Agent （UA和Cookies是直接相关的，必须同时刷新）
def getUA(__op = 0):
    global strUA
    if strUA == "" or __op == -1:
        strUA = raw_input("请输入一个UA：".decode("utf-8").encode("gbk"))
    return strUA

# 检查并设置captcha cookie
def getCookie(__op = 0):
    global strCookie
    cookieHeader = "obm_human="
    if strCookie == "" or __op == -1:
        strCookie = raw_input("请输入一个Cookie：".decode("utf-8").encode("gbk"))
        if strCookie == 'debug':
            raise RuntimeError
    return cookieHeader + strCookie

# 刷新headers
def setHeaders():
    cookie = getCookie()
    ua = getUA()
    __headers = {
        'user-agent': ua,
        'referer': 'https://bloodcat.com/osu',
        'cookie': cookie}
    return __headers

# 获取一个罗马音转换器
def getConverter():
    import sys  # reload()之前必须要引入模块
    reload(sys)
    sys.setdefaultencoding('utf-8') # 防止UTF8出问题
    from pykakasi import kakasi
    kakasi = kakasi()
    kakasi.setMode('H', 'a')
    kakasi.setMode('K', 'a')
    kakasi.setMode('J', 'a')
    conv = kakasi.getConverter()
    return conv

# 获取活动连接
def getSession():
    global sessionBloodCat
    if sessionBloodCat == "":
        refreshSession()
    return sessionBloodCat

# 刷新连接
def refreshSession():
    global sessionBloodCat
    sessionBloodCat = requests.session()
    sessionBloodCat.headers.update(setHeaders())

# 通用下载接口 返回-1会强制触发cookie检查
def dloadFile(url,fileName = '',headers = {}):
    print_gbk ("正在下载：" + url)
    # FINISHED:复用连接并加入重试
    # r = requests.get(url,headers=headers)
    s = getSession()
    if headers != {}:
        s = requests.session()
        s.headers.update(headers)
    try: # 监测网络错误
        r = s.get(url)
    except:
        print_gbk("正在重试.....")
        return -1 # -1 for network error
    if r.status_code == 200:
        if fileName != '':
            fileName = fileName
        else :
            fileName = r.headers['Content-Disposition'].split('"')[1]
        print_gbk("下载完成，正在写入文件：" + fileName)
        file = open(fileName, 'wb')
        for chunk in r.iter_content(100000):
            file.write(chunk)
        file.close()
        return 0
    else:
        # ↓调试代码
        if debugFlag == 1:
            global debugObject
            debugObject = r
            print(r.status_code)
            return 0
        # ↑调试代码
        print_gbk("下载失败，请检查参数！")
        getCookie(-1)
        getUA(-1)
        refreshSession()
        return -1

# 使用网易云ID搜索血猫，返回谱面ID(list)
def retrieveSongFromID(__songID,workMode = 0): # Unconverted
    # workMode：0 = 只下载一个匹配，1 = 下载所有匹配
    targetSongDetail = cloudMusicAPI.req_netease_detail(__songID)
    targetSongName = targetSongDetail['name']
    url = urlBloodCatQuery_Base + targetSongName + "&c=b&p=1&s=&m=&g=&l="
    r = requests.get(url)
    try:
        __dictResult = json.loads(r.content)
    except ValueError:
        print_gbk("网络错误，通常重试一下就可以解决，程序即将退出...")
        os.system('pause')
        __dictResult = {} # 我恨死语法检查了
    __matchSongID = []
    conv = getConverter()
    if langid.classify(targetSongName)[0] == 'ja':
        flagJapanese = 1
        parsedTargetTitle = str(conv.do(targetSongName)).replace("-","")
        # print(parsedTargetTitle)
        # print "Japanese found!" # for debug purposes
    else:
        parsedTargetTitle = targetSongName
        flagJapanese = 0
    #FINISHED:去掉罗马音里的空格来进行歌名比对，使用长度进行验证
    for __eachSong in __dictResult:
        # print_gbk(__eachSong['title'])
        if flagJapanese == 0:
            if __eachSong['title'] == parsedTargetTitle:
                print_gbk("找到匹配：")
                print_gbk(__eachSong['title']),
                print_gbk("艺术家："),
                print_gbk(__eachSong['artist'])
                __matchSongID.append(int(__eachSong['id'].decode('utf-8')))
                if workMode == 0:
                    break
        elif flagJapanese == 1:
            # 我们在这里有： - parsedTargetTitle 处理后的全小写罗马音，来自网易云
            #              - __eachSong['title']，来自血猫
            prettifiedResultName = str(__eachSong['title']).lower().replace(" ","") # 移除空格和大写
            seq = difflib.SequenceMatcher(None,prettifiedResultName,parsedTargetTitle)
            if seq.ratio() >= 0.5:
                print_gbk("找到匹配：")
                print_gbk(__eachSong['title']),
                print_gbk("艺术家："),
                print_gbk(__eachSong['artist'])
                __matchSongID.append(int(__eachSong['id'].decode('utf-8')))
                if workMode == 0:
                    break
    if __matchSongID != []:
        print_gbk("匹配到的谱面ID：" + str(__matchSongID))
    else: print_gbk("没有找到匹配！")

    return __matchSongID

# 从网易云歌单获取歌曲名字，返回歌曲名字(unicode,list)
def retrieveNameFromPlaylist(__playlistID):
    url = urlCloudMusicPlaylist_Base + str(__playlistID)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
    print_gbk("如果歌单曲目较多（超过500首），可能需要较长时间获取，请耐心等待...")
    print_gbk("出现Connnection Broken错误即为网络不稳定，可以多试几次")
    r = requests.get(url,headers = headers)
    __dictResult = json.loads(r.content)
    print_gbk ("歌单名称："),
    print_gbk (__dictResult['result']['name'])
    print_gbk ("歌曲数："),
    print_gbk (__dictResult['result']['trackCount'])
    trackNames = []
    for __eachTrack in __dictResult['result']['tracks']:
        trackNames.append(__eachTrack['name'])
    return trackNames

# 从网易云歌单获取歌曲ID，返回歌曲ID(int,list)
def retrieveIDFromPlaylist(__playlistID):
    url = urlCloudMusicPlaylist_Base + str(__playlistID)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
    print_gbk("如果歌单曲目较多（超过500首），可能需要较长时间获取，请耐心等待...")
    print_gbk("出现Connection Broken错误即为网络不稳定，可以多试几次")

    dloadFile(url,'nowWorkingOn.list',headers)
    f = open('nowWorkingOn.list','r')
    __content = f.read()
    f.close()

    try:
        __dictResult = json.loads(__content)
    except ValueError:
        print_gbk("网络错误，通常重试一下就可以解决，程序即将退出...")
        os.system('pause')
        __dictResult = {} # 我恨死语法检查了

    print_gbk ("歌单名称："),
    print (__dictResult['result']['name'])
    print_gbk ("歌曲数："),
    print (__dictResult['result']['trackCount'])
    trackIDs = []
    for __eachTrack in __dictResult['result']['tracks']:
        trackIDs.append(__eachTrack['id'])
    os.remove('nowWorkingOn.list')
    return trackIDs

# 使用 **网易云ID** 下载谱面
def dloadBeatmapFromID(__songID):
    matchSongID = retrieveSongFromID(__songID)
    headers = setHeaders()
    for __eachID in matchSongID:
        url = urlBloodCatDload_Base + str(__eachID)
        while dloadFile(url) == -1:
            dloadFile(url)

# 从网易云歌单下载谱面
def dloadBeatmapFromPlaylist(__playlistId):
    trackIDs = retrieveIDFromPlaylist(__playlistId)
    for __eachID in trackIDs:
        dloadBeatmapFromID(__eachID)