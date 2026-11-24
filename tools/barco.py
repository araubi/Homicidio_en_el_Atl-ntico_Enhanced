# Simulación en Python de las rutinas USR 2 (sala) y USR 3 (ocupante) de MSA.bin
import sys,re
def carga(path, base=0xBD00, hdr=0):
    d=open(path,'rb').read()[hdr:]
    m=bytearray(0x10000); m[base:base+len(d)]=d; return m
def sala(m,Y,X,tabla=None):
    hl=tabla if tabla else m[0xBD2B]|m[0xBD2C]<<8
    a=(0x0E-Y)&0xFF; b=a
    while True:
        # bucle bd2e: lee hasta FF, djnz
        while True:
            v=m[hl]; hl+=1
            if v==0xFF: break
        b=(b-1)&0xFF
        if b==0: break
    a=X
    if a<m[hl]: return (0,0)
    a=(a-m[hl])&0xFF
    while True:
        b=a; hl+=1; c=m[hl]
        if not c&0x80:
            b=a; a=(a-1)&0xFF
            if a==0: return (m[hl],m[hl+1])
            hl+=1; continue
        if m[hl]==0xFF: return (0,0)
        c&=0x7F; a=b; c+=1; r=(a-c)&0xFF; hl+=1
        if r&0x80 or r==0: return (m[hl],m[hl+1])
        a=r; hl+=1
def ocupante(m,Y,X,tabla=0xD81C):
    hl=tabla
    while True:
        if m[hl]==Y:
            if m[hl+1]==X:
                b2,b3=m[hl+2],m[hl+3]
                if b3>=0x40: return ('texto',b3<<8|b2)
                return ('pers',b2,b3)
            hl+=4; continue
        if m[hl]==0xFF: return None
        hl+=4
if __name__=='__main__':
    m=carga(sys.argv[1],hdr=int(sys.argv[2]) if len(sys.argv)>2 else 0)
    for Y in range(13,0,-1):
        prev=None
        for X in range(0,120):
            s=sala(m,Y,X)
            if s!=prev: print('Y%2d %s X%3d sala=%s'%(Y,chr(78-Y),X,s)); prev=s
