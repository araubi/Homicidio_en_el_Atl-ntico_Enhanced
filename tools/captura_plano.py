# Captura la VRAM tras dibujar el plano con el BASIC original (araubi con Claude, 2026; MIT)
# Uso: python3 captura_plano.py HomicidioAtlantico_ES_arreglada.rom  -> vram_plano.bin (pasar a build_rom.py con --plano)
# (la ROM arreglada sale de build_rom.py --todas; necesita openMSX con la BIOS del HB-20P)
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from omsx import *
o=OM('Sony_HB-20P',('-cart',sys.argv[1]))
o.run(10); tecla(o,'J',pausa=0)
vis=set()
o.cmd('debug set_bp -once 0 {[peek16 0xF41C]==20040} {set pause on}') if False else None
# usa condicion de linea con watchpoint simple: sondeo fino
base=None
for i in range(20000):
    o.run(0.01); c=int(cur(o))
    if c>=20040 and base is None and c<20240: base=vram(o); print('base en',c)
    if c in (20230,10,20,25): break
print('fin en',c)
open('vram_base.bin','wb').write(base); open('vram_plano.bin','wb').write(vram(o))
o.quit()
