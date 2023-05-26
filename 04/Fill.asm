// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(LOOP)
 // START = SCREEN
 @SCREEN
 D=A
 @START
 M=D

 // END = SCREEN + 8192
 @SCREEN
 D=A
 @8192
 D=D+A
 @END
 M=D

 // if (KBD == 0) GOTO WHITE
 @KBD
 D=M
 @WHITE
 D;JEQ

(BLACK)
 // FILL = 0 - 1
 @0
 D=A
 @1
 D=D-A
 @FILL
 M=D

 // GOTO DRAW  
 @DRAW
 0;JMP

(WHITE)
 // FILL = 0
 @0
 D=A
 @FILL
 M=D

(DRAW)
 // if (END-START == 0) GOTO LOOP
 @END
 D=M
 @START
 D=D-M
 @LOOP
 D;JEQ

 // *START = FILL
 @FILL
 D=M
 @START
 A=M
 M=D

 // START += 1
 @1
 D=A
 @START
 M=M+D

 // GOTO DRAW
 @DRAW
 0;JMP
