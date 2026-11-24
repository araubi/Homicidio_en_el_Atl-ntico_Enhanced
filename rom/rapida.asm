; --- Version rapida: rutinas que sustituyen a las partes lentas del BASIC ----
; araubi con Claude (2026), MIT. Se incluye al principio de USR9 (cartucho.asm).
;   USR9(0)  = GOSUB 420 (raya + GOSUB 430)
;   USR9(1)  = GOSUB 430 (borra sala, cara y ventana de texto)
;   USR9(2)  = texto del testimonio desde B920h; devuelve cuantos bytes imprimio
;   USR9(4)  = texto de registro desde la direccion PEEK(NU)*256+PEEK(NU+1)
;   USR9(5)  = LINE(16,152)-(256,192),1,BF
;   USR9(8)  = plano del barco (lineas 20045-20220 del MSA2 original)
;   USR9(9)  = LINE(16,160)-(256,192),1,BF
;   USR9(10) = cambia en MSA las llamadas a WRTVRM por una version rapida
;   USR9(512+X1) = linea 396: "COL. nn" debajo del puente
; Se dibuja con las mismas rutinas de la BIOS que usa el BASIC (MAPXY, NSETCX,
; SETC, GRPPRT), asi que la VRAM queda igual que con el programa original.
ATRBYT  equ 0F3F2h
MAPXY   equ 0111h
SETC    equ 0120h
NSETCX  equ 0123h
LDIRVM  equ 005Ch
NU      equ 0DE00h
R_CX    equ BUF+0F0h        ; variables (BUF esta libre mientras corre el programa)
R_A     equ BUF+0F2h
R_B     equ BUF+0F3h
R_W     equ BUF+0F4h
R_X     equ BUF+0F6h
R_N     equ BUF+0F8h
R_Y     equ BUF+0FAh

        ei
        ld a,(DAC2+1)
        and a
        jp nz,R_COLUMNA
        ld a,(DAC2)
        and a
        jr z,R_420
        cp 1
        jr z,R_430
        cp 2
        jp z,R_TESTIMONIO
        cp 4
        jp z,R_REGISTRO
        cp 5
        jp z,R_BORRA19
        cp 8
        jp z,R_PLANO
        cp 9
        jp z,R_BORRA20
        cp 10
        jp z,R_PARCHE_MSA
        jp R_SIGUE

; LINE(175,152)-(240,152),8: el BASIC la pinta punto a punto (SETC)
R_RAYA: ld a,8
        ld (ATRBYT),a
        ld hl,1300h+168     ; y=152 (fila 19, linea 0), x=168..175: solo el punto 175
        ld c,01h
        call PON_MASC
        ld b,8              ; x=176..239: bytes enteros
        ld hl,1300h+176
RR_1:   push bc
        push hl
        ld c,0FFh
        call PON_MASC
        pop hl
        ld de,8
        add hl,de
        pop bc
        djnz RR_1
        ld c,80h            ; x=240
        jp PON_MASC
R_420:  call R_RAYA
R_430:  ld hl,2BB0h         ; USR(5): colores de la sala a FFh
        ld b,8
R4_1:   push bc
        push hl
        ld bc,64
        ld a,0FFh
        call V_LLENA
        pop hl
        inc h
        pop bc
        djnz R4_1
        ld hl,0D28h         ; USR(1): patrones de la cara a 0
        ld b,5
R4_2:   push bc
        push hl
        ld bc,32
        xor a
        call V_LLENA
        pop hl
        inc h
        pop bc
        djnz R4_2
        call R_BORRA19
        jr R_RAYA

R_BORRA19:
        ld de,152
        ld b,40
        jr RB
R_BORRA20:
        ld de,160
        ld b,32
RB:     ld hl,16
        ld ix,240
        ld a,1
; --- CAJA: LINE BF. HL=x, DE=y, B=filas, IX=ancho, A=color -------------------
; Igual que NSETCX de la BIOS (lo que usa el BASIC), pero rapido: un byte entero
; queda con patron 0 y color 0c; los trozos de byte se dejan a NSETCX.
CAJA:   ld (ATRBYT),a
        ld (R_CX),hl
        ld (R_W),ix
        ld a,l              ; recuadro de caracteres enteros: FILVRM
        or e
        or b
        push ix
        pop hl
        or l
        and 7
        jr nz,CJ_FILA
