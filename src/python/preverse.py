import os
from os.path import isfile, isdir, abspath, dirname, basename, getsize, join
from binascii import unhexlify

def getRevFileName(name):
    hexname = name.encode('utf-8').hex()
    return hexname + '.rev'

def restoreRevFileName(revName):
    if revName.endswith(".rev"):
        revName = revName[:-4]
    return unhexlify(revName).decode("utf-8")


def reverseBytes(bytes, outBytes, size):
    for i in range(size):
        outBytes[i] = bytes[size -1 -i]

def createRevFile(origin, blocksize = 65536, revfn = None):
    if not isfile(origin):
        return
    fsize = getsize(origin)
    fullpath = abspath(origin)
    pathname = dirname(fullpath)
    if revfn is None:
        revfn = getRevFileName(basename(fullpath))

    reververPos = lambda pos: fsize - pos

    buf = bytearray(blocksize)
    with open(origin, 'rb') as input:
        with open(join(pathname, revfn), 'wb') as output:
            pos = 0
            while pos < fsize:
                readsize = min(blocksize, fsize - pos)
                # read from reversed pos to pos + readsize
                fromLoc, toLoc = reververPos(pos + readsize), reververPos(pos)

                input.seek(fromLoc)
                read = input.read(readsize)
                assert len(read) == readsize
                if readsize == blocksize:
                    tmp = buf
                else:
                    tmp = bytearray(readsize)
                reverseBytes(read, tmp, readsize)
                output.write(tmp)

                pos += readsize

def reverseDir(dirpath, renameTop = True):
    if not isdir(dirpath):
        return

    fullpath = abspath(dirpath)
    dname = basename(fullpath)
    parentdir = dirname(fullpath)

    for fname in os.listdir(dirpath):
        fullname = join(fullpath, fname)

        if isdir(fullname):
            reverseDir(fullname)
        elif isfile(fullname):
            createRevFile(fullname)
            os.remove(fullname)

    if renameTop:
        os.rename(fullpath, join(parentdir, getRevFileName(dname)))


def restore(revPath):
    fullpath = abspath(revPath)
    bname = basename(fullpath)
    if not isdir(fullpath) and not bname.endswith(".rev"):
        return
    parentdir = dirname(fullpath)

    if isdir(fullpath):
        for fname in os.listdir(fullpath):
            fullsub = join(fullpath, fname)
            restore(fullsub)
        if fullpath.endswith(".rev"):
            os.rename(join(parentdir, bname), join(parentdir, restoreRevFileName(bname)))
    elif isfile(fullpath):
        nameRestore = restoreRevFileName(bname)
        createRevFile(fullpath, revfn=nameRestore)
        os.remove(fullpath)



if __name__ == '__main__':
    #createRevFile(r"c:\temp\upload\HCartoon\avi.xxx", revfn='xxx.avi')
    #reverseDir(r"c:\temp\upload\HCartoon", renameTop=False)
    pass
