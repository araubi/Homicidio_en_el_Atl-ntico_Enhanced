#!/usr/bin/env python3
"""Homicidio en el Atlantico Enhanced: cartucho ASCII16 de 64 KB (version rapida).
Uso: python3 build_rom.py ladoA.cas ladoB.cas [--plano plano.vram] [--todas]
Las cintas son las del usuario (no se distribuyen); se comprueba su SHA-1.
El plano del barco se toma de plano.vram si se da (tools/captura_plano.py)
o, si no, de la ROM publicada en ../releases/.
--todas deja ademas la ROM sin cambios y la arreglada sin acelerar.
(araubi con Claude, 2026; MIT)"""
import sys,os,subprocess,glob
AQUI=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,AQUI); sys.path.insert(0,os.path.join(AQUI,'..','desensamblado'))
import build, basic_rom
import tokeniza_rom as tokeniza
BANCO=16384
def rle(d):
    # byte n<128: n literales; n>=128: n-126 repeticiones del byte siguiente; 0 = fin
    out=bytearray(); i=0; lit=bytearray()
    def suelta():
        nonlocal lit
        while lit: out.append(len(lit[:127])); out.extend(lit[:127]); lit=lit[127:]
    while i<len(d):
        j=i
        while j<len(d) and d[j]==d[i] and j-i<129: j+=1
        if j-i>=3: suelta(); out.extend((j-i+126,d[i])); i=j
        else: lit.append(d[i]); i+=1
    suelta(); out.append(0); return out
def largo_rle(d,i):
    o=i
    while d[o]: o+=1+(d[o] if d[o]<128 else 1)
    return o+1-i
def rle_plano(vram,titulo):
    if vram:  # la VRAM tras dibujar el plano con el BASIC original (captura_plano.py)
        v=open(vram,'rb').read()
        return rle(v[0:0xB00])+rle(v[0x2000:0x2B00])
    roms=sorted(glob.glob(os.path.join(AQUI,'..','releases','*.rom')))
    assert roms,'falta plano.vram o la ROM de releases/'
    r=open(roms[-1],'rb').read(); i=r.find(titulo); assert i>0,'titulo no encontrado'
    i+=len(titulo); n1=largo_rle(r,i); n2=largo_rle(r,i+n1)
    return r[i:i+n1+n2]
def main(cas_a,cas_b,vram=None,todas=False):
    build.comprueba(cas_a,build.SHA1_A); build.comprueba(cas_b,build.SHA1_B)
    for c in (cas_a,cas_b):
        for t,n,d in build.ficheros(c):
            if t=='asc': basic_rom.FUENTES[n.decode().strip()]=d
    fa={n.decode().strip():c for t,n,c in build.ficheros(cas_a) if t=='bin'}
    fb={n.decode().strip():c for t,n,c in build.ficheros(cas_b) if t=='bin'}
    def cuerpo(c):  # (destino, datos) de un binario BSAVE
        s=c[0]|c[1]<<8; e=c[2]|c[3]<<8; return s,c[6:6+e-s+1]
    open(os.path.join(AQUI,'titulo.bin'),'wb').write(cuerpo(fa['ENTETE'])[1][0x100:])
    titulo=cuerpo(fa['ENTETE'])[1][0x100:]
    variantes=[(1,1,'HomicidioAtlantico_ES_Enhanced.rom')]
    if todas: variantes=[(0,0,'HomicidioAtlantico_ES.rom'),(1,0,'HomicidioAtlantico_ES_arreglada.rom')]+variantes
    plano=rle_plano(vram,titulo)
    for arr,rap,nombre in variantes:
        INICIO=0x3000 if rap else 0x2400   # la rapida lleva el plano en el banco 0
        open(os.path.join(AQUI,'variante.inc'),'w').write('RAPIDA equ %d\n'%rap)
        if rap: open(os.path.join(AQUI,'plano.rle'),'wb').write(plano)
        fich={2:cuerpo(fa['TRIMMS']),3:cuerpo(fa['MSA']),
              4:(0x8001,tokeniza.tokeniza(basic_rom.juego(arr,rap))),
              5:(0x8001,tokeniza.tokeniza(basic_rom.test(arr)))}
        for i in range(1,41): fich[10+i]=cuerpo(fb['TEM%d'%i])
        flujo=bytearray(); tabla={}; o=INICIO
        for k in [3,4,5]+list(range(11,51))+[2]:
            dst,d=fich[k]; tr=[]; i=0
            while i<len(d):
                n=min(len(d)-i,BANCO-o%BANCO)
                tr.append((o//BANCO,0x4000+o%BANCO,dst+i,n)); i+=n; o+=n
            flujo+=d; tabla[k]=tr
        assert o<=4*BANCO,o
        L=['TABLA:']+['        dw %s'%('T%d'%k if k in tabla else 'T_VACIO') for k in range(51)]
        L.append('T_VACIO: db 0FFh')
        for k,tr in tabla.items():
            L.append('T%d:'%k)
            for b,s,dd,n in tr: L.append('        db %d\n        dw %d,%d,%d'%(b,s,dd,n))
            L.append('        db 0FFh')
        open(os.path.join(AQUI,'tabla.inc'),'w').write('\n'.join(L)+'\n')
        subprocess.check_call(['pasmo','cartucho.asm','banco0.bin'],cwd=AQUI)
        b0=open(os.path.join(AQUI,'banco0.bin'),'rb').read()
        assert len(b0)<=INICIO,hex(len(b0))
        rom=bytearray(b'\xff'*(4*BANCO))
        rom[:len(b0)]=b0; rom[INICIO:INICIO+len(flujo)]=flujo
        for b in (1,2,3): assert rom[b*BANCO:b*BANCO+2]!=b'AB'
        open(os.path.join(AQUI,nombre),'wb').write(rom)
        print(nombre,'banco0 %d bytes, ocupado %d de 65536'%(len(b0),INICIO+len(flujo)))
if __name__=='__main__':
    a=sys.argv[1:]; todas='--todas' in a; a=[x for x in a if x!='--todas']
    vram=None
    if '--plano' in a: k=a.index('--plano'); vram=a[k+1]; del a[k:k+2]
    if len(a)!=2: sys.exit(__doc__)
    main(a[0],a[1],vram,todas)
