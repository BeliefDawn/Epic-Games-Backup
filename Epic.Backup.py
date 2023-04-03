# -*- coding:utf-8 -*-
import base64
import ctypes
import glob

import os
import shutil
import tempfile
import threading
import tkinter
import tkinter.messagebox
import zipfile
from asyncio.windows_events import NULL
from shutil import ExecError, copy2, copytree
from tkinter import *
from tkinter import END, filedialog, scrolledtext
from tkinter.ttk import *

import multiprocessing
from multiprocessing_win import *
from EIcon import *
from PFile import *

#版本代码
Eversion = "V1.14m"

#实现开始###########################################################################################
def on_closing():   #退出确认
    if tkinter.messagebox.askyesno('退出','确认退出，请确定没有执行中的流'):
        try:
            os.remove('tmp.ico')
        except OSError:
            pass
        root.destroy()
def GameItemList():     #获取游戏清单
    try:
        ItemList = glob.glob('C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\*.item')
        #获取游戏的名称与路径位置
        global GameList
        global GmaeItem_Path
        GameList = []
        GmaeItem_Path = []
        for id in ItemList:
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
            file.close()
        #构建已安装游戏字典
        global GameDict
        GameDict = dict(zip(GameList,GmaeItem_Path))
    except OSError:
        tkinter.messagebox.showinfo('提示','未能检索到清单，请确认epic中安装过游戏')
def file_name(file_dir, type):      #获取某类型文件名
    L=[]
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == type:
            #if os.path.splitext(file)[1] == '.manifest':  # 想要保存的文件格式
                L.append(os.path.splitext(file)[0])  
    return L
def PathCheck(FolderPath):      #判断路径指向类型
    if os.path.isdir(FolderPath):
        return('__directory')
    elif os.path.isfile(FolderPath):
        return('__file')
    else:
        return('__specialfile')   

