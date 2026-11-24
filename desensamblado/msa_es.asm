; MSA.BIN de la cinta en castellano - Homicidio en el Atlantico (MSX)
; Juego: Cobra Soft (Bertrand Brocard, Marie-Anne Alison), Infogrames 1985-87.
; Desensamblado y comentarios: araubi con Claude (2026), CC BY-NC-SA 4.0.
; Solo el codigo es nuestro. Los datos del juego (caras, textos y tablas) no se
; publican: build.py los saca de la cinta del usuario a msa_*.bin.
        include "msa_codigo.inc"

; --- Punteros a los 27 dibujos de sala (RAM de la pagina 1, cargados por TRIMMS)
; 27 palabras: direccion de cada dibujo comprimido (4000h-75FEh).
TABLA_DIBUJOS:
        incbin "msa_dibujos.bin"        ; 54 bytes

; --- 40 caras de 160 bytes (persona 1-40): 4x5 caracteres (32x40 puntos),
; guardadas por filas de caracteres, 8 lineas x 4 bytes. Ver USR0_CARA.
CARAS:
        incbin "msa_caras.bin"          ; 6400 bytes

; --- Tabla de ocupantes: entradas de 4 bytes (puente 1=M..13=A, columna, b2, b3)
; hasta FFh. Ver USR3_OCUPANTE.
TABLA_OCUPANTES:
        incbin "msa_ocupantes.bin"      ; 249 bytes

; --- Textos de registro (terminan en 02h), D915h-DBEBh
TEXTOS:
        incbin "msa_textos.bin"         ; 727 bytes

; --- Tabla de salas: una lista por puente (la 0 no se usa), ver USR2_SALA.
; Cada lista: columna inicial y entradas "tt dd" o "8n tt dd"; FFh al final.
TABLA_SALAS:
        incbin "msa_salas.bin"          ; 519 bytes (con el relleno final)
