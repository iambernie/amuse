# standard amuse configuration include
# config.mk will be made after ./configure has run
AMUSE_DIR?=../../../..
-include ${AMUSE_DIR}/config.mk

MPICXX   ?= mpicxx

CFLAGS   += 
CXXFLAGS += $(CFLAGS) 
LDFLAGS  += -lm $(MUSE_LD_FLAGS)

OBJ = interface.o

CODELIB = src/libhalogen.a

CODE_GENERATOR = $(AMUSE_DIR)/build.py

all: halogen_worker 

clean:
	$(RM) -f *.so *.o *.pyc worker_code.cc worker_code.h 
	$(RM) *~ halogen_worker worker_code.cc
	make -C src clean

$(CODELIB):
	make -C src all

worker_code.cc: interface.py
	$(CODE_GENERATOR) --type=c interface.py HalogenInterface -o $@

worker_code.h: interface.py
	$(CODE_GENERATOR) --type=H interface.py HalogenInterface -o $@

halogen_worker: worker_code.cc worker_code.h $(CODELIB) $(OBJ)
	$(MPICXX) $(CXXFLAGS) $(LDFLAGS) $< $(OBJ) $(CODELIB) -o $@  $(LIBS)

$(OBJ): interface.cc interface.h
	$(CXX) $(CXXFLAGS) -c -o $(OBJ) $<