def MakeBackup(FolderPath, self):      #备份程序包
    def make_zip(source_dir, output_filename):
        numC = 1
        all_file_num = FileNum(os.path.abspath(source_dir))
        AskDeflated = tkinter.messagebox.askyesno('提示','是否启用压缩？这将缩减备份包体积并大量占用CPU进行压缩，耗费时间更长')
        if AskDeflated == True:
            try:
                zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
                pre_len = len(os.path.dirname(source_dir))
                for parent, dirnames, filenames in os.walk(source_dir):
                    for filename in filenames:    
                        Pb['value'] = '{:.0f}'.format(numC/all_file_num*100)
                        Scrol.insert(END,'Packing: {:.0f}%'.format(numC/all_file_num*100) + ' /{0}'.format(os.path.basename(filename)) + '\n')
                        Scrol.see(END)
                        pathfile = os.path.join(parent, filename)
                        arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
                        zipf.write(pathfile, arcname)
                        numC += 1
                zipf.close()
                numC = 0
                all_file_num = 0
                Scrol.insert(END,'打包完成' + '\n')
                Scrol.see(END)
            except OSError:
                Mkzip = -1
        else:
            try:
                zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_STORED)
                pre_len = len(os.path.dirname(source_dir))
                for parent, dirnames, filenames in os.walk(source_dir):
                    for filename in filenames:    
                        Pb['value'] = '{:.0f}'.format(numC/all_file_num*100)
                        Scrol.insert(END,'Packing: {:.0f}%'.format(numC/all_file_num*100) + ' /{0}'.format(os.path.basename(filename)) + '\n')
                        Scrol.see(END)
                        pathfile = os.path.join(parent, filename)
                        arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
                        zipf.write(pathfile, arcname)
                        numC += 1
                zipf.close()
                numC = 0
                all_file_num = 0
                Scrol.insert(END,'打包完成' + '\n')
                Scrol.see(END)
            except OSError:
                Mkzip = -1
    def add_files_into_package(source_dir, output_zip):
        try:
            zipf = zipfile.ZipFile(output_zip, "a")
            pre_len = len(os.path.dirname(source_dir))
            for parent, dirnames, filenames in os.walk(source_dir):
                for filename in filenames:
                    pathfile = os.path.join(parent, filename)
                    arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
                    zipf.write(pathfile, arcname)
            zipf.close()
        except OSError:
            tkinter.messagebox.showinfo('提示','未能正确检索到备份包，无法将配置文件插入')
    def add_file_into_package(file, output_zip):
        try:
            zipf = zipfile.ZipFile(output_zip, "a")
            #zinfo = zipfile.ZipInfo(file)
            #zinfo.compress_type = zipf.compression
            fn = os.path.basename(file)
            #f = open(file, "r", encoding='utf-8')
            f = open(file, "rb")        #修改为二进制读写，避免utf8读取后二进制写入的编码改变
            zipf.writestr(fn, f.read())
            #zipf.writestr(zinfo, f.read())     #保留原始的文件树结构
            f.close()
            zipf.close()
        except OSError:
            tkinter.messagebox.showinfo('提示','未能正确检索到备份包，无法将配置文件插入')
    def MakeBackup_o(Folderpath, self):
        #实现-制作key文件
        def text_creat(content):
            full_path = os.path.join(tmp_path, 'key.txt')   #创建key文件
            content = os.path.abspath(os.path.join(content,os.pardir))
            content = eval(repr(content).replace('\\', '\\\\'))
            with open(full_path, 'w') as file_object:       #打开key文件
                file_object.write(content)     #key文件写入内容
        #执行流
        #处理临时文件夹
        TMPDIR = tempfile.TemporaryDirectory()
        tmp_path = TMPDIR.name
        #写出KEY
        text_creat(Folderpath)     #调用函数创建key文件
        Folderpath_manifest = os.path.join(Folderpath,'.egstore/')      #为路径添加，进入配置文件夹
        L2 = file_name(Folderpath_manifest, '.manifest')     #获取游戏ID，分离扩展名
        ID = L2[0]      #将List唯一值转到变量中
        #提取Manifest清单文件#
        #拼合文件路径
        F1 = 'C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\'
        F2 = ID + '.item'   #拼合文件名
        Folderpath_cdr =  os.path.abspath(os.path.join(F1,F2))      #拼合文件路径
        #复制清单文件
        shutil.copy(Folderpath_cdr, tmp_path)
        #打包游戏文件
        GamePath = os.path.basename(Folderpath)     #获取游戏文件夹名称
        MKzipName = GamePath + '.zip'   #设计备份文件名称
        FIle_F2 = tmp_path + '/' + F2
        FIle_key = tmp_path +'/key.txt'
        global Mkzip
        Mkzip = 0
        make_zip(Folderpath, MKzipName)   #通过路径直接打包游戏本体
        ##加入配置文件
        if Mkzip == 0:
            add_file_into_package(FIle_F2, MKzipName)     #通过临时文件夹向压缩包插入配置文件
            add_file_into_package(FIle_key, MKzipName)     #通过临时文件夹向压缩包插入key文件
        else:
            tkinter.messagebox.showinfo('提示','不能创建备份包，关闭占有包的软件')
        TMPDIR.cleanup()
        Scrol.insert(END,'临时文件删除完成' + '\n')
        Scrol.see(END)
        #提示
        if Mkzip == 0:
            tkinter.messagebox.showinfo('提示', '备份包 ' + Folderpath + '.zip')
            sWin.destroy()
        else:
            pass
    if PathCheck(FolderPath)=='__directory':
        def ThreadMkzip(FolderPath): #启用子线程
            self = 0
            SourseWithDistpath = (FolderPath, self)
            Thread_MKzip = threading.Thread(target = MakeBackup_o, args = SourseWithDistpath)
            Thread_MKzip.start()
        sWin = Tk()
        sWin.title('备份：'+os.path.basename(FolderPath)+'...')
        sWin.iconbitmap('tmp.ico')
        sframe = Frame(sWin)
        sframe.pack()
        Pb = Progressbar(sframe, mode='determinate', value=0)
        Pb.pack(fill=X)
        Scrol = scrolledtext.ScrolledText(sframe,font=('微软雅黑',10))
        Scrol.pack(fill=BOTH)
        Scrol.insert(END,'运行情况将在这里输出\n')
        ThreadMkzip(FolderPath)
        sWin.mainloop()
    else:
        tkinter.messagebox.showerror('错误', '无路径被选择')
