#恢复
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
        
#解压
def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:     
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)       
    else:
        print('This is not zip')

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
tmp_path = './Temp1'
tmp_path_n = tmp_path + '/'
tmdir(tmp_path)

print('Epic Games Store 游戏打包助手')
print('请选择你的备份，文件整理解包需要时间，大型游戏时间更长，我会提醒喝茶时间~~')

#获取备份包
info('提示','选择备份文件')
root = tk.Tk()      #调起对话框，选择恢复包
root.withdraw() 
FileName = filedialog.askopenfilename()     #获取选择的文件
root.destroy()

#解压备份包到临时文件夹
print('请开始喝茶~')
unzip_file(FileName, tmp_path_n)

#读取key文件，获取原始路径
full_path = './Temp1/key.txt'
with open(full_path, 'r') as file_object:       #打开key文件
    key_r = file_object.read()     #key文件读入内存
    key = key_r.replace("'","")
#print(key)

#获取游戏恢复路径
info('提示','选择游戏恢复的位置')
root = tk.Tk()      #调起对话框，选择文件夹
root.withdraw()     
Folderpath = filedialog.askdirectory()      #获取选择的文件夹
Folderpath_n = repr(Folderpath.replace('/', '\\'))       #对获得的路径字串转译保存到KEY函数
print('请开始喝茶~~')
root.destroy
#写出Manifest文件，用获取的文件路径替换key存储的路径

#获取ID值
def file_name(file_dir):   
    L=[]   
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == '.item':  # 想要读取的文件格式
                L.append(os.path.splitext(file)[0])  
    return L

Folderpath_manifest = tmp_path_n        #指向临时文件夹的manifest文件
L2 = file_name(Folderpath_manifest)     #获取游戏ID，分离扩展名
ID = L2[0]      #将List唯一值转到变量中

F1 = tmp_path_n
F2 = ID + '.item'
F3 = ID + '.bak'
Manifest_o = os.path.abspath(os.path.join(F1,F2))
Manifest_n = os.path.abspath(os.path.join(F1,F3))

# 打开旧文件
f = open(Manifest_o,'r',encoding='utf-8')
# 打开新文件
f_new = open(Manifest_n,'w',encoding='utf-8')
# 循环读取旧文件
for line in f:
   # 进行判断
   if key in line:
       Folderpath_rp = Folderpath_n.replace("'","")
       line = line.replace(key,Folderpath_rp)
   # 如果不符合就正常的将文件中的内容读取并且输出到新文件中
   f_new.write(line)
f.close()
f_new.close()

#删除旧文件
os.remove(Manifest_o)

#重命名新文件
manifest_l = os.path.splitext(Manifest_n)     #分离文件名与后缀，放在list中
if manifest_l[1] == '.bak':
        # 重新组合文件名和后缀名   
        manifest_r = manifest_l[0] + ".item"
        os.rename(Manifest_n,manifest_r)
#print(manifest_r)


#复制Manifest文件到清单文件夹
shutil.copy(Manifest_o, 'C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\')

#复制游戏目录到选定的目录
    
#获取游戏文件夹名称
GamePath = os.path.basename(FileName) 
GamePath = os.path.splitext(GamePath)[0]
GamePath2 = os.path.join(tmp_path_n,GamePath)
print(GamePath)
print(GamePath2)
#复制文件
Folderpath_u = os.path.join(Folderpath, GamePath)
shutil.copytree(GamePath2, Folderpath_u)

#删除文件
shutil.rmtree(tmp_path)

#弹出完成窗口
info('Epic Game Backup','恢复完成')      