CJ_BLOQ:push bc
        push de
        ld a,e              ; HL = (y/8)*256 + x
        rrca
        rrca
        rrca
        and 1Fh
        ld h,a
        ld a,(R_CX)
        ld l,a
        push hl
        ld bc,(R_W)
        xor a
        call V_LLENA
        pop hl
        set 5,h
        ld bc,(R_W)
        ld a,(ATRBYT)
        call V_LLENA
        pop hl
        ld de,8
        add hl,de
        ex de,hl
        pop bc
        ld a,b
        sub 8
        ld b,a
        jr nz,CJ_BLOQ
        ret
CJ_FILA:push bc
        push de
        ld hl,(R_CX)
        ld (R_X),hl
        ld hl,(R_W)
        ld (R_N),hl
CJ_BUC: ld hl,(R_N)
        ld a,h
        or l
        jr z,CJ_FIN
        ld a,(R_X)
        and 7
        jr nz,CJ_PARC
        ld bc,8
        or a
        sbc hl,bc
        jr c,CJ_PARC
        ld (R_N),hl
        ld a,e              ; byte entero: HL = (y/8)*256 + (x and F8h) + (y and 7)
        and 7
        ld l,a
        ld a,(R_X)
        and 0F8h
        or l
        ld l,a
        ld a,e
        rrca
        rrca
        rrca
        and 1Fh
        ld h,a
        xor a
        call V_ESCR
        set 5,h
        ld a,(ATRBYT)
        call V_ESCR
        ld hl,(R_X)
        ld bc,8
        add hl,bc
        ld (R_X),hl
        jr CJ_BUC
CJ_PARC:ld a,(R_X)          ; trozo de byte: NSETCX con min(N, 8-(x and 7)) puntos
        and 7
        ld c,a
        ld a,8
        sub c
        ld c,a
        ld b,0
        ld hl,(R_N)
        or a
        sbc hl,bc
        jr nc,CJ_P2
        ld bc,(R_N)
        ld hl,0
CJ_P2:  ld (R_N),hl
        push bc
        push de
        ld hl,(R_X)
        push hl
        add hl,bc
        ld (R_X),hl
        pop bc
        call MAPXY
        pop de
        pop hl
        push de
        call NSETCX
        pop de
        jr CJ_BUC
CJ_FIN: pop de
        inc de
        pop bc
        dec b
        jp nz,CJ_FILA
        ret

; --- PRESET(BC,DE): punto del color de fondo y cursor grafico ----------------
PUNTO:  ld (GRPACX),bc
        ld (GRPACY),de
        call MAPXY
        ld a,(BAKCLR)
        ld (ATRBYT),a
        jp SETC

; --- linea 396 ------------------------------------------------------------------
R_COLUMNA:
        ld hl,80            ; LINE(80,99)-(167,107),1,BF
        ld de,99
        ld b,9
        ld ix,88
        ld a,1
        call CAJA
        ld a,8
        ld (FORCLR),a
        ld bc,84
        ld de,100
        call PUNTO
        ld hl,R_TXTCOL      ; "COL."
        ld b,4
RC_1:   ld a,(hl)
        inc hl
        push hl
        push bc
        call R_LETRA
        pop bc
        pop hl
        djnz RC_1
        ld a,' '            ; PRINT de un numero: espacio, cifras, espacio
        call R_LETRA
        ld a,(DAC2)
        ld c,'0'-1
RC_2:   inc c
        sub 10
        jr nc,RC_2
        add a,10+'0'
        push af
        ld a,c
        cp '0'
        call nz,R_LETRA
        pop af
        call R_LETRA
        ld a,' '
        call R_LETRA
        ld a,15
        ld (FORCLR),a
        ret
R_TXTCOL: db "COL."
; letra en (GRPACX,GRPACY) y avanza 8 puntos
R_LETRA:
        ld hl,(GRPACX)
        push hl
        call GLIFO
        pop hl
        ld de,8
        add hl,de
        ld (GRPACX),hl
        ret