def UnPackBackup(BackupPackPath, Folderpath):       #恢复程序包
    def unzip_file(zip_src, dst_dir):
        numC = 0
        all_file_num = 0
        r = zipfile.is_zipfile(zip_src)
        if r:
            fz = zipfile.ZipFile(zip_src, 'r')
            all_file_num = len(fz.namelist())
            for file in fz.namelist():
                numC += 1
                fz.extract(file, dst_dir)
                Pb['value'] = '{:.0f}'.format(numC/all_file_num*100)
                Scrol.insert(END,'Unpacking: {:.0f}%'.format(numC/all_file_num*100) +' /{0}'.format(os.path.basename(file)) + '\n')
                Scrol.see(END)
            fz.close()
        else:
            print('This is not zip')
        numC = 0
        all_file_num = 0
        Scrol.insert(END,'解压完成' + '\n')
        Scrol.see(END)
    def unzip_file_extension(zip_src, dst_dir, fmode):
        r = zipfile.is_zipfile(zip_src)
        if r:
            fz = zipfile.ZipFile(zip_src, 'r')
            if fmode == 0:     #只解压配置文件到临时文件夹
                for file in fz.namelist():
                    if file.endswith(".txt"):
                        Scrol.insert(END,'Unpacking: ' + ' /{0}'.format(os.path.basename(file)) + '\n')
                        Scrol.see(END)
                        fz.extract(file, dst_dir)
                    elif file.endswith(".item"):
                        Scrol.insert(END,'Unpacking: ' + ' /{0}'.format(os.path.basename(file)) + '\n')
                        Scrol.see(END)
                        fz.extract(file, dst_dir)
                    else:
                        pass
            elif fmode == 1:    #除了配置文件外解压到游戏目录
                numC = 0
                all_file_num = 0
                for file in fz.namelist():
                    all_file_num = len(fz.namelist())
                    if file.endswith(".txt"):
                        pass
                    elif file.endswith(".item"):
                        pass
                    else:
                        numC += 1
                        Scrol.insert(END,'Unpacking: ' + ' /{0}'.format(os.path.basename(file)) + '\n')
                        Scrol.see(END)
                        Pb['value'] = '{:.0f}'.format(numC/all_file_num*100)
                        fz.extract(file, dst_dir)
                numC = 0
                all_file_num = 0
                Scrol.insert(END,'解压完成' + '\n')
                Scrol.see(END)
            #for file in fz.namelist():
            #    if not os.path.isfile(os.path.join(zip_src, file)):
            #        continue
            #    if file.split('.')[-1] == extension1:
            #        print(extension1)
            #        print(file.split('.')[-1])
            #        Scrol.insert(END,'Unpacking: ' + ' /{0}'.format(os.path.basename(file)) + '\n')
            #        Scrol.see(END)
            #        fz.extract(file, dst_dir)

        else:
            print('This is not zip')
    def UnpackBackup_o(BackupPackPath, Folderpath):         
        #执行流
        #处理临时文件夹
        TMPDIR = tempfile.TemporaryDirectory()
        tmp_path = TMPDIR.name
        #解压配置文件到临时文件夹
        unzip_file_extension(BackupPackPath, tmp_path, 0)
        #读取key文件，获取原始路径
        full_path = tmp_path +'/key.txt'
        with open(full_path, 'r') as file_object:       #打开key文件
            key_r = file_object.read()     #key文件读入内存
            key = key_r.replace("'","")
        #获取游戏恢复路径
        Folderpath_n = repr(Folderpath.replace('/', '\\'))       #对获得的路径字串转译保存到KEY函数
        #写出Manifest文件，用获取的文件路径替换key存储的路径
        #获取ID值
        Folderpath_manifest = tmp_path        #指向临时文件夹的manifest文件
        L2 = file_name(Folderpath_manifest, '.item')     #获取游戏ID，分离扩展名
        ID = L2[0]      #将List唯一值转到变量中
        F1 = tmp_path
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
        Scrol.insert(END,'配置文件释放成功' + '\n')
        #复制游戏目录到选定的目录
            #获取游戏文件夹名称
        GamePath = os.path.basename(BackupPackPath) 
        GamePath = os.path.splitext(GamePath)[0]
            #解压游戏文件
        unzip_file_extension(BackupPackPath, Folderpath, 1)   #解压文件到游戏目录
            #删除文件
        TMPDIR.cleanup()
        Scrol.insert(END,'删除临时文件，完成' + '\n')
        Scrol.see(END)
            #弹出完成窗口
        tkinter.messagebox.showinfo('提示','恢复完成')
        GameItemList()
        sWin.destroy()

    def ThreadUNzip(BackupPackPath, Folderpath):
        SourseWithDistpath = (BackupPackPath, Folderpath)
        Thread_UNzip = threading.Thread(target= UnpackBackup_o, args= SourseWithDistpath)
        Thread_UNzip.start()
    sWin = Tk()
    sWin.title('恢复：'+os.path.basename(BackupPackPath)+'...')
    sWin.iconbitmap('tmp.ico')
    sframe = Frame(sWin)
    sframe.pack()
    Pb = Progressbar(sframe, mode='determinate', value=0)
    Pb.pack(fill=X)
    Scrol = scrolledtext.ScrolledText(sframe,font=('微软雅黑',10))
    Scrol.pack(fill=BOTH)
    Scrol.insert(END,'运行情况将在这里输出\n')
    sWin.update()
    ThreadUNzip(BackupPackPath, Folderpath)
    sWin.mainloop()     
