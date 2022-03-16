import os
import sys
import math
import time

global totalSize
global fileNum
global dirNum
totalSize = 0
fileNum = 0
dirNum = 0

 
def visitDir(path):                                 # 统计文件、文件夹数量，文件夹大小
    global totalSize
    global fileNum
    global dirNum
    for lists in os.listdir(path):
        sub_path = os.path.join(path, lists)
        #print(sub_path)
        if os.path.isfile(sub_path):
            fileNum = fileNum+1                     # 统计文件数量
            totalSize = totalSize+os.path.getsize(sub_path)  # 文件总大小
        elif os.path.isdir(sub_path):
            dirNum = dirNum+1                       # 统计文件夹数量
            visitDir(sub_path)                      # 递归遍历子文件夹
 
def sizeConvert(size):                              # 单位换算
    K, M, G = 1024, 1024**2, 1024**3
    if size >= G:
        return str(size/G)+'G Bytes'
    elif size >= M:
        return str(size/M)+'M Bytes'
    elif size >= K:
        return str(size/K)+'K Bytes'
    else:
        return str(size)+'Bytes'

def copy_large_file(src, dst):                      # 大文件复制进度
    '''
    Copy a large file showing progress.
    '''
    print('copying "{}" --> "{}"'.format(src, dst))
    if os.path.exists(src) is False:
        print('ERROR: file does not exist: "{}"'.format(src))
        sys.exit(1)
    if os.path.exists(dst) is True:
        os.remove(dst)
    if os.path.exists(dst) is True:
        print('ERROR: file exists, cannot overwrite it: "{}"'.format(dst))
        sys.exit(1)

    # Start the timer and get the size.
    start = time.time()
    size = os.stat(src).st_size
    print('{} bytes'.format(size))

    # Adjust the chunk size to the input size.
    divisor = 10000  # .1%
    #chunk_size = size / divisor
    chunk_size = math.ceil( size / divisor )  # suggested by 0xmessi to fix an error.
    while chunk_size == 0 and divisor > 0:
        divisor /= 10
        chunk_size = size / divisor
    print('chunk size is {}'.format(chunk_size))

    # Copy.
    try:
        with open(src, 'rb') as ifp:
            with open(dst, 'wb') as ofp:
                copied = 0  # bytes
                chunk = ifp.read(chunk_size)
                while chunk:
                    # Write and calculate how much has been written so far.
                    ofp.write(chunk)
                    copied += len(chunk)
                    per = 100. * float(copied) / float(size)

                    # Calculate the estimated time remaining.
                    elapsed = time.time() - start  # elapsed so far
                    avg_time_per_byte = elapsed / float(copied)
                    remaining = size - copied
                    est = remaining * avg_time_per_byte
                    est1 = size * avg_time_per_byte
                    eststr = 'rem={:>.1f}s, tot={:>.1f}s'.format(est, est1)

                    # Write out the status.
                    sys.stdout.write('\r\033[K{:>6.1f}%  {}  {} --> {} '.format(per, eststr, src, dst))
                    sys.stdout.flush()

                    # Read in the next chunk.
                    chunk = ifp.read(chunk_size)

    except IOError as obj:
        print('\nERROR: {}'.format(obj))
        sys.exit(1)

    sys.stdout.write('\r\033[K')  # clear to EOL
    elapsed = time.time() - start
    print('copied "{}" --> "{}" in {:>.1f}s"'.format(src, dst, elapsed))


def main(path):
    global totalSize
    global fileNum
    global dirNum
    totalSize = 0
    fileNum = 0
    dirNum = 0
    if not os.path.isdir(path):
        print('Error:"', path, '" is not a directory or does not exist.')
        return
    visitDir(path)
 
def output(path):
    print('文件夹 '+path+' 总大小为:' +  sizeConvert(totalSize))
    print('文件夹 '+path+' 文件总数为:', fileNum)
    print('文件夹 '+path+' 子文件夹数:', dirNum)


def DirNum(path):
    main(path)
    return dirNum
def FileNum(path):
    main(path)
    return fileNum
def TotalSize(path):
    main(path)
    return(sizeConvert(totalSize))
