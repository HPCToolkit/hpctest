#BHEADER****************************************************************
# (c) 2007   The Regents of the University of California               *
#                                                                      *
# See the file COPYRIGHT_and_DISCLAIMER for a complete copyright       *
# notice and disclaimer.                                               *
#                                                                      *
#EHEADER****************************************************************

ifdef llomp
LLVM_OMP = -Wl,-rpath=$(llomp) -L $(llomp) -lomp
endif

ifdef mpi
CC       = mpicc
else
CC       = gcc
endif

LDR      = $(CC)

OFLAGS   = -g -O3 -fopenmp

CFLAGS   = -c $(OFLAGS)

LDFLAGS  = $(OFLAGS) 

LIBS     = $(LLVM_OMP)
LIB_DIRS = 

PROG     = AMGMk

OBJS     = main.o \
           csr_matrix.o   csr_matvec.o  \
           laplace.o relax.o \
           hypre_error.o hypre_memory.o \
           vector.o

all : $(PROG)

$(PROG) : $(OBJS)
	$(LDR)  $(LDFLAGS) -o $(PROG) $(OBJS) $(LIB_DIRS) $(LIBS)


clean :
	rm -f *.o $(PROG) core job.out *~ 


.SUFFIXES : .o  .c

#*****************************************************************
#* Rules for C object file dependencies
#*****************************************************************
.c.o :
	$(CC) $(CFLAGS) $*.c 







