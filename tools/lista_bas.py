import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import msxbasic
def chint(b):
    if 0x20<=b<0x7f: return chr(b)
    if b>=0x80: return bytes([b]).decode('cp437')
    return '{%02X}'%b
msxbasic.ch=chint
def chstr(bs): return ''.join(chint(x) if x!=1 else '' for x in bs)
msxbasic.chstr=lambda bs: ''.join(chint(x) for x in bs)
def lista(path):
    d=open(path,'rb').read()
    if d[0]==0xff: d=d[1:]
    return '\n'.join('%d %s'%(ln,t) for ln,p,raw,t,n in msxbasic.listar(d))
if __name__=='__main__': print(lista(sys.argv[1]))
