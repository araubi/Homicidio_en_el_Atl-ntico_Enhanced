# Lector de TSX (TZX con bloque 4B, MSX). Devuelve lista de bloques (id, datos)
import struct,sys
def bloques(d):
    assert d[:7]==b'ZXTape!'
    i=10; out=[]
    while i<len(d):
        bid=d[i]; i+=1
        if bid==0x4B:
            ln=struct.unpack('<I',d[i:i+4])[0]; blk=d[i+4:i+4+ln]
            pause,pilot,pulses,bit0,bit1,cfg=struct.unpack('<HHHHHB',blk[:11])
            out.append((0x4B,blk[12:],dict(pausa=pause,pilot=pilot,pulsos=pulses,b0=bit0,b1=bit1)))
            i+=4+ln
        elif bid==0x30:
            ln=d[i]; out.append((0x30,d[i+1:i+1+ln],None)); i+=1+ln
        elif bid==0x32:
            ln=struct.unpack('<H',d[i:i+2])[0]; out.append((0x32,d[i+2:i+2+ln],None)); i+=2+ln
        elif bid==0x35:
            ln=struct.unpack('<I',d[i+16:i+20])[0]; out.append((0x35,d[i:i+20+ln],None)); i+=20+ln
        elif bid==0x20:
            out.append((0x20,d[i:i+2],None)); i+=2
        elif bid==0x33:
            n=d[i]; out.append((0x33,d[i+1:i+1+3*n],None)); i+=1+3*n
        else:
            raise ValueError('bloque %02X en %d'%(bid,i))
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    for bid,b,inf in bloques(d):
        if bid==0x4B: print('4B',len(b),b[:16].hex(),inf)
        elif bid==0x30: print('30 texto:',b.decode('latin1'))
        elif bid==0x32: print('32 info:',b)
        else: print('%02X'%bid,len(b))
