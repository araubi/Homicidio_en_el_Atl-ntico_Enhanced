import sys
# MSX internacional ~ CP437 en 80h-FFh
def dec(b):
    return b.decode('cp437').replace('\r\n','\n').replace('\r','\n')
if __name__=='__main__':
    sys.stdout.write(dec(open(sys.argv[1],'rb').read()))
