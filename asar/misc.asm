
; CLEARING TEXT BOXES
; Tedanki Prisoner text box 
org $CB3F7F
db $00, $00, $00, $00, $00, $00

; Magic Ball man
org $CA01A1
db $00, $00, $00, $00, $00, $00

; Yellow Orb
org $CDA93B
db $00, $00, $00, $00, $00, $00
org $CDA952
db $00, $00, $00, $00, $00, $00

; Starry Ring
org $CB90CE
db $00, $00, $00, $00, $00, $00
org $CB90E5
db $00, $00, $00, $00, $00, $00

; Ortega's Helm
org $CB39F6
db $00, $00, $00, $00, $00, $00

; Wizard Ring
org $CDA8FB
db $00, $00, $00, $00, $00, $00
org $CDA909
db $00, $00, $00, $00, $00, $00

; Silver Orb
org $CBA12E
db $00, $00, $00, $00, $00, $00




; Remove Change Staff -> Sailor Bone exchange flags
org $CB4EFF
nop
nop
nop
nop
nop
nop

org $CB4F0B
nop
nop
nop
nop






; MOVE EVENT FLAG CHECKING

; Rainbow Drop Shrine
org $CC8991
lda $359A

org $CC89AB
lda $359A

; Lovely Memories usage
org $CC930A
lda $359C

; Elf Queen 
org $CA1892
lda $359E





; CHEST HOOK FOR EVENT FLAGS
org $C44789
jml FlagHandler

org $C0F400
FlagHandler:

pha
phx
phy


; Rain Staff
CMP #$0011
BNE FlagCheck2
sep #$30
LDA #$80
TSB $359A
rep #$30
BRA FlagFinish

FlagCheck2:
; Stones of Sunlight
CMP #$00C8
BNE FlagCheck3
sep #$30
LDA #$20
TSB $359A
rep #$30
BRA FlagFinish

FlagCheck3:
; Sacred Talisman
CMP #$0084
BNE FlagCheck4
sep #$30
LDA #$02
TSB $359A
rep #$30
BRA FlagFinish

FlagCheck4:
; Black Pepper
CMP #$00A2
BNE FlagCheck5
sep #$30
LDA #$10
TSB $3542
rep #$30
BRA FlagFinish

FlagCheck5:
; Sailor Bone
CMP #$00C1
BNE FlagCheck6
sep #$30
LDA #$80
TSB $3510
LDA #$DB
TSB $351C
LDA #$08
TSB $3546
rep #$30
BRA FlagFinish

FlagCheck6:
; Lovely Memories
CMP #$00BE
BNE FlagCheck7
sep #$30
LDA #$80
TSB $359C
rep #$30
BRA FlagFinish

FlagCheck7:
; Dream Ruby
CMP #$00AE
BNE FlagCheck8
sep #$30
LDA #$10
TSB $359E
rep #$30
BRA FlagFinish

FlagCheck8:

FlagFinish:

ply
plx
pla


pha
phx
phy
lda $002F, X
and #$00FF
JML $C44790



;;;; THE BELOW WORKS FINE FOR FULL EXP MULTIPLIERS 
; hook for EXP Multiplier
org $C2A74A
jml $C0F500

org $C0F500
phy
phx
pha

; times 4

clc 
; this checks if x4 would overflow, if so, increase too much
sep #$30
lda $23DD
cmp #$40
bcc EXPCase1
inc $23DE

EXPCase1:

rep #$30
asl $23DC
asl $23DC


pla
plx
ply

lda $23dc
sta $00
lda $23de
sta $02
jml $C2A754





; Disable Dharma level checking
org $C3E500
cpx #$0001





; misc fixes
; Sabrina in Portoga weird issue w/ #7e3541
org $cb0140
jml $CB0148
