import struct,sys,os
def files(d):
    bs=d[:512]
    bps=struct.unpack('<H',bs[11:13])[0]; spc=bs[13]; res=struct.unpack('<H',bs[14:16])[0]; nf=bs[16]
    ndir=struct.unpack('<H',bs[17:19])[0]; spf=struct.unpack('<H',bs[22:24])[0]
    fat=d[res*bps:(res+spf)*bps]
    dirs=(res+nf*spf)*bps; data0=dirs+ndir*32
    def nxt(c):
        o=c*3//2; v=fat[o]|fat[o+1]<<8
        return v>>4 if c&1 else v&0xfff
    out=[]
    for i in range(ndir):
        e=d[dirs+i*32:dirs+i*32+32]
        if e[0]==0: break
        if e[0]==0xe5: continue
        name=e[:8].decode('latin1').strip()+'.'+e[8:11].decode('latin1').strip()
        cl=struct.unpack('<H',e[26:28])[0]; sz=struct.unpack('<I',e[28:32])[0]
        b=b''; c=cl
        while 2<=c<0xff8 and len(b)<sz:
            o=data0+(c-2)*spc*bps; b+=d[o:o+spc*bps]; c=nxt(c)
        out.append((name,b[:sz]))
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    os.makedirs(sys.argv[2],exist_ok=True)
    for n,b in files(d):
        print(n,len(b)); open(os.path.join(sys.argv[2],n),'wb').write(b)
