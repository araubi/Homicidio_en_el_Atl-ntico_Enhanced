; ENTETE (cinta, cara A): pantalla de presentacion de "Homicidio en el Atlantico"
; Se carga en 9000h con BLOAD"CAS:ENTETE",R desde MSA1.
; Desensamblado: Claude para araubi (2026). Datos: build.py los saca de la cinta.
CHGMOD  equ 005Fh
DISSCR  equ 0041h
ENASCR  equ 0044h
WRTVRM  equ 004Dh
        org 9000h
        ld a,2
        call CHGMOD             ; SCREEN 2
        call DISSCR             ; apaga la pantalla mientras dibuja
        ld ix,DATOS             ; parejas (valor, repeticiones); 0 repeticiones = fin
        ld hl,0000h
        call VUELCA             ; tabla de patrones (los 3 tercios)
        ld hl,2000h
        call VUELCA             ; tabla de colores
        ld hl,0E020h
        ld (0F69Fh),hl          ; ?? deja E020h en F69Fh (zona de variables del BASIC)
        call ENASCR
        ret
VUELCA: ld a,(ix+1)
        and a
        jr z,VU_FIN
        ld b,a
VU_REP: ld a,(ix+0)
        call WRTVRM
        inc hl
        djnz VU_REP
        inc ix
        inc ix
        jr VUELCA
VU_FIN: inc ix
        inc ix
        ret
; 903Dh-90FFh: restos de memoria sin uso (se guardan tal cual)
        incbin "entete_resto.bin"
DATOS   equ 9100h
