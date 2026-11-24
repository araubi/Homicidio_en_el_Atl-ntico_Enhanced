import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from cas import blocks
d=open(sys.argv[1],'rb').read(); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
bl=blocks(d); i=0
while i<len(bl):
    b=bl[i]
    if b[:10]==b'\xea'*10:
        name=b[10:16].decode('latin1').strip(); data=b''; i+=1
        while i<len(bl) and not (len(bl[i])==16 and bl[i][:10] in (b'\xd3'*10,b'\xd0'*10,b'\xea'*10)):
            data+=bl[i]; i+=1
        data=data.split(b'\x1a')[0]
        open(f'{out}/{name}.asc','wb').write(data); print(name,'ascii',len(data))
    elif b[:10]==b'\xd0'*10:
        name=b[10:16].decode('latin1').strip(); dd=bl[i+1]
        s=dd[0]|dd[1]<<8; e=dd[2]|dd[3]<<8; x=dd[4]|dd[5]<<8
        open(f'{out}/{name}.bin','wb').write(dd[6:6+e-s+1]); print(name,'bin %04X-%04X exec %04X len %d avail %d'%(s,e,x,e-s+1,len(dd)-6)); i+=2
    else: print('??',i,len(b)); i+=1
