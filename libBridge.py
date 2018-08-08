# coding=utf-8
import cloudMusicAPI
import json
import requests
import langid
import difflib

urlBloodCatQuery_Base = "https://bloodcat.com/osu/?mod=json&q="
urlBloodCatDload_Base = "https://bloodcat.com/osu/s/"
urlCloudMusicPlaylist_Base = "http://music.163.com/api/playlist/detail?id="
fileName_Base = ".osz"
strCookie = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzM2OTAzNjcsImlwIjoiMTgyLjIwMC4xMjkuMTQzIiwidWEiOjI2ODkyMTg5OTh9.taD8Ftb0H7_pfdK9OP5uVdXjpBgz3IxxZxki0UAvZUE"
# Override print() for CMD users
def print_gbk(str):
    print(str.decode("utf-8").encode("gbk"))

# Override input() for CMD users
def input_gbk_numbersonly(str):
    return int(raw_input(str.decode("utf-8").encode("gbk")))

# 检查并设置captcha cookie
def getCookie(op = 0):
    global strCookie
    cookieHeader = "obm_human="
    if strCookie == "" or op == -1:
        strCookie = raw_input("请输入一个Cookie：".decode("utf-8").encode("gbk"))
    return cookieHeader + strCookie

# 刷新headers
def setHeaders():
    cookie = getCookie()
    __headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
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

# 通用下载接口 返回-1会强制触发cookie检查
def dloadFile(url,fileName,headers = {}):
    print_gbk ("正在下载：" + url)
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        print_gbk("下载完成，正在写入文件：" + fileName)
        file = open(fileName, 'wb')
        for chunk in r.iter_content(100000):
            file.write(chunk)
        file.close()
        return 0
    else:
        print_gbk("下载失败，请检查Cookie！")
        getCookie(-1)
        return -1

# 使用网易云ID搜索血猫，返回谱面ID(list)
def retrieveSongFromID(__songID,workMode = 0): # Unconverted
    # workMode：0 = 只下载一个匹配，1 = 下载所有匹配
    targetSongDetail = cloudMusicAPI.req_netease_detail(__songID)
    targetSongName = targetSongDetail['name']
    url = urlBloodCatQuery_Base + targetSongName + "&c=b&p=1&s=&m=&g=&l="
    r = requests.get(url)
    __dictResult = json.loads(r.content)
    __matchSongID = []
    conv = getConverter()
    if langid.classify(targetSongName)[0] == 'ja':
        flagJapanese = 1
        parsedTargetTitle = str(conv.do(targetSongName)).replace("-","")
        # print "Japanese found!" # for debug purposes
    else:
        parsedTargetTitle = targetSongName
        flagJapanese = 0
    #FINISHED:去掉罗马音里的空格来进行歌名比对，使用长度进行验证
    for __eachSong in __dictResult:
        # print_gbk eachSong['title']
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
    print_gbk("匹配到的谱面ID：" + str(__matchSongID))
    return __matchSongID

# 从网易云歌单获取歌曲名字，返回歌曲名字(unicode,list)
def retrieveNameFromPlaylist(__playlistID):
    url = urlCloudMusicPlaylist_Base + str(__playlistID)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
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
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    r = requests.get(url,headers = headers)
    __dictResult = json.loads(r.content)
    print_gbk ("歌单名称："),
    print (__dictResult['result']['name'])
    print_gbk ("歌曲数："),
    print (__dictResult['result']['trackCount'])
    trackIDs = []
    for __eachTrack in __dictResult['result']['tracks']:
        trackIDs.append(__eachTrack['id'])
    return trackIDs

# 使用 **网易云ID** 下载谱面
def dloadBeatmapFromID(__songID):
    matchSongID = retrieveSongFromID(__songID)
    headers = setHeaders()
    for __eachID in matchSongID:
        url = urlBloodCatDload_Base + str(__eachID)
        while(dloadFile(url,str(__eachID) + fileName_Base,headers) != 0):
            headers = setHeaders()

# 从网易云歌单下载谱面
def dloadBeatmapFromPlaylist(__playlistId):
    trackIDs = retrieveIDFromPlaylist(__playlistId)
    for __eachID in trackIDs:
        dloadBeatmapFromID(__eachID)

# convertedTargetSongName = conv.do(targetSongName)