; --- lineas 1560 y 8000-9003: texto del testimonio -------------------------------
R_TESTIMONIO:
        ld hl,0B920h
        ld c,31
        call TEXTO
        ld de,0B920h
        or a
        sbc hl,de
        ld (DAC2),hl
        ret
; --- lineas 1160 y 11000-11006: texto de registro ---------------------------------
R_REGISTRO:
        ld a,(NU)
        ld h,a
        ld a,(NU+1)
        ld l,a
        ld c,2
; TEXTO: imprime desde HL mientras el byte sea > C, en las columnas 2-31 de las
; filas 20-23; con la ventana llena espera el ESPACIO y la borra.
TEXTO:  ld a,2
        ld (R_A),a
        ld a,20
        ld (R_B),a
TX_1:   ld a,c
        cp (hl)
        ret nc              ; byte <= C: fin
        push hl
        push bc
        ld a,(R_A)
        cp 32
        jr c,TX_2
        ld a,2              ; IF A>31 THEN B=B+1:A=2
        ld (R_A),a
        ld hl,R_B
        inc (hl)
TX_2:   ld a,(R_B)
        cp 24
        jr c,TX_4
TX_3:   call CHGET          ; IF B>23: espera el ESPACIO
        cp ' '
        jr nz,TX_3
        call R_BORRA19
        ld a,15
        ld (FORCLR),a
        ld a,20
        ld (R_B),a
        ld a,2
        ld (R_A),a
TX_4:   ld a,(R_A)          ; PRESET(A*8,B*8)
        add a,a
        add a,a
        add a,a
        ld c,a
        ld b,0
        ld a,(R_B)
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        call PUNTO
        pop bc
        pop hl
        ld a,(hl)
        push hl
        push bc
        call GLIFO         ; PRINT#1,CHR$(PEEK(O))
        pop bc
        pop hl
        inc hl
        ld a,(R_A)
        inc a
        ld (R_A),a
        jr TX_1

; --- plano del barco: RLE a la VRAM (patrones y colores de las filas 0-10) -------
; byte n < 128: n bytes literales; n >= 128: n-126 veces el byte siguiente; 0 = fin
R_PLANO:
        ld ix,DATOS_PLANO
        ld de,0000h
        call RLE_VRAM
        ld de,2000h
; colores: la tinta sale de la captura y el fondo se deja el que puso CLS (negro
; en MSX1, azul en el HB-F900: igual que con el programa original)
RLE_COL:ld a,(ix+0)
        inc ix
        and a
        ret z
        cp 128
        jr nc,RC_REP
        ld b,a
RC_L:   ld a,(ix+0)
        inc ix
        call PON_COL
        djnz RC_L
        jr RLE_COL
RC_REP: sub 126
        ld b,a
        ld a,(ix+0)
        inc ix
RC_R:   push af
        call PON_COL
        pop af
        djnz RC_R
        jr RLE_COL
PON_COL:push bc
        and 0F0h
        ld c,a
        ex de,hl
        call V_LEE
        and 0Fh
        or c
        call V_ESCR
        inc hl
        ex de,hl
        pop bc
        ret
RLE_VRAM:
        ld a,(ix+0)
        inc ix
        and a
        ret z
        ld c,a
        ld b,0
        cp 128
        jr nc,RV_REP
        push ix
        pop hl
        add ix,bc
        push ix
        push de
        push bc
        call LDIRVM         ; HL=ROM, DE=VRAM, BC=n
        pop bc
        pop hl
        add hl,bc
        ex de,hl
        pop ix
        jr RLE_VRAM
RV_REP: ld a,c
        sub 126
        ld c,a
        ld a,(ix+0)
        inc ix
        push ix
        push de
        push bc
        ex de,hl
        call V_LLENA         ; HL=VRAM, BC=n, A=byte
        pop bc
        pop hl
        add hl,bc
        ex de,hl
        pop ix
        jr RLE_VRAM

; --- Acceso propio a la VDP (las de la BIOS del HB-20P son muy lentas) ------------
V_DIRW: ld a,l              ; direccion de escritura HL (con DI)
        out (99h),a
        ld a,h
        and 3Fh
        or 40h
        out (99h),a
        ret
V_ESCR: push af             ; WRTVRM: (HL) = A
        di
        call V_DIRW
        pop af
        out (98h),a
        ei
        ret
