'''

先安装必须的包
pip install fastapi uvicorn aiohttp requests bs4

运行，记得要把你云主机的29212端口打开
python -m uvicorn fastapiServerPro:app --host 0.0.0.0 --port 29212 --reload

你的对外地址，即系统中需要填的[推送地址]
http://公网ip:29212/artlist/

核心功能是 56-74行，其他都是下载网页相关的，可以不看

'''
import os
from fastapi import FastAPI, Request, HTTPException
from pprint import pprint
import json,requests
import traceback
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
from time import sleep


SaveJsonDir = "c:\\artlist\\json"
SaveTxtDir = "c:\\artlist\\html"
saveImgDir = "c:\\artlist\\html\\images"

if not os.path.exists(SaveJsonDir):
    os.makedirs(SaveJsonDir)
if not os.path.exists(SaveTxtDir):
    os.makedirs(SaveTxtDir)
if not os.path.exists(saveImgDir):
    os.makedirs(saveImgDir)

def SaveFile(fpath,fileContent):    
    with open(fpath,'w',encoding='UTF-8') as f:
        f.write(fileContent)

def get_current_time_string():
    # 设置时区为东八区（北京时间）
    tz = pytz.timezone('Asia/Shanghai')    
    # 获取当前时间并应用时区
    current_time = datetime.now(tz)    
    # 格式化时间字符串
    time_string = current_time.strftime("%Y-%m-%d_%H-%M-%S_%f")
    
    # 只保留微秒的前三位（毫秒）
    return time_string[:-3]




app = FastAPI() 
@app.post("/artlist/")
async def artlist(request: Request):  
    try:  
        json_data = await request.json()
        pprint(json_data)
        
        # 保存发过来的json数据
        current_time = get_current_time_string() +".txt"
        savepath = os.path.join(SaveJsonDir,current_time)
        SaveFile(savepath,json.dumps(json_data,ensure_ascii=False,indent=4))
        
        # 下载网页，如果不需要可以把这行注释掉
        DownArtList(json_data)
        
        
        return  "success"  
    except:
        print(traceback.format_exc())
    return "error"
    
    
    
    
    
    
    
    
    
    
    
    
    
    

# 下面都是下载网页相关的，可以不看
# 来源于作者的开源项目   https://github.com/LeLe86/vWeChatCrawl
# 下载url网页
def DownLoadHtml(url):
    # 构造请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
    }
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        htmltxt = response.text  # 返回的网页正文
        return htmltxt
    else:
        return None


# 将图片从远程下载保存到本地
def DownImg(url, savepath):
    # 构造请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
    }
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, headers=headers)
    with open(savepath, 'wb') as f:
        f.write(response.content)


# 修改网页中图片的src，使图片能正常显示
def ChangeImgSrc(htmltxt, saveimgdir, htmlname):
    bs = BeautifulSoup(htmltxt, "lxml")  # 由网页源代码生成BeautifulSoup对象，第二个参数固定为lxml
    imgList = bs.findAll("img")
    imgindex = 0
    for img in imgList:
        imgindex += 1
        originalURL = ""  # 图片真实url
        if "data-src" in img.attrs:  # 有的<img 标签中可能没有data-src
            originalURL = img.attrs['data-src']
        elif "src" in img.attrs:  # 如果有src则提取出来
            originalURL = img.attrs['src']
        else:
            originalURL = ""
        if originalURL.startswith("//"):  # 如果url以//开头，则需要添加http：
            originalURL = "http:" + originalURL
        if len(originalURL) > 20:
            print("\r down imgs " + "▇" * imgindex + "  " + str(imgindex), end="")
            if "data-type" in img.attrs:
                imgtype = img.attrs["data-type"]
            else:
                imgtype = "png"
            imgname = htmlname + "_" + str(imgindex) + "." + imgtype  # 形如 1.png的图片名
            imgsavepath = os.path.join(saveimgdir, imgname)  # 图片保存目录
            DownImg(originalURL, imgsavepath)
            img.attrs["src"] = "images/" + imgname  # 网页中图片的相对路径
        else:
            img.attrs["src"] = ""
    ChangeCssSrc(bs)  # 修改link标签
    ChangeContent(bs)  # 修改js_content的style，使正文能正常显示
    allscript = bs.findAll("script")
    for script in allscript:
        if "src" in script.attrs:  # 解决远程加载js失败导致打开网页很慢的问题
            script["src"] = ""
    return str(bs)  # 将BeautifulSoup对象再转换为字符串，用于保存




def ChangeCssSrc(bs):
    linkList = bs.findAll("link")
    for link in linkList:
        href = link.attrs["href"]
        if href.startswith("//"):
            newhref = "http:" + href
            link.attrs["href"] = newhref


def ChangeContent(bs):
    jscontent = bs.find(id="js_content")
    if jscontent:
        jscontent.attrs["style"] = ""
    else:
        print("-----可能文章被删了-----")



def DownArtList(json_data):
    try:
        idx = 0 
        for item in json_data:
            idx += 1
            url = item["url"]
            title = item["title"]
            biz = item["biz"]
            bizname = item["bizname"]
            pub_time = item["pub_time"]
            artname = f"{biz}_{pub_time}_{idx}"
            print("下载",title)
            
            
            
            # 先以title为文件名尝试保存，但有可能其中包含不能作为文件名的字符
            # 需要自行注意有的公众号会发title完全相同文章的情况
            savepath = os.path.join(SaveTxtDir, f"[{bizname}]{title}.html")
            try:
                # 尝试保存一个空文件，如果不报错就表示文件名可用
                SaveFile(savepath,"")
            except (OSError, IOError):
                # 如果保存失败，使用默认名称
                print("文件名无效，使用默认名称:", artname)
                savepath = os.path.join(SaveTxtDir, f"{artname}.html")
            
             
            arthtmlstr = DownLoadHtml(url)        
            arthtmlstr = ChangeImgSrc(arthtmlstr, saveImgDir, artname)
            SaveFile(savepath,arthtmlstr)
            if idx > 3: #超过3篇文章之后，则需要控制下载速度
                sleep(2) #防止下载过快被屏蔽
    except:
        print(traceback.format_exc())

