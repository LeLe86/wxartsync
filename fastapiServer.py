'''

先安装必须的包
pip install fastapi uvicorn aiohttp requests bs4

运行，记得要把你云主机的29212端口打开
python -m uvicorn fastapiServer:app --host 0.0.0.0 --port 29212 --reload

你的对外地址，即系统中需要填的[推送地址]
http://公网ip:29212/artlist/


'''
import os
from fastapi import FastAPI, Request, HTTPException
from pprint import pprint
import json,requests
import traceback
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
from WxartDownloader import DownArtList,SaveFile,get_current_time_string


SaveJsonDir = "c:\\artlist\\json"

if not os.path.exists(SaveJsonDir):
    os.makedirs(SaveJsonDir)
    
# 是否下载文章
downArtFlag = True

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
        
        if downArtFlag:
            DownArtList(json_data)
        
        return  "success"  
    except:
        print(traceback.format_exc())
    return "error"
    
    
    
    
    
    
    
    
    