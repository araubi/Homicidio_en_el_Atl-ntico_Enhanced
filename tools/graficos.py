# Extrae los graficos: titulo (ENTETE), 27 dibujos de sala (TRIMMS) y 40 caras (MSA)
import sys,os
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from omsx import PAL
def sala(trimms,msa,n):
    ram=bytearray(0x10000); ram[0x4000:0x4000+0x35ff]=trimms[0x5B:0x5B+0x35ff]
    a=0xBEE6-0xBD00+2*(n-1); de=msa[a]|msa[a+1]<<8
    cols=ram[de]; de+=1; rows=ram[de]
    vram=bytearray(0x4000)
    def desc(de,hl):
        de+=1; val=ram[de]; de+=1; cnt=ram[de]
        for c in range(cols):
            for r in range(rows):
                for k in range(8):
                    vram[(hl+c*8+r*256+k)&0x3fff]=val
                    cnt=(cnt-1)&255
                    if cnt==0: de+=1; val=ram[de]; de+=1; cnt=ram[de]
        return de
    de=desc(de,0x0BB0); de-=2; desc(de,0x2BB0)
    img=Image.new('RGB',(cols*8,rows*8)); px=img.load()
    for c in range(cols):
        for r in range(rows):
            for k in range(8):
                p=vram[0x0BB0+c*8+r*256+k]; co=vram[0x2BB0+c*8+r*256+k]
                for b in range(8):
                    px[c*8+b,r*8+k]=PAL[co>>4] if p&(0x80>>b) else PAL[co&15]
    return img,cols,rows
def cara(msa,n):
    a=0xBF1C-0xBD00+160*(n-1)
    img=Image.new('RGB',(32,40),(255,255,255)); px=img.load()
    for fr in range(5):
        for l in range(8):
            for ch in range(4):
                v=msa[a]; a+=1
                for b in range(8):
                    if v&(0x80>>b): px[ch*8+b,fr*8+l]=(0,0,0)
    return img
def titulo(entete):
    vram=bytearray(0x4000); i=0x100
    for base in (0,0x2000):
        hl=base
        while True:
            v,c=entete[i],entete[i+1]; i+=2
            if c==0: break
            for k in range(c): vram[hl]=v; hl+=1
    img=Image.new('RGB',(256,192)); px=img.load()
    for row in range(24):
        for col in range(32):
            for l in range(8):
                o=(row//8)*0x800+(row%8)*256+col*8+l
                p=vram[o]; co=vram[0x2000+o]
                for b in range(8): px[col*8+b,row*8+l]=PAL[co>>4] if p&(0x80>>b) else PAL[co&15]
    return img
if __name__=='__main__':
    A=sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
    tr=open(A+'/TRIMMS.bin','rb').read(); ms=open(A+'/MSA.bin','rb').read(); en=open(A+'/ENTETE.bin','rb').read()
    titulo(en).resize((512,384),Image.NEAREST).save(out+'/titulo_ENTETE.png')
    hoja=Image.new('RGB',(9*72,3*72),(40,40,40))
    for n in range(1,28):
        try:
            im,c,r=sala(tr,ms,n)
            im.save(out+'/sala_%02d.png'%n); hoja.paste(im,(((n-1)%9)*72+4,((n-1)//9)*72+4))
        except Exception as e: print('sala',n,e)
    hoja.resize((hoja.width*2,hoja.height*2),Image.NEAREST).save(out+'/salas_todas.png')
    hc=Image.new('RGB',(10*40,4*48),(80,80,80))
    for n in range(1,41):
        im=cara(ms,n); hc.paste(im,(((n-1)%10)*40+4,((n-1)//10)*48+4))
    hc.resize((hc.width*3,hc.height*3),Image.NEAREST).save(out+'/caras_todas.png')
