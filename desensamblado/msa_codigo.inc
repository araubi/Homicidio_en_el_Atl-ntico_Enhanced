; ---------------------------------------------------------------------------
;  RUTINAS USR DE "MSA" (BD00h-BF1Bh)
;  El BASIC las llama con DEFUSR=&HBD00 : A=USR(V), V entero (DEFINT V-Z).
;  El argumento entero queda en DAC+2 (F7F8h).
;  Parametros por la "ventana" NU=DE00h (2 bytes); VE=DE02h son las 51
;  banderas del juego (ver ANALISIS.md).
; ---------------------------------------------------------------------------
DAC2    equ 0F7F8h      ; argumento de USR (entero)
EXPTBL0 equ 0FCC1h      ; slot de la BIOS (pagina 0)
ENASLT  equ 0024h
WRTVRM  equ 004Dh
FILVRM  equ 0056h
NU      equ 0DE00h      ; NU   : puente (Y1) / numero de persona / sala...
NU1     equ 0DE01h      ; NU+1 : columna (X1) / dibujo / codigo de registro

        org 0BD00h
; --- Despachador: salta a la rutina numero DAC2 de TABLA_USR -----------------
; Codigo automodificable: escribe el desplazamiento 2*n y 2*n+1 en las dos
; instrucciones LD L,(IX+d) / LD H,(IX+d).
USR:    ld a,(DAC2)
        add a,a
        ld ix,TABLA_USR
        ld (USR_D1+2),a
        inc a
        ld (USR_D2+2),a
USR_D1: ld l,(ix+0)
USR_D2: ld h,(ix+0)
        jp (hl)
TABLA_USR:
        dw USR0_CARA      ; 0: dibuja la cara de la persona PEEK(NU) (1..40)
        dw USR1_BORRACARA ; 1: borra el recuadro de la cara
        dw USR2_SALA      ; 2: que sala hay en (puente NU, columna NU+1)
        dw USR3_OCUPANTE  ; 3: quien/que hay en (puente NU, columna NU+1)
        dw USR4_DIBUJO    ; 4: dibuja la sala numero PEEK(NU+1) (64x64)
        dw USR5_BORRASALA ; 5: borra el recuadro de la sala
        dw USR6_INICIO    ; 6: busca la RAM de la pagina 1 (dibujos de TRIMMS)

; --- USR 2: sala de la casilla (Y1,X1) ---------------------------------------
; TABLA_SALAS: una lista por puente (A=1.. M=13), cada una terminada en FFh:
;   X0 = primera columna, y luego entradas:
;   tt dd        -> 1 casilla de tipo tt (nombre n.tt de la linea 1010) y dibujo dd
;   8n tt dd     -> n+1 casillas iguales
; Devuelve NU=tipo de sala y NU+1=dibujo (0,0 si no hay nada).
USR2_SALA:
        ld hl,NU
        ld a,0Eh
        sub (hl)                ; 14-Y1 = listas que hay que saltar
        ld hl,TABLA_SALAS
        ld b,a
U2_SALTA:
        ld a,(hl)
        inc hl
        cp 0FFh
        jr nz,U2_SALTA
        djnz U2_SALTA
        ld a,(NU1)
        cp (hl)
        jr c,U2_NADA            ; columna anterior al principio del puente
        sub (hl)
U2_BUCLE:
        ld b,a
        inc hl
        ld c,(hl)
        bit 7,c
        jr nz,U2_TRAMO
        ld b,a                  ; casilla suelta
        dec a
        jr z,U2_HALLADA
        inc hl
        jr U2_BUCLE
U2_TRAMO:
        ld a,0FFh
        cp (hl)
        jr z,U2_NADA            ; fin de la lista del puente
        res 7,c
        ld a,b
        inc c
        sub c
        inc hl
        jp m,U2_HALLADA
        jr z,U2_HALLADA
        inc hl
        jr U2_BUCLE
U2_NADA:
        xor a
        ld (NU),a
        ld (NU1),a
        ret
U2_HALLADA:
        jp DEVUELVE_HL

; --- USR 0: cara de la persona PEEK(NU) ---------------------------------------
; 40 caras de 160 bytes: 4x5 caracteres (32x40 pixeles), guardadas por filas de
; caracteres: 8 lineas x 4 bytes. En CARAS. Se copian a la tabla de patrones (VRAM 0D28h: fila 13,
; columna 5) con WRTVRM.
USR0_CARA:
        ld hl,CARAS
        ld a,(NU)
        dec a
        and a
        jr z,U0_YA
        ld b,a
        ld de,160
U0_MULT:
        add hl,de
        djnz U0_MULT
U0_YA:  ld de,0D28h
        ex de,hl                ; DE=datos, HL=VRAM
        ld b,5                  ; 5 filas de caracteres
U0_FILA:
        push bc
        push hl
        ld b,8                  ; 8 lineas por caracter
U0_LINEA:
        push bc
        push hl
        ld b,4                  ; 4 caracteres de ancho
U0_CAR: push bc
        ld a,(de)
        call WRTVRM
        inc de
        ld bc,8
        add hl,bc
        pop bc
        djnz U0_CAR
        pop hl
        inc hl
        pop bc
        djnz U0_LINEA
        pop hl
        inc h                   ; siguiente fila de caracteres (+256)
        pop bc
        djnz U0_FILA
        ret

; --- USR 1: borra el recuadro de la cara (5 x 32 bytes de patrones a 0) -------
USR1_BORRACARA:
        ld hl,0D28h
        ld b,5
U1_FILA:
        push bc
        push hl
        ld bc,32
        xor a
        call FILVRM
        pop hl
        inc h
        pop bc
        djnz U1_FILA
        ret

; --- USR 4: dibuja la sala n.PEEK(NU+1) ---------------------------------------
; Los dibujos estan comprimidos en la RAM de la pagina 1 (4000h-75FEh), donde
; los dejo TRIMMS. Se conecta esa RAM, se descomprime a patrones (VRAM 0BB0h)
; y colores (2BB0h) y se vuelve a poner la BIOS/BASIC.
; Formato: columnas, filas (en caracteres), y parejas (valor, repeticiones) para
; patrones y despues para colores.
USR4_DIBUJO:
        ld a,(SLOT_RAM1)
        ld hl,4000h
        call ENASLT
        ld ix,TABLA_DIBUJOS
        ld a,(NU1)
        dec a
        add a,a
        ld (U4_D1+2),a          ; automodificable: indice en TABLA_DIBUJOS
        inc a
        ld (U4_D2+2),a
U4_D1:  ld e,(ix+0)
U4_D2:  ld d,(ix+0)
        ld a,(de)
        ld (N_COLS),a
        inc de
        ld a,(de)
        ld (N_FILAS),a
        ld hl,0BB0h             ; patrones: fila 11, columna 22 (x=176,y=88)
        call DESCOMPRIME
        dec de
        dec de
        ld hl,0BB0h
        ld a,h
        or 20h                  ; colores: 2BB0h
        ld h,a
        call DESCOMPRIME
        ld a,(EXPTBL0)
        ld hl,4000h
        call ENASLT             ; devuelve el BASIC a la pagina 1
        ret
DESCOMPRIME:
        inc de
        ld a,(de)
        ld (VALOR),a
        inc de
        ld a,(de)
        ld (CUENTA),a
        ld a,(N_COLS)
        ld b,a
DC_COLUMNA:
        push bc
        push hl
        ld a,(N_FILAS)
        ld b,a
DC_FIL: push bc
        push hl
        ld b,8
DC_BYTE:
        ld a,(VALOR)
        call WRTVRM
        inc hl
        ld a,(CUENTA)
        dec a
        call z,DC_OTRA
        ld (CUENTA),a
        djnz DC_BYTE
        pop hl
        inc h
        pop bc
        djnz DC_FIL
        pop hl
        ld bc,8
        add hl,bc
        pop bc
        djnz DC_COLUMNA
        ret
DC_OTRA:
        inc de
        ld a,(de)
        ld (VALOR),a
        inc de
        ld a,(de)
        ret

; --- USR 5: borra el recuadro de la sala (8 filas x 64 bytes de colores a FFh)-
USR5_BORRASALA:
        ld hl,0BB0h
        ld a,20h
        or h
        ld h,a
        ld b,8
U5_FILA:
        push bc
        push hl
        ld bc,64
        ld a,0FFh
        call FILVRM
        pop hl
        inc h
        pop bc
        djnz U5_FILA
        ret

; --- USR 3: que hay en (Y1,X1) -------------------------------------------------
; TABLA_OCUPANTES: entradas de 4 bytes (Y, X, b2, b3) hasta FFh.
;   b3 >= 40h : b3b2 es la direccion de un texto de registro -> NU,NU+1 = dir.
;   b3 <  40h : NU = persona (1-40, o 99 = registro especial) y
;               NU+1 = codigo de registro especial (1-13, 0 = ninguno).
USR3_OCUPANTE:
        ld hl,TABLA_OCUPANTES
        ld bc,4
U3_BUCLE:
        ld a,(NU)
        cp (hl)
        jr z,U3_PUENTE
        ld a,0FFh
        cp (hl)
        jp z,U2_NADA
        add hl,bc
        jr U3_BUCLE
U3_PUENTE:
        inc hl
        ld a,(NU1)
        cp (hl)
        inc hl
        jr z,U3_HALLADA
        inc hl
        inc hl
        jr U3_BUCLE
U3_HALLADA:
        inc hl
        ld a,(hl)
        dec hl
        cp 40h
        jr c,DEVUELVE_HL
        ld (NU),a               ; texto: NU = byte alto, NU+1 = byte bajo
        ld a,(hl)
        ld (NU1),a
        ret
DEVUELVE_HL:                    ; NU,NU+1 = (HL),(HL+1)
        ld (DH_LD+2),hl         ; automodificable
DH_LD:  ld de,(0)
        ld (NU),de
        ret

; --- USR 6: busca en que slot hay RAM en la pagina 1 --------------------------
; Igual que la rutina de TRIMMS. Prueba los slots 0-3 y subslots 0-3
; escribiendo el complemento en 4000h. Si no hay RAM, RST 0 (reinicia).
USR6_INICIO:
        di
        xor a
        call BUSCA_RAM
        ld a,(EXPTBL0)
        ld hl,4000h
        call ENASLT
        ei
        ret
BUSCA_RAM:
        ld (B_SLOT),a
        ld c,a
        xor a
BR_SUB: ld (B_SUBSLOT),a
        add a,a
        add a,a
        ld b,a                  ; subslot * 4
        ld a,c
        ld (BR_IX+2),a          ; automodificable: EXPTBL+slot
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
        cp (hl)
        cpl
        ld (hl),a
        ret z                   ; es RAM
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
VALOR:      db 0
CUENTA:     db 0
N_COLS:       db 0
N_FILAS:      db 0
            db 0,0
