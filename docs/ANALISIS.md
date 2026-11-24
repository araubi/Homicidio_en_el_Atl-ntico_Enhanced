# Homicidio en el Atlántico (MSX): análisis técnico

Juego de Cobra Soft (guion de Bertrand Brocard, gráficos de Marie-Anne Alison) publicado por Infogrames: *Meurtres sur l'Atlantique* (1985-86), en MSX en disco francés, cinta española (1987) y disco alemán (1987). Análisis hecho por araubi con Claude el 5-11-2026 sobre la cinta española de FERPECT, comparada con los dos discos.

## 1. Cómo está hecho

Casi todo el juego es **MSX-BASIC grabado en ASCII** (los listados se leen tal cual en la cinta), con unas pocas rutinas en código máquina para lo que el BASIC no puede hacer rápido.

| Fichero (cinta A) | Tipo | Carga en | Qué hace |
|---|---|---|---|
| MSA1 | BASIC ASCII | | `CLEAR 20,&H8FFF`, carga ENTETE y TRIMMS, salta a MSA2 |
| ENTETE | binario `,R` | 9000h | descomprime la pantalla de título a la VRAM (SCREEN 2) |
| TRIMMS | binario `,R` | 9000h | copia 35FFh bytes de dibujos comprimidos a la **RAM de la página 1** (4000h-75FEh) |
| MSA2 | BASIC ASCII | | dibuja el plano del barco con LINE/PSET y DATA (en disco es BATVER.XXX, una copia de la VRAM) |
| MSA3 | BASIC ASCII | | el juego |
| MSA | binario | BD00h-DDF2h | rutinas USR, 40 caras, tablas de salas y ocupantes, textos de registro |
| TEST | BASIC ASCII | | test final, se carga a mano con `RUN"CAS:TEST"` |
| TEM1…TEM40 (cara B) | binario | B91Fh | un testimonio por personaje |

Por TRIMMS el juego **exige 64 KB**: el BASIC no ve la página 1 de RAM, y USR(4) la conecta con ENASLT para leer cada dibujo y después vuelve a poner el BASIC. USR(6) busca al empezar en qué slot y subslot hay RAM en 4000h.

### Memoria

| Zona | Uso |
|---|---|
| 4000h-75FEh (RAM de página 1, oculta) | 27 dibujos de sala comprimidos |
| 9000h-… | ENTETE y TRIMMS (solo durante la carga) |
| B91Fh | número del testimonio que está cargado (para no volver a leer la cinta) |
| B920h-BCFFh | testimonio cargado |
| BD00h-BF1Bh | rutinas USR |
| BF1Ch-DDF2h | 40 caras de 160 bytes, tablas de salas y ocupantes y textos de registro |
| D81Ch | tabla de ocupantes (4 bytes por entrada: puente, columna, persona, código de registro) |
| DBECh | tabla de salas (una lista por puente) |
| DE00h-DE01h (NU) | parámetros de las USR |
| DE02h-DE34h (VE) | las 51 banderas del juego; es lo que graba `£` en el fichero ETAT |

### Rutinas USR (`DEFUSR=&HBD00`, `A=USR(V)`)

El despachador es automodificable: escribe 2·V y 2·V+1 como desplazamientos de dos `LD L,(IX+d)` / `LD H,(IX+d)` y salta.

| V | Rutina | Entrada → salida |
|---|---|---|
| 0 | dibuja la cara de la persona PEEK(NU) | 1-40 |
| 1 | borra el recuadro de la cara | |
| 2 | sala en (puente NU, columna NU+1) | NU = tipo de sala (índice en los DATA 1010-1070), NU+1 = dibujo (9 = sala prohibida sin palabra clave, 0 = sin dibujo) |
| 3 | ocupante de (puente, columna) | NU = persona (1-40), 99 = registro especial sin persona, o ≥41 = dirección alta de un texto de registro; NU+1 = código de registro (1-13) o dirección baja |
| 4 | dibuja la sala PEEK(NU+1) | RLE por columnas: valor, repeticiones; primero patrones (VRAM 0BB0h) y luego colores (2BB0h) |
| 5 | borra el recuadro de la sala | |
| 6 | busca la RAM de la página 1 | guarda el slot en SLOT_RAM1 |

Las tablas de salas usan entradas `tt dd` (una casilla) y `8n tt dd` (n+1 casillas iguales) a partir de la primera columna de cada puente. `tools/barco.py` las recorre igual que la rutina y saca `mapa_barco.txt`.

## 2. El barco

- 13 puentes, de A (arriba, Y1=13) a M (abajo, Y1=1). La letra es `CHR$(78-Y1)`.
- Te mueves por columnas con ←/→ y solo por pasillo: el juego mira si el punto del plano es blanco (`POINT(...)=15`).
- **Escalera**: solo en la columna 64 y solo entre los puentes E y J (↑/↓).
- **Ascensores**: columnas 31 (izquierdo) y 76 (derecho). Se llaman con `*` o `$` y se elige el puente con su letra. El derecho, el 10 % de las veces, para un puente más abajo cuando baja. Pulsando I durante el viaje se registra la cabina: en el izquierdo hay una tarjeta de ALTMAN y un casquillo de 7,65; en el derecho una colilla de Marlboro.
- Empiezas en el puente D, columna 25 (sala de baile).

## 3. Órdenes (versión española)

