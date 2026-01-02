# Usage: 
#   make clean
#   make all
#
#   For windows target compilation
#   make TARGET=WIN all
#   mingw32-gcc must be installed and accessible from command line
#   See: http://www.mingw.org/wiki/howto_install_the_mingw_gcc_compiler_suite
#

TIC_PROCESS_DIR=..

#CFLAGS+=-DTIC_PARSER_NO_CHECKSUM=1 
# Note: when FAKE_ETX_STX uses '<' and '>' instead of '\002' and '\003'
CFLAGS=-Wall -I$(TIC_PROCESS_DIR)  -I.
CFLAGS+=-DTIC_TOOLS_CODECS -DTIC_TOOLS_FAKE_ETX_STX=1 -g -O0

ifeq ($(TARGET),WIN)
${info COMPILE: Compiling for Windows using (MinGw32-gcc)}
CC=mingw32-gcc.exe
EXT="-WIN"
else
${info COMPILE: Compiling with gcc native}
${info Note: Compile with TARGET=WIN for windows (MinGW) executable}
CC=gcc
EXT=""
endif


vpath %.c $(TIC_PROCESS_DIR)

#all: tictobin bintotic tictocrit 
all: bintotic tictobin

bintotic: bintotic.c tic-formater.o tic-tools.o
	$(CC) $(LDFLAGS) $(CFLAGS) $^ -o $@$(EXT)

tictobin: tictobin.c tic-parser.o tic-formater.o tic-tools.o ong-codec-tic.o
	$(CC) $(LDFLAGS) $(CFLAGS) $^ -o $@$(EXT)

%: %.o
	$(CC) $(LDFLAGS) $^ -o $@

clean:
	$(RM) *.o



