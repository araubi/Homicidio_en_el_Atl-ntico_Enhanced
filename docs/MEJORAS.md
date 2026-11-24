# Homicidio en el Atlántico Enhanced (MSX): mejoras

Cartucho de 64 KB (mapper ASCII16) con la cinta española entera dentro: juego, dibujos, rutinas y los 40 testimonios. No hace falta la cara B: los testimonios salen al momento. araubi con Claude, 5-11-2026.

## La ROM

`releases/HomicidioAtlantico_ES_Enhanced_v1.0.rom` es el juego de la cinta con sus fallos arreglados y con las partes lentas pasadas a ensamblador. Es la única que se publica. Con `build_rom.py --todas` las fuentes montan también la versión fiel a la cinta y la arreglada lenta, para comparar.

Arreglos sobre la cinta:

1. **El morse de la radio se oye entero** (A77, S). En la cinta se cortaba con «ATENCIÓN ERROR DE CASSETTE» en la Ñ de BORGOÑA. Ahora el mensaje va sin espacios ni eñes, como en la versión francesa.
2. **La maleta dice «NO ES CORRECTO...»** cuando fallas la combinación (la cinta decía «CORRECTO...»).
3. **El test perfecto tiene su mensaje**: con 15 de 15 sale «¡MUY BIEN! ¡NO HAY FALTA NINGUNA!». Es el mismo arreglo que trae la versión alemana.
4. **Columna en pantalla**: debajo de «PUENTE D» sale «COL. 25». Es el mismo número que usa la guía (D25 = puente D, columna 25).
5. **Una «A» suelta en la columna 0**: al registrar el cadáver del frigorífico (M27, F), la A de «UNA TARJETA» caía fuera de la ventana de texto y se quedaba en pantalla el resto de la partida. Ahora el texto está recolocado.
6. Erratas: DEMASADIO → DEMASIADO, CONCIENCA → CONCIENCIA, FEMININOS → FEMENINOS, NON AUTORIZADO → NO AUTORIZADO, ¡AI! → ¡AY!

## Qué la hace rápida

Lo lento está hecho en código máquina. La lógica del juego sigue siendo el BASIC original, así que se juega igual. Tiempos medidos en un HB-20P emulado:

| Qué | BASIC original | Rápida |
|---|---|---|
| Del menú a la pregunta de cargar (dibujo del plano) | 29,7 s | 2,5 s |
| Un paso por el puente | 0,38 s | 0,02 s |
| Ver la sala (V) | 0,66 s | 0,30 s |
| Registrar (I) | 1,34 s | 0,52 s |
| Una página de testimonio | unos 6 s | al momento |

Qué se ha cambiado:

1. **Plano del barco**: va ya dibujado en la ROM (comprimido) y se vuelca a la pantalla. El fondo es el que deja el CLS de cada máquina, igual que el original: negro en MSX1 y azul en el HB-F900.
2. **Textos de testimonios y registros**: salen de golpe en vez de letra a letra. Al llenarse la ventana se sigue esperando el ESPACIO.
3. **Todo PRINT#1 en la pantalla gráfica** pasa por una rutina propia, con el gancho H.OUTD. La del HB-20P dibuja punto a punto y tarda unos 13 ms por letra.
4. **Borrado de ventanas, raya roja y columna**: son rutinas propias en lugar de LINE...BF, y las elecciones de orden se hacen con un solo `ON INSTR(...) GOTO` en vez de 13 IF seguidos.
5. **Caras y dibujos de sala** (rutinas de MSA): su WRTVRM de la BIOS pasa a uno rápido, puesto en el hueco de la rutina USR(6), que solo se usa al empezar.

Las rutinas imitan a las de la BIOS que usaba el BASIC (SETC, NSETCX, GRPPRT), así que la pantalla queda igual. Lo comprobé así:

- En el HB-20P la VRAM queda idéntica byte a byte a la de la arreglada lenta después de cada orden probada.
- En la partida entera de la guía, las 205 capturas salen iguales a las de la versión lenta.

**El reloj de Turning no cambia**: el bucle de espera de tecla (líneas 510-530) es el mismo. Sube 3,55 por minuto, frente a 3,57 en la versión lenta, así que Turning sigue apareciendo a las 3 h y pico de espera.

## Cómo se usa

- Al encender sale la pantalla de título con **«¿JUEGO O TEST? (J/T)»**, como en el disco francés. J empieza la investigación y T el test de evaluación. Para hacer el test después de jugar, reinicia y pulsa T.
- La pregunta «¿DESEAS CARGAR EL TRANSCURSO DE TU INVESTIGACIÓN?» y la tecla £ (grabar) siguen usando la **cinta** (fichero ETAT), igual que en el original.
- Exige 64 KB de RAM, como la cinta.

## Probado

En openMSX: Sony HB-20P (MSX1) y Sony HB-F900 (MSX2 con dos disqueteras). La partida entera de la guía, sin tocar la memoria: los testimonios, SESAMO, la maleta (mal y bien), el frigorífico, el morse, Turning tras la espera, la avería del ascensor y el test 15/15. El mapper sale ASCII16 en openMSX y en BlueMSX.

## Cómo está hecha

Todo esto está en `rom/`:

- `cartucho.asm` (banco 0): engancha H.STKE, pinta el título (lo que hacía ENTETE), pregunta J/T y teclea en el búfer del teclado `CLEAR9,&HCFFF:?USR9(6):RUN20010`. La orden no se ve. Así, en máquinas con disco, no se pisa la RAM de 8000h, donde está el código que llama a H.STKE.
- `USR9` es una rutina de 12 bytes en DDF3h, entre el final de MSA y NU, que llama al cartucho con CALSLT. USR9(6) ejecuta TRIMMS desde la RAM y copia el programa ya tokenizado a 8001h. USR9(3) carga MSA y USR9(10+n) carga el testimonio n. La copia entre bancos se hace con una rutina copiada a BUF (F55Eh).
- `basic_rom.py` junta MSA2 (renumerado +20000) con MSA3 en un solo programa y cambia los `BLOAD"CAS:..."` por `USR9`. `tokeniza_rom.py` lo tokeniza. Comprobé con el MSX-BASIC real de openMSX que los cuatro programas salen idénticos byte a byte.
- `rapida.asm` (solo en la rápida) tiene las rutinas nuevas. El plano comprimido se saca de la ROM publicada en `releases/`. También se puede rehacer: `tools/captura_plano.py` captura la VRAM en openMSX tras dibujar el plano con el BASIC original de la ROM arreglada, y `build_rom.py --plano vram_plano.bin` la comprime.
- `python3 build_rom.py ladoA.cas ladoB.cas` rehace la ROM desde la cinta original (pasmo). Los programas BASIC, el código de las rutinas y los testimonios salen de la cinta de quien la monta; en el repositorio no hay nada del original.

Licencias: ver el README.
