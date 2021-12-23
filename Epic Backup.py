import glob
from tkinter import *
import tkinter
import tkinter.ttk
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import os
import shutil
import zipfile
from tkinter import filedialog


#实现开始###########################################################################################

#弹窗通知
def info(stringtitle,stringinfo):
    # 弹出对话框
    info = tkinter.Tk()      #调起对话框
    info.withdraw() 
    result = tkinter.messagebox.showinfo(title = stringtitle, message = stringinfo)
    # 返回值为：ok
#实现-获取文件名
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

#实现-文件解压
def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:     
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)       
    else:
        print('This is not zip')

#初始化临时文件夹
def tmdir(tmp_path):
    folder = os.path.exists(tmp_path)
    if not folder:
        os.makedirs(tmp_path)
    else:
        shutil.rmtree(tmp_path)
        os.makedirs(tmp_path) 
#判断路径指向类型
def PathCheck(FolderPath): 
    if os.path.isdir(FolderPath):
        return('__directory')
    elif os.path.isfile(FolderPath):
        return('__file')
    else:
        return('__specialfile')   

#备份程序包
def MakeBackup(FolderPath): #判断是否空路径
    if PathCheck(FolderPath)=='__directory':
        MakeBackup_o(FolderPath)
    else:
        tkinter.messagebox.showerror('错误', '无路径被选择')
    #print it's a special file(socket,FIFO,device file)    
def MakeBackup_o(Folderpath):
    #实现-制作key文件
    def text_creat(name,content):
        key_path = tmp_path_n  #创建key文件的存放路径
        full_path = key_path + name + '.txt'    #创建key文件

        with open(full_path, 'w') as file_object:       #打开key文件
            file_object.write(content)      #key文件写入内容

    #执行流
    
    #处理临时文件夹
    tmp_path = './Temp0'
    tmp_path_n = tmp_path + '/'
    tmdir(tmp_path)

    #写出KEY
    text_creat('key', Folderpath)     #调用函数创建key文件

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
    #删除文件
    shutil.rmtree(tmp_path)
    #提示
    info('提示', '备份成功！备份包在 /程序目录//' + GamePath + '.zip')

#恢复程序包

def UnPackBackup(BackupPackPath): #判断是否备份包
    if zipfile.is_zipfile(BackupPackPath):
        UnpackBackup_o(BackupPackPath)
    else:
        tkinter.messagebox.showerror('错误', '无备份包被选择')   
