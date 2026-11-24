# Prepara los BASIC de la ROM (araubi con Claude, 2026; MIT)
import re,sys,os
AQUI=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,AQUI)
FUENTES={}   # nombre -> texto ASCII del BASIC, sacado de las cintas del usuario (build_rom.py)
import tokeniza_rom as T
def chars(s): return s.encode('latin-1')
T.chars=chars
def lee(nombre):
    L=[]
    for l in FUENTES[nombre].decode('latin-1').split('\r\n'):
        l=l.strip('\x1a')
        if not l.strip(): continue
        n,_,t=l.lstrip().partition(' ')
        L.append((int(n),t))
    return L
KWL=r'(GOTO|GOSUB|THEN|ELSE|RESTORE|RESUME)'
def renum(lines,off):
    out=[]
    for n,t in lines:
        parts=re.split(r'("[^"]*"?)',t)
        for i in range(0,len(parts),2):
            def f(m):
                nums=re.sub(r'\d+',lambda k:str(int(k.group())+off),m.group(2))
                return m.group(1)+nums
            parts[i]=re.sub(KWL+r'(\s*\d+(?:\s*,\s*\d+)*)',f,parts[i])
        out.append((n+off,''.join(parts)))
    return out
def sub(lines,n,old,new):
    for i,(k,t) in enumerate(lines):
        if k==n:
            assert old in t,(n,old,t); lines[i]=(k,t.replace(old,new,1)); return
    raise KeyError(n)
def juego(arreglada,rapida=0):
    m2=renum(lee('MSA2'),20000)
    sub(m2,20230,'RUN"CAS:MSA3"','GOTO 10')
    m3=lee('MSA3')
    sub(m3,20,'BLOAD"CAS:MSA"','DEFUSR9=&HDDF3:A=USR9(3)')
    sub(m3,1550,'K$="CAS:TEM"+RIGHT$(K$,LEN(K$)-1):BLOADK$+".BIN"','DEFUSR9=&HDDF3:A=USR9(10+PEEK(NU))')
    if arreglada:
        # 1) morse sin espacios ni Ñ (como el francés)
        for i,(k,t) in enumerate(m3):
            if k==1680: m3[i]=(k,'DATA POLICIA,FEDERAL,NUEVAYORK,BUSCAMOSA,JOHNWADE,INDIVIDUO,MUYPELIGROSO,VIAJA,SOBREELBORGONA,BAJOEL,NOMBREDE,AL')
        # 2) maleta
        sub(m3,1390,'PRINT#1,"CORRECTO..."','PRINT#1,"NO ES CORRECTO..."')
        # erratas
        sub(m3,1520,'DEMASADIO','DEMASIADO')
        sub(m3,1610,'CONCIENCA','CONCIENCIA')
        sub(m3,1340,'FEMININOS','FEMENINOS')
        # la A de UNA caia en la columna 0, fuera de la ventana que se borra
        sub(m3,1340,'FEMENINOS,UNA  TARJETA.','FEMENINOS,     UNA TARJETA.')
        sub(m3,1180,'NON AUTORIZADO','NO AUTORIZADO')
        sub(m3,740,'\xadAI!','\xadAY!')
        # columna debajo del puente (se repinta al andar y al cambiar de puente)
        sub(m3,225,'COLOR15,1','COLOR15,1:GOSUB396')
        sub(m3,340,'GOSUB420','GOSUB420:GOSUB396')
        sub(m3,350,'GOSUB420','GOSUB420:GOSUB396')
        m3.append((396,'LINE(80,99)-(167,107),1,BF:COLOR8:PRESET(84,100):PRINT#1,"COL.";X1:COLOR15:RETURN'))
    if rapida:
        rapido(m2,m3)
    return sorted(m3+m2)
def rapido(m2,m3):
    """Version rapida: las partes lentas pasan a USR9 (rapida.asm)."""
    # plano del barco ya dibujado en la ROM
    m2[:]=[(k,t) for k,t in m2 if not (20045<=k<=20220 or k>=20240)]
    m2.append((20045,'DEFUSR9=&HDDF3:V=USR9(8)'))
    d=dict(m3)
    def pon(n,t): 
        for i,(k,_) in enumerate(m3):
            if k==n: m3[i]=(n,t); return
        m3.append((n,t))
    # WRTVRM rapido para MSA (caras y salas)
    sub(m3,60,'COLOR15,1,1','COLOR15,1,1:V=USR9(10)')
    # ventanas y columna
    pon(420,'V=USR9(0):RETURN')
    pon(430,'V=USR9(1):RETURN')
    pon(396,'V=USR9(512+X1):RETURN')
    for i,(k,t) in enumerate(m3):
        t=t.replace('LINE(8*2,8*19)-(8*32,8*24),1,BF','V=USR9(5)').replace('LINE (8*2,8*19)-(8*32,8*24),1,BF','V=USR9(5)')
        t=t.replace('LINE(8*2,8*20)-(8*32,8*24),1,BF','V=USR9(9)')
        m3[i]=(k,t)
    # una sola linea elige la orden en vez de 13 IF seguidos
    libra=d[330].split('K$="')[1][0]   # la tecla de grabar, tal cual la cinta
    ks='CHR$(30)+CHR$(31)+"DV*$MPI%s"+CHR$(29)+CHR$(28)+"E"'%libra
    sub(m3,210,'HM=700:','HM=700:KS$=%s:'%ks)
    pon(240,'ON INSTR(KS$,K$) GOTO 250,260,270,280,290,291,300,310,320,330,340,350,360:GOTO 370')
    sub(m3,340,'GOSUB420:GOSUB396','GOSUB420:GOSUB396:GOTO370')
    sub(m3,350,'GOSUB420:GOSUB396','GOSUB420:GOSUB396:GOTO370')
    # textos de un golpe
    pon(1560,'IF PEEK(O)>31 THEN V=USR9(2):O=O+V')
    pon(1160,'IF PEEK(O+O1)>2 THEN V=USR9(4)')
def test(arreglada):
    t=lee('TEST')
    if arreglada:
        t.append((195,'IF R=15 THEN GOSUB 320:GOTO 210'))
    return sorted(t)
if __name__=='__main__':
    for arr,rap in ((0,0),(1,0),(1,1)):
        for nom,L in (('JUEGO',juego(arr,rap)),('TEST',test(arr))):
            arr2=arr+rap
            b=T.tokeniza(L)
            print(nom,arr,len(b),hex(0x8001+len(b)))
            open('%s_%d.tok'%(nom,arr2),'wb').write(b)
            open('%s_%d.asc'%(nom,arr2),'wb').write(('\r\n'.join('%d %s'%x for x in L)+'\r\n').encode('latin-1')+b'\x1a')
