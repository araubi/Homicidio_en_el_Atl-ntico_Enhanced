#!/usr/bin/env python3
"""Rehace las dos cintas de "Homicidio en el Atlantico" (MSX, Cobra Soft/Infogrames 1987)
a partir del desensamblado.  Uso:
    python3 build.py ladoA_original.cas ladoB_original.cas
Las cintas originales solo se usan para sacar lo que no se publica (los
programas BASIC, los graficos de ENTETE/TRIMMS, los datos de MSA y los 40
testimonios) y para comparar el resultado.
Ensambla con sjasmplus (si esta) o pasmo. Deja salida/ladoA.cas y salida/ladoB.cas.
"""
import sys,os,subprocess,hashlib,shutil
# Cinta en castellano (TOSEC: "...(1987)(Infogrames)(FR)(es)(Side A)(Game)[!].cas" y "(Side B)(Testimonies)[!].cas")
SHA1_A='38ac8aa8d9837200f5cb7feb00db4b62b3448887'
SHA1_B='d4a2957453debe1d641c3b42ac88f066867c1a3f'
# trozos de datos de MSA (desde BEE6h): nombre, tamano
MSA_DATOS=[('msa_dibujos.bin',54),('msa_caras.bin',6400),('msa_ocupantes.bin',249),
           ('msa_textos.bin',727),('msa_salas.bin',519)]
MSA_CODIGO=0x1E6   # BD00h-BEE5h
def comprueba(cas,sha):
    h=hashlib.sha1(open(cas,'rb').read()).hexdigest()
    if h!=sha: print('AVISO: %s no es la cinta esperada (SHA-1 %s, se esperaba %s)'%(cas,h,sha))
def datos(orig,trabajo):
    """Deja en trabajo/ los datos que no se publican, sacados de la cinta."""
    open(os.path.join(trabajo,'entete_resto.bin'),'wb').write(orig['ENTETE'][6+0x3D:])
    open(os.path.join(trabajo,'trimms_dibujos.bin'),'wb').write(orig['TRIMMS'][6+0x5B:])
    m=orig['MSA'][6:]; o=MSA_CODIGO
    for n,t in MSA_DATOS:
        open(os.path.join(trabajo,n),'wb').write(m[o:o+t]); o+=t
    assert o==len(m),(o,len(m))
AQUI=os.path.dirname(os.path.abspath(__file__))
HDR=bytes([0x1F,0xA6,0xDE,0xBA,0xCC,0x13,0x7D,0x74])
def bloques(d):
    pos=[];i=0
    while True:
        j=d.find(HDR,i)
        if j<0:break
        pos.append(j);i=j+8
    return [d[p+8:(pos[k+1] if k+1<len(pos) else len(d))] for k,p in enumerate(pos)]
def ficheros(cas):
    """lista (tipo, nombre6, contenido) de una CAS"""
    bl=bloques(open(cas,'rb').read()); out=[]; i=0
    while i<len(bl):
        b=bl[i]
        if b[:10]==b'\xd0'*10:
            dd=bl[i+1]; s=dd[0]|dd[1]<<8; e=dd[2]|dd[3]<<8
            out.append(('bin',b[10:16],dd[:6+e-s+1])); i+=2
        elif b[:10]==b'\xea'*10:
            data=b''; i+=1
            while i<len(bl) and not (len(bl[i])==16 and bl[i][:10] in (b'\xd0'*10,b'\xea'*10,b'\xd3'*10)):
                data+=bl[i]; i+=1
            out.append(('asc',b[10:16],data.split(b'\x1a')[0]))
        else: raise ValueError('bloque raro')
    return out
def ensambla(asm,dst,trabajo):
    for f in os.listdir(AQUI):
        if f.endswith(('.asm','.inc')): shutil.copy(os.path.join(AQUI,f),trabajo)
    if shutil.which('sjasmplus'):
        subprocess.check_call(['sjasmplus','--nologo','--raw='+dst,asm],cwd=trabajo)
    else:
        subprocess.check_call(['pasmo','--bin',asm,dst],cwd=trabajo)
    return open(os.path.join(trabajo,dst),'rb').read()
def cas(ficheros_out,alinea_ultimo=True):
    out=bytearray()
    def bloque(data,ultimo=False):
        while len(out)%8: out.append(0)
        out.extend(HDR); out.extend(data)
    for tipo,nombre,cont in ficheros_out:
        if tipo=='bin':
            bloque(b'\xd0'*10+nombre); bloque(cont)
        else:
            bloque(b'\xea'*10+nombre)
            d=cont+b'\x1a'
            while len(d)%256: d+=b'\x1a'
            for k in range(0,len(d),256): bloque(d[k:k+256])
    return bytes(out)
def cabecera(ini,fin,ej): return bytes([ini&255,ini>>8,fin&255,fin>>8,ej&255,ej>>8])
def main():
    if len(sys.argv)<3: print(__doc__); sys.exit(1)
    comprueba(sys.argv[1],SHA1_A); comprueba(sys.argv[2],SHA1_B)
    A=ficheros(sys.argv[1]); B=ficheros(sys.argv[2])
    trabajo=os.path.join(AQUI,'trabajo'); os.makedirs(trabajo,exist_ok=True)
    sal=os.path.join(AQUI,'salida'); os.makedirs(sal,exist_ok=True)
    orig={n.decode().strip():c for t,n,c in A}
    datos(orig,trabajo)
    entete=ensambla('entete.asm','entete.bin',trabajo)
    trimms=ensambla('trimms.asm','trimms.bin',trabajo)
    msa=ensambla('msa_es.asm','msa.bin',trabajo)
    def bas(n): return orig[n]          # los programas BASIC, tal cual la cinta
    ladoA=[('asc',b'MSA1  ',bas('MSA1')),
           ('bin',b'ENTETE',cabecera(0x9000,0x9000+len(entete)-1,0x9000)+entete),
           ('bin',b'TRIMMS',cabecera(0x9000,0x9000+len(trimms)-1,0x9000)+trimms),
           ('asc',b'MSA2  ',bas('MSA2')),('asc',b'MSA3  ',bas('MSA3')),
           ('bin',b'MSA   ',cabecera(0xBD00,0xBD00+len(msa)-1,0xBD00)+msa),
           ('asc',b'TEST  ',bas('TEST'))]
    ladoB=[('bin',n,c) for t,n,c in B]   # los 40 testimonios, tal cual
    for nombre,lista,o in (('ladoA.cas',ladoA,sys.argv[1]),('ladoB.cas',ladoB,sys.argv[2])):
        d=cas(lista); orig_d=open(o,'rb').read()
        # la cara B original no rellena el ultimo bloque
        if len(d)>len(orig_d) and d[:len(orig_d)]==orig_d: d=d[:len(orig_d)]
        open(os.path.join(sal,nombre),'wb').write(d)
        print(nombre,len(d),hashlib.sha1(d).hexdigest(),'IDENTICA' if d==orig_d else 'DISTINTA del original')
if __name__=='__main__': main()
