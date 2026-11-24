# Homicidio en el Atlántico / Meurtres sur l'Atlantique (MSX): análisis de versiones

Análisis para catalogar las seis imágenes que hay en `FERPECT MSX`. Las comparé fichero a fichero (cabeceras, listados BASIC detokenizados, binarios y textos). Hecho el 5-11-2026 por araubi con Claude.

## Resumen

| # | Fichero en FERPECT | Formato | Idioma real | Contenido |
|---|---|---|---|---|
| 1 | `Homicidio en el Atlantico (1987)(Cobra Soft, Infogrames)(Side A)(ES)[!][RUN'CAS-'][v0.8.4b].tsx` | TSX (makeTSX 0.8.4b) | castellano | cara A: juego + test |
| 2 | `Homicidio en el Atlantico (1987)(Cobra Soft, Infogrames)(Side B)(ES)[!][RUN'CAS-'][v0.8.4b].tsx` | TSX | castellano | cara B: los 40 testimonios |
| 3 | `Meurtres sur l'Atlantique. Murder on the Atlantic. Homicidio en el Atlantico (1987)(Infogrames)(FR)(es)(Side A)(Game)[!].cas` | CAS | castellano | mismos datos que el TSX 1 |
| 4 | `Meurtres sur l'Atlantique. Murder on the Atlantic. Homicidio en el Atlantico (1987)(Infogrames)(FR)(es)(Side B)(Testimonies)[!].cas` | CAS | castellano | mismos datos que el TSX 2 |
| 5 | `Meurtres sur l'Atlantique. Murder on the Atlantic (1986)(Infogrames)(FR).dsk` | DSK 720 KB | francés | versión original en disco |
| 6 | `Meurtres sur l'Atlantique. Murder on the Atlantic (1986)(Infogrames)(FR)(de).dsk` | DSK 720 KB | **alemán** | traducción alemana en disco, cargador neerlandés |

En la práctica son **tres versiones distintas** (castellano en cinta, francés en disco, alemán en disco). Las cuatro imágenes de cinta son la misma cinta en dos formatos.

## Huellas

| # | Bytes | CRC32 | MD5 | SHA1 |
|---|---|---|---|---|
| 1 | 50316 | 339e7eac | 49dd530b8cca7a35ff3ed551a2b21799 | 88b1854098a68f616431a8d1af6d9e3b9fa2e098 |
| 2 | 19569 | d6a00649 | 7457198ee16f54037c2c76522bafe85e | 16d44eea4d15824249ca64fd87a7cc62071b0b62 |
| 3 | 49312 | 8f3a8e5f | d67264de4484af6704e29814827e0816 | 38ac8aa8d9837200f5cb7feb00db4b62b3448887 |
| 4 | 18727 | a0967b4a | 84495ca438cc3815a58448dd41bc8c62 | d4a2957453debe1d641c3b42ac88f066867c1a3f |
| 5 | 737280 | 331c6be5 | 13cd73a6540592dd75f7c5e9ad5da204 | cbf401ff589538d348420b32f3908fab0b43ede2 |
| 6 | 737280 | b88b669c | ed04c8449a3c118edc08ed170c8660f1 | 09981858b81e01d2da62543e0d45c7ffd583c54f |

## 1-4. Cinta española (Cobra Soft / Infogrames, 1987)

- **CAS y TSX llevan exactamente los mismos ficheros**, byte a byte. El TSX solo añade los datos de pulsos y los metadatos de makeTSX («TSX.RIPPER», «TOSEC.NAME»...). `build.py` del desensamblado rehace las dos CAS idénticas.
- Cara A: `MSA1` (ASCII, cargador) → `ENTETE` (bin, pantalla de título) → `TRIMMS` (bin, dibujos de salas; el programa pide «TRIMMSA» y la cinta solo mira 6 letras) → `MSA2` (ASCII, dibuja el plano) → `MSA3` (ASCII, juego) → `MSA` (bin, rutinas en BD00h) → `TEST` (ASCII, test de evaluación, se carga aparte con `RUN"CAS:TEST"`).
- Cara B: `TEM1` … `TEM40` (bin), un testimonio por personaje, en orden. Cuando interrogas a alguien el juego busca su TEMn en la cara B.
- **Todo el contenido es castellano**: textos de juego, testimonios, test y título «HOMICIDIO EN EL ATLANTICO». El título lleva los logos de Infogrames y Cobra Soft. No hay ni un texto francés que el jugador vea (solo los REM del programador, en francés).
- No hay protección: el lado A de 49312 bytes no tiene bloques raros ni cargador de turbo.
- Exige **64 KB**: TRIMMS deja los dibujos de las salas en la RAM de la página 1 (4000h-7FFFh) y la rutina USR(6) la busca por slots.

**Catalogación**: las CAS (3 y 4) están marcadas `(FR)(es)`, como si fueran francesas con castellano, y en realidad son solo castellano. Propongo nombres coherentes con los TSX:

- `Homicidio en el Atlantico (1987)(Cobra Soft, Infogrames)(ES)(Side A)(Game)[!].cas`
- `Homicidio en el Atlantico (1987)(Cobra Soft, Infogrames)(ES)(Side B)(Testimonies)[!].cas`

Las dos CAS pueden ir a ALT si el TSX es la representativa (son la misma cinta), o al revés. El `[!]` es correcto en las cuatro: el juego carga y se termina entero (lo comprobé jugando).

