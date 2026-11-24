# Tokenizador MSX-BASIC (inverso de msxbasic.py). Mystery House, 2026-11-04.
import re,struct,sys
sys.path.insert(0,__file__.rsplit('/',1)[0])
# Copia del tokenizador de Mystery House con constantes con exponente y simple precision.
from msxbasic import TOK1,TOK2,KATA,HIRA1,HIRA2,HIRA3,G1
INV={}
for i,c in enumerate(KATA): INV[c]=0xA1+i
for i,c in enumerate(HIRA1): INV[c]=0x86+i
for i,c in enumerate(HIRA2): INV[c]=0x91+i
for i,c in enumerate(HIRA3): INV[c]=0xE0+i
G1INV={c:i+0x41 for i,c in enumerate(G1)}
# Caracteres propios de la traducción (glifos en la fuente en RAM, códigos 80h-8Ah)
ESP={'♥':0x80,'á':0x81,'é':0x82,'í':0x83,'ó':0x84,'ú':0x85,'ñ':0x86,'Ñ':0x87,'¿':0x88,'¡':0x89,'▣':0x8A}
KW=[(t,0x00,c) for c,t in TOK1.items()]+[(t,0xFF,c) for c,t in TOK2.items()]
KW.sort(key=lambda x:-len(x[0]))
LNKW={'GOTO','GOSUB','THEN','ELSE','RESTORE','RUN','LIST','LLIST','DELETE','RESUME','RETURN','AUTO','RENUM'}
def chars(s):
    """Texto (cadenas, REM, DATA) -> bytes; {XX} escapes, {01XX}."""
    out=bytearray();i=0
    while i<len(s):
        m=re.match(r'\{([0-9A-F]{2,4})\}',s[i:])
        if m:
            out+=bytes.fromhex(m.group(1)); i+=m.end(); continue
        c=s[i]
        if c in ESP: out.append(ESP[c])
        elif c in G1INV: out+=bytes([1,G1INV[c]])
        elif c in INV: out.append(INV[c])
        elif ord(c)<128: out.append(ord(c))
        else: raise ValueError('carácter %r'%c)
        i+=1
    return bytes(out)
def num(tok, lnctx):
    if tok.startswith('&H'): return b'\x0c'+struct.pack('<H',int(tok[2:],16))
    if tok.startswith('&O'): return b'\x0b'+struct.pack('<H',int(tok[2:],8))
    if lnctx and tok.isdigit(): return b'\x0e'+struct.pack('<H',int(tok))
    if tok.isdigit() and int(tok)<32768:
        v=int(tok)
        if v<10: return bytes([0x11+v])
        if v<256: return bytes([0x0f,v])
        return b'\x1c'+struct.pack('<h',v)
    # coma flotante BCD (como el MSX: 6 cifras o menos y sin '#' = simple)
    m=re.fullmatch(r'(\d*)\.?(\d*)E([+-]?\d+)([!#]?)',tok)
    if m: ip,fp,ex,suf=m.groups(); ex=int(ex)
    else:
        suf=tok[-1] if tok[-1] in '!#' else ''
        ip,_,fp=tok.rstrip('!#').partition('.'); ex=0
    digs=ip+fp; e=len(ip)+ex
    st=digs.lstrip('0'); e-=len(digs)-len(st); digs=st.rstrip('0')
    if not suf: suf='!' if len(digs)<=6 else '#'
    n=4 if suf=='!' else 8
    b=bytes([e+0x40])+bytes.fromhex((digs+'0'*16)[:2*(n-1)]) if digs else bytes(n)
    return bytes([0x1d if suf=='!' else 0x1f])+b
def tok_line(s):
    out=bytearray();i=0;ident=False;lnctx=False;ultimo=''
    while i<len(s):
        c=s[i]
        if c=='"':
            j=s.find('"',i+1)
            if j<0: out+=b'"'+chars(s[i+1:]); break
            out+=b'"'+chars(s[i+1:j])+b'"'; i=j+1; ident=False; continue
        if c=="'":
            out+=b':\x8f\xe6'+chars(s[i+1:]); break
        if s.startswith('ELSE',i):
            out+=b':\xa1'; i+=4; ident=False; lnctx=True; continue
        m=None
        if not ident or True:
            for t,pre,code in KW:
                if s.startswith(t,i):
                    m=(t,pre,code); break
        if m and not (ident and m[0] in ('E',)):
            t,pre,code=m
            out+= bytes([0xff,code]) if pre else bytes([code])
            i+=len(t); ident=False
            if t=='REM': out+=chars(s[i:]); break
            if t=='DATA':
                # hasta ':' fuera de comillas
                j=i;q=False
                while j<len(s) and (q or s[j]!=':'):
                    if s[j]=='"': q=not q
                    j+=1
                out+=chars(s[i:j]); i=j; continue
            lnctx = t in LNKW or (t in ('=','<','>') and ultimo=='ERL')
            ultimo=t
            continue
        if not ident:
            mm=re.match(r'&H[0-9A-Fa-f]+|&O[0-7]+|\d*\.?\d+E[+-]?\d+[!#]?|\d*\.\d+[!#]?|\d+\.\d*[!#]?|\d+[!#]|\d+',s[i:])
            if mm:
                out+=num(mm.group(0),lnctx); i+=mm.end(); continue
        if c.isalpha(): ident=True; out.append(ord(c)); i+=1; continue
        if c.isdigit() and ident: out.append(ord(c)); i+=1; continue
        ident=False
        if c==',' : pass
        elif c not in ' ': lnctx=False
        out+=chars(c); i+=1
    return bytes(out)
def tokeniza(lines, base=0x8001, links=None):
    prog=bytearray(); addr=base
    for k,(ln,txt) in enumerate(lines):
        body=tok_line(txt)
        nxt=addr+4+len(body)+1
        lk=links[k] if links else nxt
        prog+=struct.pack('<HH',lk,ln)+body+b'\0'; addr=nxt
    prog+=b'\0\0'
    return bytes(prog)
def lee_listado(path):
    L=[]
    for l in open(path,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l.strip(): continue
        n,_,t=l.partition(' ')
        L.append((int(n),t))
    return L
