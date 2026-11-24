; TRIMMS (cinta, cara A; MSA1 lo pide como "TRIMMSA"): dibujos de las salas
; Se carga en 9000h y copia 35FFh bytes de dibujos comprimidos a la RAM de la
; pagina 1 (4000h-75FEh), donde los lee la rutina USR 4 de MSA. Exige 64 KB.
; Desensamblado: Claude para araubi (2026). Datos: build.py los saca de la cinta.
EXPTBL0 equ 0FCC1h
ENASLT  equ 0024h
        org 9000h
        di
        xor a
        call BUSCA_RAM          ; conecta en la pagina 1 el primer slot con RAM
        ld hl,DIBUJOS
        ld de,4000h
        ld bc,35FFh
        ldir
        ld a,(EXPTBL0)
        ld hl,4000h
        call ENASLT             ; vuelve a poner el BASIC
        ei
        ret
BUSCA_RAM:                      ; casi la misma rutina que USR 6 de MSA
        ld (B_SLOT),a
        ld c,a
        xor a
BR_SUB: ld (B_SUBSLOT),a
        add a,a
        add a,a
        ld b,a
        ld a,c
        ld (BR_IX+2),a          ; automodificable
        ld ix,EXPTBL0
BR_IX:  ld a,(ix+0)
        or c
        or b
        ld (SLOT_RAM1),a
        push bc
        ld hl,4000h
        call ENASLT
        pop bc
        ld hl,4000h
        ld a,(hl)
        cpl
        ld (hl),a
        cp (hl)                 ; (a diferencia de MSA, aqui no se repone el byte)
        ret z
        ld a,(B_SUBSLOT)
        inc a
        cp 4
        jr c,BR_SUB
        ld a,(B_SLOT)
        inc a
        cp 4
        jr c,BUSCA_RAM
        ei
        rst 0
B_SLOT:     db 0
B_SUBSLOT:  db 0
SLOT_RAM1:  db 0
; 27 dibujos de sala comprimidos (ver graficos.py)
DIBUJOS:
        incbin "trimms_dibujos.bin"
