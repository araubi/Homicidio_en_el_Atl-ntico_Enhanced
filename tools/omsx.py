# Control de openMSX por -control stdio
import subprocess,re,time,html,os
class OM:
    def __init__(s,machine='Sony_HB-20P',extra=()):
        env=dict(os.environ)
        s.p=subprocess.Popen(['xvfb-run','-a','openmsx','-machine',machine,'-control','stdio',*extra],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
        s.p.stdin.write('<openmsx-control>\n'); s.buf=''
        s.cmd('set renderer SDL'); s.cmd('set throttle off'); s.cmd('set power on'); s.cmd('set pause on')
    def cmd(s,c):
        s.p.stdin.write('<command>%s</command>\n'%html.escape(c)); s.p.stdin.flush()
        while True:
            l=s.p.stdout.readline()
            if not l: raise EOFError
            s.buf+=l
            m=re.search(r'<reply result="(ok|nok)">(.*?)</reply>',s.buf,re.S)
            if m:
                s.buf=s.buf[m.end():]
                r=html.unescape(m.group(2))
                if m.group(1)=='nok': raise RuntimeError(c+' -> '+r)
                return r
    def run(s,secs):
        # avanza tiempo emulado
        s.cmd('set pause on')
        s.cmd('after time %f {set pause on}'%secs)
        s.cmd('set pause off')
        while s.cmd('set pause')!='true': time.sleep(0.01)
    def peek(s,a): return int(s.cmd('peek %d'%a))
    def shot(s,f): s.cmd('screenshot -raw %s'%f)
    def quit(s):
        try: s.cmd('exit')
        except Exception: pass

MAT={}
for r,s in enumerate(["01234567","89-=\\[];","'`,./\x00AB","CDEFGHIJ","KLMNOPQR","STUVWXYZ"]):
    for b,c in enumerate(s):
        if c!='\x00': MAT[c]=(r,1<<b)
ESP={'SHIFT':(6,1),'CTRL':(6,2),'GRAPH':(6,4),'CAPS':(6,8),'CODE':(6,16),'ESC':(7,4),'BS':(7,32),'RET':(7,128),
     'SPC':(8,1),'LEFT':(8,16),'UP':(8,32),'DOWN':(8,64),'RIGHT':(8,128),' ':(8,1)}
SHIFTED={'$':'4','*':'8','!':'1','#':'3'}
def tecla(o,k,t=0.12,pausa=0.25):
    sh=False
    if k in SHIFTED: k=SHIFTED[k]; sh=True
    r,b=ESP[k] if k in ESP else MAT[k.upper()]
    if sh: o.cmd('keymatrixdown 6 1')
    o.cmd('keymatrixdown %d %d'%(r,b)); o.run(t); o.cmd('keymatrixup %d %d'%(r,b))
    if sh: o.cmd('keymatrixup 6 1')
    o.run(pausa)
def pos(o):
    y=int(o.cmd('vpeek 0x1B00')); x=int(o.cmd('vpeek 0x1B01'))
    return (10-(y-31)//3, (x-14)//2, x, y)
def ve(o,n): return int(o.cmd('peek %d'%(0xDE02+n)))

PAL=[(0,0,0),(0,0,0),(33,200,66),(94,220,120),(84,85,237),(125,118,252),(212,82,77),(66,235,245),(252,85,84),(255,121,120),(212,193,84),(230,206,128),(33,176,59),(201,91,186),(204,204,204),(255,255,255)]
def vram(o):
    return bytes.fromhex(o.cmd('binary encode hex [debug read_block VRAM 0 16384]'))
def pantalla(o,f,escala=2):
    from PIL import Image
    v=vram(o); img=Image.new('RGB',(256,192))
    px=img.load()
    for row in range(24):
        for col in range(32):
            n=v[0x1800+row*32+col]; bank=(row//8)*0x800
            for l in range(8):
                p=v[bank+n*8+l]; c=v[0x2000+bank+n*8+l]
                fg=PAL[c>>4]; bg=PAL[c&15]
                for b in range(8):
                    px[col*8+b,row*8+l]=fg if p&(0x80>>b) else bg
    # sprites 8x8 (modo del juego)
    for i in range(32):
        y,x,pt,cl=v[0x1B00+i*4:0x1B04+i*4]
        if y==208: break
        y=(y+1)&255
        for l in range(8):
            p=v[0x3800+pt*8+l]
            for b in range(8):
                if p&(0x80>>b) and 0<=x+b<256 and 0<=y+l<192: px[x+b,y+l]=PAL[cl&15]
    img.resize((256*escala,192*escala),Image.NEAREST).save(f)

def anda(o,X,maxp=200):
    for i in range(maxp):
        Y1,X1,_,_=pos(o)
        if X1==X: return True
        k='RIGHT' if X>X1 else 'LEFT'
        tecla(o,k,pausa=0.35)
        if pos(o)[1]==X1: return False
    return False
def ascensor(o,piso):
    tecla(o,'$',pausa=2)
    tecla(o,piso,pausa=1)
    for i in range(60):
        o.run(1)
        if o.cmd('peek16 0xF41C') in ('510','520','530') : break
    o.run(1)

ESPERA={'510','520','530'}
def cur(o): return o.cmd('peek16 0xF41C')
def espera(o,maxs=400,espacio=True,log=None):
    """Espera al bucle principal; pulsa ESPACIO en las paginas de texto."""
    for i in range(maxs):
        c=cur(o)
        if c in ESPERA:
            o.run(0.3)
            if cur(o) in ESPERA: return True
        elif c in ('9000','9001','11003','11004') and espacio:
            if log is not None: log.append(pantalla_txt(o))
            tecla(o,' ',pausa=0.3)
        elif c in ('760',):  # ascensor averiado: pulsar A
            tecla(o,'A',pausa=1)
        elif c in ('790',):
            for d in '53602': tecla(o,d,pausa=0.3)
            o.run(1)
        else:
            o.run(0.5)
    return False
def pantalla_txt(o):
    return None
def ascensor(o,piso):
    tecla(o,'$',pausa=1.5)
    if cur(o) in ESPERA: return False
    tecla(o,piso,pausa=0.5)
    espera(o)
    return True
def ir(o,Y,X):
    for intento in range(6):
        Y1,X1,_,_=pos(o)
        if Y1==Y:
            if anda(o,X): return True
        # cambiar de puente
        if 4<=Y<=9 and 4<=Y1<=9 and anda(o,64):
            while pos(o)[0]!=Y:
                tecla(o,'UP' if Y>pos(o)[0] else 'DOWN',pausa=0.5)
            continue
        for L in (76,31) if abs(X-76)<abs(X-31) else (31,76):
            if anda(o,L):
                ascensor(o,chr(78-Y)); break
    return pos(o)[0]==Y and pos(o)[1]==X

SEG={13:[(22,80)],12:[(21,31),(71,82)],11:[(31,31),(71,89)],10:[(10,96)],9:[(10,96)],8:[(8,31),(54,96)],7:[(8,31),(54,95)],
     6:[(1,95)],5:[(1,95)],4:[(1,95)],3:[(2,31),(76,95)],2:[(3,31),(76,95)],1:[(3,95)]}
def segmento(Y,X):
    for a,b in SEG[Y]:
        if a<=X<=b: return (a,b)
def ir(o,Y,X):
    for intento in range(8):
        Y1,X1,_,_=pos(o)
        if Y1==Y and segmento(Y,X)==segmento(Y1,X1):
            if anda(o,X): return True
        lifts=[L for L in (31,76) if segmento(Y,L)==segmento(Y,X)]
        L=lifts[0] if len(lifts)==1 else min(lifts,key=lambda l:abs(l-X))
        # ir al ascensor L en el puente actual (debe estar en mi segmento)
        if segmento(Y1,L)!=segmento(Y1,X1):
            L2=[l for l in (31,76) if segmento(Y1,l)==segmento(Y1,X1)][0]
            anda(o,L2); ascensor(o,'H'); continue   # H,I,J,M y D,E tienen los dos
        anda(o,L); ascensor(o,chr(78-Y))
    return pos(o)[:2]==(Y,X)

def var_basic(o,nombre):
    vt=int(o.cmd('peek16 0xF6C2')); at=int(o.cmd('peek16 0xF6C4'))
    m=bytes.fromhex(o.cmd('binary encode hex [debug read_block memory %d %d]'%(vt,at-vt)))
    i=0; n=(nombre+'\0')[:2].encode()
    while i<len(m):
        t=m[i]; nm=m[i+1:i+3]; val=m[i+3:i+3+t]
        if nm==n: return t,val
        i+=3+t
    return None
def bcd(val):
    e=val[0]
    if e==0: return 0.0
    s=-1 if e&0x80 else 1; e=(e&0x7f)-0x40
    dig=''.join('%02X'%x for x in val[1:])
    return s*float('0.'+dig)*10**e
def H(o):
    r=var_basic(o,'H'); return bcd(r[1]) if r else None
