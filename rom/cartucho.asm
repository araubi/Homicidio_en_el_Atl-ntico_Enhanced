; Homicidio en el Atlantico (MSX) - cartucho ASCII16 de 64 KB
; Cargador: araubi con Claude (2026), MIT. Probado en openMSX: Sony HB-20P y HB-F900 (disco). El juego es de Cobra Soft / Infogrames.
; El banco 0 (4000h-7FFFh) lleva este codigo, la pantalla de titulo y la tabla de
; ficheros; el resto de la ROM son los ficheros de la cinta, troceados por bancos.
RSLREG  equ 0138h
ENASLT  equ 0024h
CHGMOD  equ 005Fh
CHGCLR  equ 0062h
DISSCR  equ 0041h
ENASCR  equ 0044h
WRTVRM  equ 004Dh
FILVRM  equ 0056h
GRPPRT  equ 008Dh
CHGET   equ 009Fh
KILBUF  equ 0156h
EXPTBL  equ 0FCC1h
HSTKE   equ 0FEDAh
FORCLR  equ 0F3E9h
BAKCLR  equ 0F3EAh
BDRCLR  equ 0F3EBh
GRPACX  equ 0FCB7h
GRPACY  equ 0FCB9h
LOGOPR  equ 0FB02h
DAC2    equ 0F7F8h
VARTAB  equ 0F6C2h
ARYTAB  equ 0F6C4h
STREND  equ 0F6C6h
KEYBUF  equ 0FBF0h
PUTPNT  equ 0F3F8h
GETPNT  equ 0F3FAh
BUF     equ 0F55Eh          ; bufer de INLIN: libre mientras se ejecuta una orden
USRTAB  equ 0F39Ah
STUB    equ 0DDF3h          ; hueco libre entre el final de MSA (DDF2h) y NU (DE00h): 13 bytes
BANCO1  equ 6000h           ; registro ASCII16 de la pagina 1
        include "variante.inc"     ; RAPIDA equ 0/1

        org 4000h
        db "AB"
        dw INIT
        dw 0,0,0
        ds 6,0

; --- INIT: averigua el slot del cartucho y engancha H.STKE ------------------
INIT:   call RSLREG
        rrca
        rrca
        and 3
        ld c,a
        ld b,0
        ld hl,EXPTBL
        add hl,bc
        ld a,(hl)
        and 80h
        or c
        ld c,a
        jp p,IN_NOEXP
        inc hl
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        and 0Ch
        or c
        ld c,a
IN_NOEXP:
        ld hl,HSTKE
        ld (hl),0F7h        ; RST 30h (llamada entre slots)
        inc hl
        ld (hl),c
        inc hl
        ld (hl),ARRANQUE & 0FFh
        inc hl
        ld (hl),ARRANQUE / 256
        inc hl
        ld (hl),0C9h
        ret

; --- ARRANQUE: el BASIC ya esta listo (gancho H.STKE) -----------------------
; En maquinas con disco quien llama a H.STKE es codigo en la RAM de 8000h, asi
; que aqui no se toca la RAM baja: se pinta el titulo, se elige juego o test y
; se teclea en el bufer una orden que hace el resto desde el BASIC:
;   CLEAR9,&HCFFF:?USR9(6):RUN20010   (o ?USR9(7):RUN para el test)
; CLEAR deja la pila por encima de TRIMMS (9000h-C676h) y del programa.
ARRANQUE:                   ; el BASIC espera HL y BC intactos (STKINI)
        push hl
        push bc
        push de
        push af
        call ARR2
        pop af
        pop de
        pop bc
        pop hl
        ret
ARR2:   ei                  ; la llamada entre slots llega con DI
        ld hl,STUB_SRC      ; rutina residente para USR9
        ld de,STUB
        ld bc,STUB_FIN-STUB_SRC
        ldir
        ld a,(HSTKE+1)
        ld (MISLOT),a       ; (en RAM, dentro del propio STUB)
        ld (STUB+3),a       ; LD IY,ss00
        ld a,0C9h
        ld (HSTKE),a        ; el gancho solo una vez
        ld hl,STUB
        ld (USRTAB+2*9),hl  ; DEFUSR9=&HDDF3
        call TITULO
        call MENU           ; Z = juego, NZ = test
        ld hl,TXT_RUNJ
        jr z,AR_TECLAS
        ld hl,TXT_RUNT
AR_TECLAS:
        ld a,1
        ld (FORCLR),a       ; lo que se teclea no se ve
        ld (BAKCLR),a
        ld de,KEYBUF
AR_T1:  ld a,(hl)
        ld (de),a
        inc hl
        inc de
        cp 13
        jr nz,AR_T1
        ld (PUTPNT),de
        ld hl,KEYBUF
        ld (GETPNT),hl
        ret
TXT_RUNJ: db "CLEAR9,&HCFFF:?USR9(6):RUN20010",13
TXT_RUNT: db "CLEAR9,&HCFFF:?USR9(7):RUN",13