V_LEE:  di                  ; RDVRM: A = (HL)
        ld a,l
        out (99h),a
        ld a,h
        and 3Fh
        out (99h),a
        ex (sp),hl
        ex (sp),hl
        in a,(98h)
        ei
        ret
V_LLENA:push af             ; FILVRM: HL=dir, BC=cuantos, A=byte
        di
        call V_DIRW
        pop de
VL_1:   ld a,d
        out (98h),a
        dec bc
        ld a,b
        or c
        jr nz,VL_1
        ei
        ret

; --- PON_MASC: los puntos C del byte de patrones HL toman el color ATRBYT -------
; Punto a punto (de izquierda a derecha) con la regla de SETC de la BIOS en SCREEN 2:
;  color = fondo -> se borra el bit;  color = tinta -> se enciende;
;  otro color: se enciende y el byte toma esa tinta, salvo si el byte quedaria
;  lleno (FFh): entonces el bit se borra y el color nuevo pasa a ser el fondo.
PON_MASC:
        ld a,(ATRBYT)
        ld (R_CC),a
        add a,a
        add a,a
        add a,a
        add a,a
        ld (R_C4),a
        call V_LEE
        ld b,a              ; B = patron
        set 5,h
        call V_LEE
        res 5,h
        ld e,a              ; E = color
        ld d,80h            ; D = punto
        push hl
PM_1:   ld a,c
        and d
        jr z,PM_SIG
        ld a,e
        and 0Fh
        ld hl,R_CC
        cp (hl)
        jr z,PM_BORRA
        ld a,e
        and 0F0h
        inc hl              ; R_C4
        cp (hl)
        jr z,PM_PON
        ld a,b
        or d
        inc a
        jr z,PM_LLENO
        dec a
        ld b,a
        ld a,e
        and 0Fh
        or (hl)
        ld e,a
        jr PM_SIG
PM_LLENO:
        ld a,d
        cpl
        ld b,a
        ld a,e
        and 0F0h
        dec hl              ; R_CC
        or (hl)
        ld e,a
        jr PM_SIG
PM_BORRA:
        ld a,d
        cpl
        and b
        ld b,a
        jr PM_SIG
PM_PON: ld a,b
        or d
        ld b,a
PM_SIG: srl d
        jr nz,PM_1
        pop hl
        ld a,b
        call V_ESCR
        set 5,h
        ld a,e
        call V_ESCR
        res 5,h
        ret

; --- GLIFO: como GRPPRT: letra A en (GRPACX,GRPACY) con el color FORCLR ------------
CGPNT   equ 0F91Fh
GLIFO:  ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,(CGPNT+1)
        add hl,de           ; HL = dibujo de la letra (BIOS, pagina 0)
        ld a,(FORCLR)
        ld (ATRBYT),a
        ld a,(GRPACY)
        ld (R_Y),a
        ld b,8
GL_1:   push bc
        push hl
        ld a,(R_Y)
        cp 192
        jr nc,GL_SIG
        ld a,(hl)
        and a
        jr z,GL_SIG
        ld c,a              ; C = parte del byte de la izquierda
        ld e,0              ; E = parte del byte de la derecha
        ld a,(GRPACX)
        and 7
        jr z,GL_3
        ld b,a
GL_2:   srl c
        rr e
        djnz GL_2
GL_3:   push de
        call DIR_XY
        ld a,c
        and a
        call nz,PON_MASC
        pop de
        ld a,e
        and a
        jr z,GL_SIG
        ld a,(GRPACX)
        cp 0F8h
        jr nc,GL_SIG        ; fuera de la pantalla
        ld bc,8
        add hl,bc
        ld c,e
        call PON_MASC
GL_SIG: pop hl
        inc hl
        ld a,(R_Y)
        inc a
        ld (R_Y),a
        pop bc
        djnz GL_1
        ret
DIR_XY: ld a,(R_Y)          ; HL = (y/8)*256 + (x and F8h) + (y and 7)
        and 7
        ld l,a
        ld a,(GRPACX)
        and 0F8h
        or l
        ld l,a
        ld a,(R_Y)
        rrca
        rrca
        rrca
        and 1Fh
        ld h,a
        ret