| Tecla | Orden | FR | DE |
|---|---|---|---|
| ←→ ↑↓ | andar / escalera | | |
| D | desfile de las 40 caras | P | P |
| V | ver la sala | V | W |
| M | mirar quién hay | R | S |
| P | preguntar (testimonio) | I | V |
| I | investigar / registrar | F | D |
| E | abrir la caja de los sollados (Turning) | O | O |
| `*` o `$` | ascensor | | |
| £ | grabar la investigación (ETAT) | | |
| A | autopsia (frigorífico), insistir con Altman, avería del ascensor | | |
| F | registrar el cadáver (frigorífico) | | |

## 4. Banderas (VE = DE02h)

`VE+n` (n = 1-40) a 1 quiere decir «la persona n ya habla». Al empezar están a 1 todas menos 3, 6, 11, 12, 14, 18, 24, 31, 33, 34, 35, 36, 37, 38 y 40 (línea 190). Si preguntas antes de tiempo: «¡¡ES DEMASADIO TEMPRANO!!».

| Bandera | Se pone a 1 cuando… |
|---|---|
| 3 (ciego) | contestas BRAILLE al registrar el tiro al blanco (E95) |
| 6 (Greta von Baumann) | lo dice la enfermera (TEM35) |
| 11 (Celestina) | contestas AQUILES al cura, o lo dice Pellton (TEM18) |
| 12 (Marthe Granet) | lo dice el vigilante (TEM23) o registras su oficina (J80, mensaje firmado «M») |
| 14 (Ben Slimane) | lo dice la camarera (TEM8) |
| 18 (Pellton) | registras a Pellton (H71, revólver) |
| 24 (novio de Celestina) | registras a Celestina (H73, cuaderno) |
| 31 (vecina) | registras el cadáver del frigorífico con F (M27) |
| 33 (Marie Vincenot) | lo dice el comisario (TEM30) |
| 34 (Erik Jacobson) | lo dice el groom (TEM39) |
| 35 (enfermera) | lo dice el doctor (TEM16) |
| 36 (Dupuis, radio) | lo dice el comandante (TEM32) |
| 37 (Turning) | pulsas E en los sollados (J88) cuando ya se puede (bandera 42 a 0) |
| 38 (capitán del whisky) | registras la sala de máquinas (M59) |
| 40 (fotógrafo) | registras al fotógrafo (E65) |
| 41 | sin uso |
| 42 | empieza a 1; pasa a 0 cuando el reloj llega a 700 (aviso «TE ACONSEJO REVISAR LOS SOLLADOS») |
| 43 | ascensor derecho arreglado (código 53602) |
| 49 | reloj/3 al grabar |
| 50 | palabra clave SESAMO (dada al comisario): deja ver y registrar las salas prohibidas y el frigorífico |

Cada TEMn termina con dos bytes: código de pregunta (1 = sucesor de San Pedro, 2 = morse, 3 = palabra clave) y la bandera que desbloquea.

## 5. El reloj

- `H` sube 0,001 en cada vuelta de las esperas de tecla (líneas 460 y 510) hasta `HM=700`. En un MSX a 3,58 MHz son unas 60 vueltas por segundo (medí 0,0597 por segundo): **700 son unas 3 h 15 min de espera real**. Solo cuenta el tiempo esperando tecla en el plano o en el ascensor: leer testimonios no suma.
- Con H ≥ 350 (más de hora y media) el ascensor derecho se avería en el siguiente viaje hasta que metes el código. La línea 730, anulada con `'`, ataba la avería a un puente concreto.
- Con H = 700 sale el aviso de los sollados y ya se puede liberar a Turning. Mientras tanto, cerca de J88 se oyen golpes al azar (`PLAY"M800O1L64S3D"`).
- H se graba dividido por 3 en VE+49 (cabe en un byte) y al cargar se multiplica por 3.

## 6. Pruebas con respuesta

| Dónde | Pregunta | Respuesta | Cómo lo comprueba |
|---|---|---|---|
| Cura (E69) | sucesor de San Pedro | AQUILES (7 teclas sin RETURN) | igualdad |
| Tiro al blanco (E95) | papel marrón | BRAILLE | igualdad |
| Camarote de Turning (H72) | combinación de la maleta | ADA | igualdad (pero si fallas dice «CORRECTO...») |
| Comisario (F79) | palabra | SESAMO | igualdad |
| Radio (A77) | ¿escuchar el mensaje? | S | |
| Ascensor averiado | código de funcionamiento | 53602 (`** *   * **   * ` en binario) | `O=536020` |
| TEST | 15 preguntas | ver la solución | **solo la suma de los códigos ASCII** |

El TEST guarda la longitud y la suma ASCII de cada respuesta (así no aparece en el listado). Si la suma no cuadra y la longitud sí, dice «HAY ALGUNOS CARACTERES CORRECTOS». Cualquier anagrama vale.

## 7. Diferencias entre idiomas

Ver VERSIONES.md (ficheros). En resumen:

- Mismo código Z80 y misma lógica BASIC; cambian textos, teclas y los nombres de fichero (`CAS:` en la cinta).
- El francés marca con `*` los objetos que venían de verdad en la caja del juego (sobre, microfilm, telegrama, fotos…). El castellano quita los asteriscos; el alemán los conserva en algunos textos (la maleta).
- El morse: en francés las palabras van sin espacios (SURBOURGOGNE, SOUSLE, NOMDE); en alemán son 11 grupos; en castellano lleva espacios y Ñ (ver CURIOSIDADES).
- El alemán arregla el mensaje del test perfecto y cambia algún tempo del morse.
