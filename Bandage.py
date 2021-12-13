#备份
import os
import shutil
import zipfile
import tkinter as tk
import tkinter.messagebox
from pathlib import Path
from tkinter import filedialog

#实现开始###########################################################################################

#临时文件夹
def tmdir(tmp_path):
    folder = os.path.exists(tmp_path)
    if not folder:
        os.makedirs(tmp_path)
    else:
        shutil.rmtree(tmp_path)
        os.makedirs(tmp_path)
        

#实现-制作key文件
def text_creat(name,content):
    key_path = tmp_path_n  #创建key文件的存放路径
    full_path = key_path + name + '.txt'    #创建key文件

    with open(full_path, 'w') as file_object:       #打开key文件
        file_object.write(content)      #key文件写入内容  

#实现-获取ID值
def file_name(file_dir):   
    L=[]   
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == '.manifest':  # 想要保存的文件格式
                L.append(os.path.splitext(file)[0])  
    return L 

#实现-打包文件
def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
            zipf.write(pathfile, arcname)
    zipf.close()

#弹窗通知
def info(stringtitle,stringinfo):
    # 弹出对话框
    root = tk.Tk()      #调起对话框，选择恢复包
    root.withdraw() 
    result = tk.messagebox.showinfo(title = stringtitle, message = stringinfo)
    root.destroy
    # 返回值为：ok
    print(result)


#实现结束###########################################################################################




#工作流#############################################################################################

#处理临时文件夹
tmp_path = './Temp0'
tmp_path_n = tmp_path + '/'
tmdir(tmp_path)

print('Epic Games Store 游戏打包助手')
print('请选择你的游戏路径，如“D:\GTAV”，则选中文件夹“GTA V”，文件整理打包需要时间，大型游戏时间更长，我会提醒喝茶时间~~')
print('第一步，共三步：key写出')
#获取游戏路径
root = tk.Tk()      #调起对话框，选择文件夹
root.withdraw()     

Folderpath = filedialog.askdirectory()      #获取选择的文件夹
Folderpath_r = os.path.abspath(os.path.join(Folderpath,os.pardir))      #获取选择的父文件夹，游戏在此父文件夹下
Folderpath_n = repr(Folderpath.replace('/', '\\'))       #对获得的路径字串转译保存到KEY函数
Folderpath_r = repr(Folderpath_r.replace('/', '\\'))        #对获得的路径转译
print('路径获得，现在开始喝杯茶等等吧~~~')
print(Folderpath_r)
print(Folderpath_n)
root.destroy

#写出KEY
text_creat('key', Folderpath_r)     #调用函数创建key文件

print('第二步，共三步：整理文件中')

Folderpath_manifest = os.path.join(Folderpath,'.egstore/')      #为路径添加，进入配置文件夹
L2 = file_name(Folderpath_manifest)     #获取游戏ID，分离扩展名
ID = L2[0]      #将List唯一值转到变量中

#提取Manifest清单文件#
#拼合文件路径
F1 = 'C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\'
F2 = ID + '.item'   #拼合文件名
Folderpath_cdr =  os.path.abspath(os.path.join(F1,F2))      #拼合文件路径

#复制清单文件
shutil.copy(Folderpath_cdr, tmp_path_n)

#复制游戏文件
GamePath = os.path.basename(Folderpath)     #获取游戏文件夹名称
GameBackup = os.path.join(tmp_path_n,GamePath)
shutil.copytree(Folderpath, GameBackup)

#打包游戏文件
make_zip(tmp_path_n, GamePath+'.zip')

print('第三步，共三步：打包文件已完成')

#删除文件
shutil.rmtree(tmp_path)

info('Epic Game Backup' , GamePath + ' 备份完成！')      #弹出完成窗口
btn1 = tk.Button(root,text = '确定',command = info)
btn1.pack()