def moveFiles(PathOld, PathNew):        #迁移执行包
    def streamIo(src, dst):       #文件复制流
        def copy2_verbose(src, dst):
            global numC
            global file_names
            global all_file_num
            numC = 1+ numC
            Pb['value'] = '{:.0f}'.format(numC/all_file_num*100)
            Scrol.insert(END,'Copying: {:.0f}%'.format(numC/all_file_num*100) + ' /{0}'.format(os.path.basename(src)) + '\n')
            Scrol.see(END)
            copy2(src,dst)
        def cptree(src, dst):
            global numC
            numC = 0
            global all_file_num
            all_file_num = FileNum(src)
            copytree(src, dst, copy_function=copy2_verbose)
            numC = 0
            all_file_num = 0
            Scrol.insert(END,'复制完成' + '\n')
            Scrol.see(END)
        cptree(src, dst)
    def moveFIles_o(PathOld,PathNew):
        PathOld_v = PathOld
        PathNew_v = PathNew
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
        L2 = file_name(GameFile_manifest, '.manifest')     #获取游戏ID，分离扩展名
        if PathCheck(GameFile_manifest) == '__directory':
            ID = L2[0]
                #拼合文件路径
            F1 = 'C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\'
            F2 = ID + '.item'   #拼合文件名
            F3 = ID + '.bak'
            #PathNew_w = os.path.join(PathNew_w,GameName)
            PathOld_w = repr(PathOld_w.replace("/","\\"))
            PathNew_w = repr(PathNew_w.replace("/","\\"))
            #Fuck Epic '\\' and '/' with a lot of unbeliable arts.
            PathOld_w = PathOld_w.replace("\\\\"+GameName,"")
            PathOld_w = PathOld_w +'/'+ GameName
            PathNew_w = PathNew_w +'/'+ GameName
            #fuck over
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
            streamIo(PathOld_s, OrderPath)
            shutil.rmtree(PathOld_s)
            #删除旧文件
            os.remove(Folderpath_Itme_o)
            Scrol.insert(END,'删除旧文件完成' + '\n')
            #重命名新文件
            manifest_l = os.path.splitext(Folderpath_Itme_n)     #分离文件名与后缀，放在list中
            if manifest_l[1] == '.bak':
                # 重新组合文件名和后缀名
                manifest_r = manifest_l[0] + ".item"
                os.rename(Folderpath_Itme_n,manifest_r)
                Scrol.insert(END,'配置文件修改完成，重启epic加载' + '\n')
            GameItemList()
            tkinter.messagebox.showinfo('提示','迁移完成')
            sWin.destroy()
        else:
            tkinter.messagebox.showinfo('提示','未能检索到游戏文件')
    def ThreadMOve():
        SourseWithDistpath = (PathOld, PathNew)
        Thread_MOve = threading.Thread(target= moveFIles_o, args= SourseWithDistpath)
        Thread_MOve.start()

    sWin = Tk()
    sWin.title('迁移：'+'...')
    sWin.iconbitmap('tmp.ico')
    sframe = Frame(sWin)
    sframe.pack()
    Pb = Progressbar(sframe, mode='determinate', value=0)
    Pb.pack(fill=X)
    Scrol = scrolledtext.ScrolledText(sframe,font=('微软雅黑',10))
    Scrol.pack(fill=BOTH)
    Scrol.insert(END,'运行情况将在这里输出\n')
    ThreadMOve()
    sWin.mainloop() 


#实现结束###########################################################################################

