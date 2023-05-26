// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

@2
M=0

(LOOP)

 // if (R2 == 0) PC=@END 
 @0
 D=M
 @END
 D;JEQ

 // R0=R0-1
 D=D-1
 @0
 M=D

 // R2=R2+R1
 @2
 D=M
 @1
 D=D+M
 @2
 M=D

 // PC=@LOOP
 @LOOP
 0;JMP

(END)
 @END
 0;JMP