def UnpackBackup_o(BackupPackPath):         
    #执行流
    #处理临时文件夹
    tmp_path = './Temp1'
    tmp_path_n = tmp_path + '/'
    tmdir(tmp_path)

    #解压备份包到临时文件夹

    unzip_file(BackupPackPath, tmp_path_n)

    #读取key文件，获取原始路径
    full_path = './Temp1/key.txt'
    with open(full_path, 'r') as file_object:       #打开key文件
        key_r = file_object.read()     #key文件读入内存
        key = key_r.replace("'","")
    #print(key)

    #获取游戏恢复路径
    info('提示','选择游戏恢复的位置')
    alert = tkinter.Tk()      #调起对话框，选择文件夹
    alert.withdraw()     
    Folderpath = filedialog.askdirectory(title = '选择恢复路径')      #获取选择的文件夹
    Folderpath_n = repr(Folderpath.replace('/', '\\'))       #对获得的路径字串转译保存到KEY函数

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

    #复制Manifest文件到清单文件夹
    shutil.copy(Manifest_o, 'C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\')

    #复制游戏目录到选定的目录
        #获取游戏文件夹名称
    GamePath = os.path.basename(BackupPackPath) 
    GamePath = os.path.splitext(GamePath)[0]
    GamePath2 = os.path.join(tmp_path_n,GamePath)
        #复制文件
    Folderpath_u = os.path.join(Folderpath, GamePath)
    shutil.copytree(GamePath2, Folderpath_u)
        #删除文件
    shutil.rmtree(tmp_path)
        #弹出完成窗口
    GameItemList()
    info('Epic Game Backup','恢复完成')      

#迁移执行包
def moveFiles():        
    def file_name(file_dir):
        L=[]
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if os.path.splitext(file)[1] == '.manifest':  # 想要保存的文件格式
                    L.append(os.path.splitext(file)[0])  
        return L 
    SureMove = tkinter.messagebox.askyesno('提示','从\n' + PathOld.get() + '\n迁移文件到\n' + PathNew.get() + '\n吗？')
    if SureMove == True:
        PathOld_v = PathOld.get()
        PathNew_v = PathNew.get()

        PathOld_w = str(PathOld_v)
        PathNew_w = str(PathNew_v)
        PathOld_s = PathOld_w
        PathNew_s = PathNew_w

            #迁移文件
        GameName = os.path.basename(PathOld_v)
        GameName = os.path.splitext(GameName)[0]
        OrderPath = os.path.join(PathNew_s,GameName)
            #修改Manifest清单文件\
        GameFile_manifest = os.path.join(PathOld_s,'.egstore')     #为路径添加，进入配置文件夹
        L2 = file_name(GameFile_manifest)     #获取游戏ID，分离扩展名
        if PathCheck(GameFile_manifest) == '__directory':  
            ID = L2[0]
                #拼合文件路径
            F1 = 'C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\'
            F2 = ID + '.item'   #拼合文件名
            F3 = ID + '.bak'
            
            PathNew_w = os.path.join(PathNew_w,GameName)
            PathOld_w = repr(PathOld_w.replace("/","\\"))
            PathNew_w = repr(PathNew_w.replace("/","\\"))
            PathOld_w = PathOld_w.replace("'",'')
            PathNew_w = PathNew_w.replace("'",'')
                #拼合文件路径
            Folderpath_Itme_o = os.path.abspath(os.path.join(F1,F2))
            Folderpath_Itme_n = os.path.abspath(os.path.join(F1,F3))
            
            f = open(Folderpath_Itme_o,'r',encoding='utf-8')
            f_new = open(Folderpath_Itme_n,'w',encoding='utf-8')
            for line in f:
                #进行判断
                if PathOld_w in line:
                    line = line.replace(PathOld_w, PathNew_w)
                f_new.write(line)
            f.close()
            f_new.close()
                        
            shutil.copytree(PathOld_s, OrderPath)
            shutil.rmtree(PathOld_s)

            #删除旧文件
            os.remove(Folderpath_Itme_o)

            #重命名新文件
            manifest_l = os.path.splitext(Folderpath_Itme_n)     #分离文件名与后缀，放在list中
            if manifest_l[1] == '.bak':
                # 重新组合文件名和后缀名   
                manifest_r = manifest_l[0] + ".item"
                os.rename(Folderpath_Itme_n,manifest_r)

            GameItemList()
            info('提示','迁移完成')
        else:
            info('提示','未能检索到游戏文件')

#实现结束###########################################################################################



#获取游戏清单
def GameItemList():
    ItemList = glob.glob('C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\*.item')
    GameNum = len(ItemList)
    #获取游戏的名称与路径位置
    global GameList
    global GmaeItem_Path
    GameList = []
    GmaeItem_Path = []
    for id in ItemList:
        #print(id)
        file = open(id, 'r',encoding='utf-8')
        for line in file:
            # 判断游戏名
            if 'DisplayName' in line:
                line = line.replace(',','')
                line = line.replace('"DisplayName": ', '')
                line = line.replace('"','')
                line = "/t".join(line.split())
                line = "/n".join(line.split())
                line = line.replace('/t', ' ')
                GameList.append(line)
                #print(line)
            #判断游戏安装路径
            if 'InstallLocation' in line:
                line = line.replace(',','')
                line = line.replace('"InstallLocation": ', '')
                line = line.replace('"','')
                line = "/t".join(line.split())
                line = "/n".join(line.split())
                line = line.replace('\\\\','\\')
                line = line.replace('/t', ' ')
                GmaeItem_Path.append(line)
                #print(line)
    #构建已安装游戏字典
    global GameDict
    GameDict = dict(zip(GameList,GmaeItem_Path))

#初始化游戏列表
GameItemList()

#GUi界面实现
root = Tk()
root.title('Epic 游戏管理')
root.geometry('800x390')
frame_top = Frame(root)
frame_top.pack()
frame_1 = LabelFrame(frame_top, text = "选择备份的游戏")
frame_1.pack(padx=10, pady=10, ipadx=10, ipady=5)
def click_item(event):
    DialogResult = tkinter.messagebox.askyesno('提示' , '备份游戏 ' + BackCb.get() + ' 吗?')
    if DialogResult == True:
        WnnaBackupGame = StringVar()
        WnnaBackupGame.set('')
        r = GameDict[BackCb.get()]
        MakeBackup(r)
SelectBackupGame = StringVar()
BackCb = Combobox(frame_1, state='readonly', width = 80, height=50)
BackCb['values'] = GameList
BackCb.bind('<<ComboboxSelected>>', click_item)
BackCb.pack(pady=5)

frame_2 = LabelFrame(frame_top, text= '选择恢复的备份包')
frame_2.pack(padx=10, pady=10, ipadx=10, ipady=5)
def EntryPath():
    UnPackBackup(filedialog.askopenfilename(title = '选择备份包', filetypes=[('备份压缩包', '.zip')]))
Ubp_btn = Button(frame_2, text="路径", command = EntryPath, width=82)
Ubp_btn.pack(pady=5)
frame_3 = LabelFrame(frame_top, text = '选择需要迁移的游戏')
frame_3.pack(padx=10, pady=10, ipadx=10, ipady=5)

PathOld = StringVar()
PathNew = StringVar()

def GetCB(self):        #第一个输入框修改
    PathOld = StringVar()
    PathOld.set('')
    Path_o.insert(0,GameDict[Cb.get()])
    PathOld = GameDict[Cb.get()]
def LocateOrder():      #第二个输入框修改
    PathNew = filedialog.askdirectory(title = '选择迁移')
    Path_n.select_clear()
    Path_n.insert(0,PathNew)

Cb = Combobox(frame_3, state='readonly', width = 80)
Cb['values'] = GameList
Cb.bind('<<ComboboxSelected>>', GetCB)
Cb.pack(pady=5)

frame_3_entry = Frame(frame_3)
frame_3_entry.pack(padx= 0, pady=5,ipadx=0,ipady=0)

label_o = Button(frame_3_entry, text='原始路径',width=8)
label_o.grid(row=0,column=0)

Path_o = Entry(frame_3_entry, justify=LEFT, textvariable=PathOld, exportselection=0, width=73)
Path_o.grid(row=0,column=1,pady=5)
label_n = Button(frame_3_entry, text='目标路径', width=8, command=LocateOrder)
label_n.grid(row=1,column=0)

Path_n =  Entry(frame_3_entry, justify=LEFT, textvariable=PathNew, exportselection=0, width=73)
#Path_n.bind('<Double-Button-1>', LocateOrder)
Path_n.grid(row=1,column=1,pady=5)

Btn_Locate = Button(frame_3, text="迁移", command = moveFiles, width=45)
Btn_Locate.pack()
root.mainloop()