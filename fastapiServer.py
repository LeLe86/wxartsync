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



SaveJsonDir = "c:\\artlist\\json"

if not os.path.exists(SaveJsonDir):
    os.makedirs(SaveJsonDir)


def SaveFile(fpath,fileContent):    
    with open(fpath,'w',encoding='UTF-8') as f:
        f.write(fileContent)

# 获取当前时间字符串，精确到毫秒
def get_current_time_string():
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(tz) 
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
        
        
        return  "success"  
    except:
        print(traceback.format_exc())
    return "error"
    
    
    
    
    
    
    
    
    