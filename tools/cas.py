import sys
HDR=bytes([0x1F,0xA6,0xDE,0xBA,0xCC,0x13,0x7D,0x74])
def blocks(d):
    pos=[];i=0
    while True:
        j=d.find(HDR,i)
        if j<0:break
        pos.append(j);i=j+8
    out=[]
    for k,p in enumerate(pos):
        e=pos[k+1] if k+1<len(pos) else len(d)
        out.append(d[p+8:e])
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    for n,b in enumerate(blocks(d)):
        t=''
        if len(b)>=16 and b[:10] in (b'\xd3'*10,b'\xd0'*10,b'\xea'*10):
            t={0xd3:'BASIC',0xd0:'BIN',0xea:'ASCII'}[b[0]]+' "'+b[10:16].decode('latin1')+'"'
        elif len(b)>=6:
            t='data %04X %04X %04X'%(b[0]|b[1]<<8,b[2]|b[3]<<8,b[4]|b[5]<<8)
        print(n,len(b),t)