if __name__ == "__main__":
    multiprocessing.freeze_support()
    #GUi界面实现
    GameItemList()
    root = Tk()
    with open('tmp.ico','wb') as tmp:
        tmp.write(base64.b64decode(Icon().img))
        root.iconbitmap('tmp.ico')
    #高DPI适配
    #调用api设置成由应用程序缩放
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    #调用api获得当前的缩放因子
    ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
    #设置缩放因子
    root.tk.call('tk', 'scaling', ScaleFactor/65)
    ##
    root.title('Epic 游戏管理 '+ Eversion +  ' @BLIEFDAWN of Github')
    root.geometry('800x460')
    #800x610
    root.resizable(width=0, height=0)
    ##
    frame_top = Frame(root)
    frame_top.pack()
    ##
    frame_1 = LabelFrame(frame_top, text = "选择备份的游戏")
    frame_1.pack(padx=10, pady=10, ipadx=10, ipady=5)
    def MKz_click_item(event):
        DialogResult = tkinter.messagebox.askyesno('提示' , '备份游戏 ' + BackCb.get() + ' 吗?')
        if DialogResult == True:
            WnnaBackupGame = StringVar()
            WnnaBackupGame.set('')
            r = GameDict[BackCb.get()]
            r2 = (r, 0)
            p = multiprocessing.Process(target=MakeBackup, args=(r2))
            p.start()
    SelectBackupGame = StringVar()
    BackCb = Combobox(frame_1, state='readonly', width = 80)
    BackCb['values'] = GameList
    BackCb.bind('<<ComboboxSelected>>', MKz_click_item)
    BackCb.pack(pady=5)
    ##
    frame_2 = LabelFrame(frame_top, text= '选择恢复的备份包')
    frame_2.pack(padx=10, pady=10, ipadx=10, ipady=5)
    def EntryPath():
        #UnPackBackup(filedialog.askopenfilename(title = '选择备份包', filetypes=[('备份压缩包', '.zip')]))
        
        r = filedialog.askopenfilename(title = '选择备份包', filetypes=[('备份压缩包', '.zip')])
        if zipfile.is_zipfile(r):
            DialogResult = tkinter.messagebox.askyesno('提示','选择恢复路径')
            if DialogResult == True:
                Folderpath = filedialog.askdirectory(title = '选择恢复路径')
                if Folderpath:
                    r2 = (r, Folderpath)
                    p = multiprocessing.Process(target=UnPackBackup, args=(r2))
                    p.start()
        else:
            tkinter.messagebox.showerror('错误', '无备份包被选择')
    Ubp_btn = Button(frame_2, text="路径", command = EntryPath, width=82)
    Ubp_btn.pack(pady=5)
    ##
    frame_3 = LabelFrame(frame_top, text = '选择需要迁移的游戏')
    frame_3.pack(padx=10, pady=10, ipadx=10, ipady=5)
    PathOld = StringVar()
    PathNew = StringVar()
    def GetCB(self):        #第一个输入框修改
        PathOld = StringVar()
        PathOld.set('')             
        Path_o.delete(0, END)       #清空原始Entry字符
        Path_o.insert(0,GameDict[Cb.get()])
        PathOld = GameDict[Cb.get()]
    def LocateOrder():      #第二个输入框修改
        PathNew = filedialog.askdirectory(title = '选择迁移')
        Path_n.select_clear()
        Path_n.delete(0, END)       #清空迁移Entry字符
        Path_n.insert(0,PathNew)
    Cb = Combobox(frame_3, state='readonly', width = 80)
    Cb['values'] = GameList
    Cb.bind('<<ComboboxSelected>>', GetCB)
    Cb.pack(pady=5)
    ##
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
    def Mov_click_item():
        SureMove = tkinter.messagebox.askyesno('提示','从\n' + PathOld.get() + '\n迁移文件到\n' + PathNew.get() + '\n吗？')
        if SureMove == True:
            r = (PathOld.get(), PathNew.get())
            p = multiprocessing.Process(target=moveFiles, args=(r))
            p.start()
    Btn_Locate = Button(frame_3, text="迁移", command = Mov_click_item, width=45)
    Btn_Locate.pack()
    '''
    frame_4 = Frame(frame_top)
    frame_4.pack(padx=1, pady=1)
    Pb = Progressbar(frame_4, mode='determinate', value=0, length=800)
    Pb.pack()
    Scrol = scrolledtext.ScrolledText(frame_4 ,width = 78, height=12, font=('微软雅黑',10))
    Scrol.pack()
    Scrol.insert(END,'运行情况将在这里输出\n')
    '''
    def task_kill(exe):
        os.system('taskkill /f /t /im '+ exe)
    def task_start(exe):
        os.system(exe)
    def EPrebot():
        task_kill('EpicGamesLauncher.exe')
        task_start('"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"')
        GameItemList()
        root.update()
    frame_4 = Frame(frame_top)
    frame_4.pack(padx=1, pady=1)
    Btn_rebot = Button(frame_4, text= "重启 EPIC GAMES STORE 并刷新数据", width = 85, command = EPrebot)
    Btn_rebot.pack()
    ##
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