## 5. Disco francés (Infogrames 1986)

- Ficheros: `AUTOEXEC.BAS` → `MEURTRE.BAS` (menú «Jeu ou Test ?»), `DISQUE.BAS` (juego, equivale a MSA3), `TEST.BAS`, `ENTETE.BIN` (título «MEURTRES SUR L'ATLANTIQUE»), `MSA.BIN`, `TRIMMSA.BIN`, `BATVER.XXX`, `ETAT.BIN` y `TEM1.BIN` … `TEM40.BIN`, más **`TEM1O.BIN`** (con letra O), copia exacta de TEM10.
- `MEURTRE.BAS` empieza con `3 ' PISANT & MEGA SOFT!` y `7 POKE&HFFFF,((PEEK(&HFFFF)XOR&HFF)AND&HF0)*1.0625!`. Esa línea 7 copia los subslots de las páginas 2-3 a las páginas 0-1. No es de Infogrames: es el arreglo de quien pasó el juego a disco (o lo crackeó) para máquinas con slots expandidos.
- `BATVER.XXX` es una copia de la VRAM (`BLOAD ,S`) con el plano del barco ya dibujado: sustituye a MSA2.
- Los testimonios se cargan con `BLOAD ...,&H2920`: en el disco están grabados desde otra dirección y se recolocan.
- El juego usa teclas francesas: P (preguntar), V, R, I, F, O (sí)...
- Su `ETAT.BIN` es una partida guardada de alguien: tiene desbloqueada la radio (bandera 36) y el reloj a 6.
- Año: el título y el nombre lo dan como 1986 (Cobra Soft sacó el juego en 1985-86 en otros sistemas).

**Catalogación**: el nombre actual es correcto. «Murder on the Atlantic» es solo el título alternativo: no hay textos en inglés.

## 6. Disco alemán, marcado «(FR)(de)»

- **Es una traducción completa al alemán**, no una versión francesa con algo de alemán: textos de juego, 40 testimonios, test («Spiel o. Test ?», «SIE HABEN ... RICHTIGE ANTWORT(EN)»).
- La pantalla de título dice **«MURDER ON THE ATLANTIC»** (en inglés) con los logos de Cobra Soft e Infogrames. Es una copia de la VRAM (16391 bytes, `BLOAD ,S`), no el ENTETE comprimido del francés.
- Cargador propio en neerlandés: `AUTOEXEC.BAS` → `ATLANTIC.BAS` con `'ON DISK BY "MINIC" COMPUTING 18-3-1987` y los rótulos «ATLANTIC WORDT GELADEN» y «1987 M.C. Even geduld s.v.p» («cargando», «un momento, por favor»). Después `ATLANTIC.` (menú) → `DISQUE.` (juego) y `TEST.`
- `TRIMMSA.BIN` es idéntico al francés. `MSA.BIN` tiene el mismo código con los textos de registro en alemán.
- Lleva el mismo `TEM1O.BIN` **francés** de sobra (copiado del disco francés; el TEM10 sí está en alemán).
- Teclas alemanas: P, W, S, V, D, O... y J (ja) para cargar partida.
- Su ETAT.BIN está a cero (sin partida; el reloj a 12).
- Arregla el fallo del test: añade `IF R=15 THEN GOSUB 320` para que salga el mensaje de test perfecto (en FR y ES nunca sale).

**Catalogación**: propongo cambiar `(FR)(de)` por `(DE)`, añadir el título del disco y dejar constancia del distribuidor:

- `Murder on the Atlantic (1987)(Cobra Soft, Infogrames)(DE)(MINIC Computing)[!].dsk`

O, si se prefiere mantener el título francés principal: `Meurtres sur l'Atlantique. Murder on the Atlantic (1987)(Infogrames)(DE)[!].dsk`. La fecha del disco es 18-3-1987.

## Ficheros internos comparados

| Fichero | ES (cinta) | FR (disco) | DE (disco) |
|---|---|---|---|
| MSA (rutinas) | 8435 b, crc b58f046e | 8448 b, crc a9d06b99 | 8448 b, crc 29ec1535 |
| TRIMMS(A) | 13937 b, crc b4ab4ac8 | 13952 b, crc 0be561c9 | = FR |
| ENTETE | 7446 b comprimido | 6080 b comprimido (otro formato) | 16391 b copia de VRAM |
| Plano | MSA2 (BASIC que lo dibuja) | BATVER.XXX 14344 b | BATVER.XXX: mismo dibujo, 8 bytes distintos en 37F9h-3800h (patrón de un sprite) |
| TEM1O.BIN | no existe | = TEM10 (francés) | = TEM10 francés |

El código Z80 de MSA es el mismo en los tres idiomas; cambian los textos y las tablas que dependen de ellos (las tres variantes se reensamblan idénticas desde el mismo `msa_codigo.inc`). Los TEM de la cinta y del disco no tienen el mismo formato de cabecera (dirección de carga distinta), pero sí la misma estructura: texto, código de pregunta y bandera.

## Qué falta en la colección

- No hay cinta francesa ni versión de disco en castellano. Existió la cinta francesa de Infogrames (y versiones para Amstrad CPC, Thomson, etc.); si aparece, la cara A debería parecerse mucho a esta española.
- No hay versión en inglés pese al título del disco alemán.