; --- MSA: USR(6) ya se uso (linea 50); en su sitio (BE8Eh) va un WRTVRM rapido y
; las dos llamadas de MSA (caras en BD8Ah, dibujos de sala en BE13h) pasan a el.
MSA_LIBRE equ 0BE8Eh
R_PARCHE_MSA:
        ld hl,WR_SRC
        ld de,MSA_LIBRE
        ld bc,WR_FIN-WR_SRC
        ldir
        ld hl,HO_SRC        ; gancho H.OUTD: PRINT#1 rapido
        ld de,HO_RAM
        ld bc,HO_FIN-HO_SRC
        ldir
        ld hl,HOUTD
        ld a,(hl)
        cp 0C9h             ; solo si nadie mas usa el gancho
        jr nz,RP_0
        ld (hl),0C3h
        inc hl
        ld (hl),HO_RAM AND 0FFh
        inc hl
        ld (hl),HO_RAM/256
RP_0:   ld hl,0BD8Ah
        call RP_1
        ld hl,0BE13h
RP_1:   ld a,(hl)           ; solo si es CALL 004Dh
        cp 0CDh
        ret nz
        inc hl
        ld a,(hl)
        cp 4Dh
        ret nz
        inc hl
        ld a,(hl)
        and a
        ret nz
        ld (hl),MSA_LIBRE/256
        dec hl
        ld (hl),MSA_LIBRE AND 0FFh
        ret
WR_SRC: push af
        ld a,l
        di
        out (99h),a
        ld a,h
        and 3Fh
        or 40h
        out (99h),a
        pop af
        out (98h),a
        ei
        ret
WR_FIN:
; Gancho H.OUTD (lo llama OUTDO con PUSH AF delante): si la salida va al fichero
; GRP: en SCREEN 2 y es una letra, la dibuja R_GRPPRT y OUTDO acaba aqui.
HOUTD   equ 0FEE4h
PTRFIL  equ 0F864h
SCRMOD  equ 0FCAFh
GRPHED  equ 0FCA6h
R_CH    equ BUF+0FBh
R_FL    equ BUF+0FCh
R_CC    equ BUF+0FDh
R_C4    equ BUF+0FEh
HO_RAM  equ MSA_LIBRE+WR_FIN-WR_SRC
HO_SRC: push af
        push hl
        push bc
        push de
        push ix
        push iy
        ld (R_CH),a
        ld iy,(MISLOT-1)
        ld ix,R_GRPPRT
        call 001Ch          ; CALSLT
        pop iy
        pop ix
        pop de
        pop bc
        pop hl
        ld a,(R_FL)
        and a
        jr nz,HO_NO
        pop af
        inc sp              ; fuera la vuelta a OUTDO...
        inc sp
        pop af              ; ...y su PUSH AF
        ret
HO_NO:  pop af
        ret
HO_FIN:

; --- R_GRPPRT: lo mismo que GRPPRT de la BIOS (MSX1) en SCREEN 2 ------------------
; Solo para PRINT#1 al fichero GRP: con una letra; si no, R_FL<>0 y sigue OUTDO.
R_GRPPRT:
        ld a,1
        ld (R_FL),a
        ld hl,(PTRFIL)
        ld a,h
        or l
        ret z
        inc hl
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        cp 0FCh             ; dispositivo GRP:
        ret nz
        ld a,(SCRMOD)
        cp 2
        ret nz
        ld a,(GRPHED)
        and a
        ret nz
        ld a,(R_CH)
        cp 20h
        ret c
        xor a
        ld (R_FL),a
        ld a,(GRPACY+1)
        ld hl,GRPACX+1
        or (hl)
        ret nz              ; fuera de la pantalla: ni dibuja ni avanza
        ld a,(GRPACY)
        cp 192
        ret nc
        ld a,(R_CH)
        call GLIFO
        ld a,(GRPACX)
        add a,8
        jr c,RG_CR
        ld (GRPACX),a
        ret
RG_CR:  xor a               ; pasa de 255: principio de la linea siguiente
        ld (GRPACX),a
        ld a,(GRPACY)
        add a,8
        cp 192
        jr c,RG_1
        xor a
RG_1:   ld (GRPACY),a
        ret
R_SIGUE:                    ; sigue en USR9 (carga de ficheros)
