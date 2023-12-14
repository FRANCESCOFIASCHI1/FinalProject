# definizione del compilatore e dei flag di compilazione
# che vengono usate dalle regole implicite
CC=gcc
CFLAGS=-g -Wall -O -std=gnu99
LDLIBS=-lm -lrt -pthread


# eseguibili da costruire
EXECS=archivio   #posso metterci gli altri eseguibili da creare
.PHONY: clean

# di default make cerca di realizzare il primo target 
all: $(EXECS)
	chmod +x server.py
	chmod +x client1
	chmod +x client2

# non devo scrivere il comando associato ad ogni target 
# perché il default di make in questo caso va bene

archivio: archivio.o zdef.o xerrori.o        #sono i requisiti per ogni eseguibile


# target che cancella eseguibili e file oggetto
clean:
	rm -f $(EXECS) *.o *. *.log
	clear

test:	
	./server.py 5 -r 2 -w 4 -v &
	sleep 4
	./client2 file1 file2
	./client1 file3
	pkill -INT -f server.py