; TRIMMS deja el BASIC en la pagina 1 al acabar: se llama desde la RAM y
; luego se vuelve a poner el cartucho.
TRAMPOLIN:
        ld hl,TR_SRC
        ld de,BUF+40h
        ld bc,TR_FIN-TR_SRC
        ldir
        jp BUF+40h
TR_SRC: call 9000h
        ld a,(MISLOT)
        ld hl,4000h
        jp ENASLT
TR_FIN:

; --- USR9: carga el fichero DAC2 (llamado por CALSLT desde el STUB) ----------
USR9:
 IF RAPIDA
        include "rapida.asm"
 ENDIF
        ld a,(DAC2)
        cp 6
        jr z,U9_JUEGO
        cp 7
        jr nz,CARGA
        ld a,5              ; 7: programa del test
        jr U9_PROG
U9_JUEGO:                   ; 6: TRIMMS (como BLOAD ,R) y programa del juego
        ld a,2
        call CARGA
        call TRAMPOLIN
        ld a,4
U9_PROG:
        call CARGA          ; programa BASIC ya tokenizado a 8001h
        ld (VARTAB),de
        ld (ARYTAB),de
        ld (STREND),de
        xor a
        ld (8000h),a
        ret
; --- CARGA: copia el fichero A (trozos de la tabla) a su sitio en la RAM ------
; Sale con DE = direccion siguiente al ultimo byte copiado.
CARGA:  ld l,a
        ld h,0
        add hl,hl
        ld de,TABLA
        add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a              ; HL = lista de trozos (banco, origen, destino, largo)
CA_TROZO:
        ld a,(hl)
        cp 0FFh
        ret z
        push hl
        ld de,BUF           ; copia la rutina de copia a la RAM y la parchea
        push de
        ld hl,CP_SRC
        ld bc,CP_FIN-CP_SRC
        ldir
        pop ix
        pop hl
        ld a,(hl)
        ld (ix+1),a         ; banco
        inc hl
        ld a,(hl)
        ld (ix+6),a         ; origen
        inc hl
        ld a,(hl)
        ld (ix+7),a
        inc hl
        ld a,(hl)
        ld (ix+9),a         ; destino
        inc hl
        ld a,(hl)
        ld (ix+10),a
        inc hl
        ld a,(hl)
        ld (ix+12),a        ; largo
        inc hl
        ld a,(hl)
        ld (ix+13),a
        inc hl
        push hl
        di
        call BUF
        ei
        pop hl
        jr CA_TROZO
CP_SRC: ld a,0
        ld (BANCO1),a
        ld hl,0
        ld de,0
        ld bc,0
        ldir
        xor a
        ld (BANCO1),a
        ret
CP_FIN:

; --- Rutina residente (se copia a DDF3h) -------------------------------------
STUB_SRC:
        ld iy,0             ; byte 3 = slot del cartucho
        ld ix,USR9
        jp 001Ch            ; CALSLT
MISLOT_OFS equ $-STUB_SRC
        db 0
STUB_FIN:
MISLOT  equ STUB+MISLOT_OFS

; --- Pantalla de titulo (lo mismo que hacia ENTETE en 9000h) ----------------
TITULO: ld a,1
        ld (FORCLR),a
        ld (BAKCLR),a
        ld (BDRCLR),a
        ld a,2
        call CHGMOD
        call CHGCLR
        call DISSCR
        ld ix,DATOS_TITULO
        ld hl,0000h
        call VUELCA
        ld hl,2000h
        call VUELCA
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

; --- Menu: juego o test -------------------------------------------------------
MENU:   ld hl,1700h+5*8     ; fila 23, columnas 5-26: franja negra para el texto
        ld bc,22*8
        xor a
        call FILVRM
        ld hl,3700h+5*8
        ld bc,22*8
        ld a,0A1h
        call FILVRM
        ld a,10
        ld (FORCLR),a
        xor a
        ld (LOGOPR),a
        ld hl,TXT_MENU
        ld de,48
ME_C:   ld a,(hl)
        and a
        jr z,ME_TECLA
        ld (GRPACX),de
        push de
        ld de,184
        ld (GRPACY),de
        push hl
        call GRPPRT
        pop hl
        pop de
        inc hl
        ex de,hl
        ld bc,8
        add hl,bc
        ex de,hl
        jr ME_C
ME_TECLA:
        call KILBUF
ME_T1:  call CHGET
        and 0DFh            ; mayusculas
        cp 'J'
        ret z
        cp 'T'
        jr nz,ME_T1
        or a                ; NZ
        ret
TXT_MENU: db 0A8h,"JUEGO O TEST? (J/T)",0

; Nunca se ejecuta: LD (77FFh),A de relleno para que openMSX y BlueMSX
; detecten ASCII16 sin dudas (ver LECCIONES_MAPPER_BLUEMSX.md).
HEURISTICA:
        rept 6
        ld (77FFh),a
        endm
        include "tabla.inc"
DATOS_TITULO:
        incbin "titulo.bin"
 IF RAPIDA
DATOS_PLANO:
        incbin "plano.rle"
 ENDIF
FIN_BANCO0:
