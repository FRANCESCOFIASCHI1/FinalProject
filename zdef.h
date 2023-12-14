#define _GNU_SOURCE /* See feature_test_macros(7) */
#include "xerrori.h"
#include <assert.h> // permette di usare la funzione assert
#include <errno.h>
#include <search.h>
#include <signal.h>
#include <math.h>
#include <stdbool.h> // gestisce tipo bool (variabili booleane)
#include <stdio.h>   // permette di usare scanf printf etc ...
#include <stdlib.h>  // conversioni stringa/numero exit() etc ...
#include <string.h>  // confronto/copia/etc di stringhe
#include <unistd.h>  // per sleep
#include <ctype.h>

// Funzioni manipolazione ENTRY
ENTRY *crea_entry(char *s, int n);
void distruggi_entry(ENTRY *e);
// funzione per leggere dalle FIFO
ssize_t readn(int,void *ptr, size_t n);
// funzione per convertire byte in un intero
int my_byte_to_integer(char* bytes);
int my_byte_to_integer2(char* bytes);
// funzione per convertire intero in stringa
char *writeInt(int file, char *label, int num);

#define Num_elem 1000000

// definisco costanti
#define PC_buffer_len 10
#define PORT 56697
#define Max_sequence_length 2048
const char *delim = ".,:; \n\r\t";

/*-------CAPOSCRITTORE-------*/
//struttura dati del thread caposcrittore
typedef struct datecaposc {
  int *caposcindex;  // indice nel buffer
  char **buffer;
  sem_t *sem_caposc_free;
  sem_t *sem_caposc_data;
} datecaposc;

/*-------CAPOLETTORE-------*/
//struttura dati del thread capolettore
typedef struct datecapolet {
  int *capoletindex;  // indice nel buffer
  char **buffer;
  sem_t *sem_capolet_free;
  sem_t *sem_capolet_data;
} datecapolet;

/*-------Thread SCRITTORI-------*/
//struttura dati dei thread comuni scrittori
typedef struct thread_scritto {
  pthread_cond_t *cv;  // condition variables condiviso con thread lettori
  int *scrittoindex;  // indice nel buffer
  char **buffer;
  pthread_mutex_t *scrittori_mutex;    // mutex condiviso con thread lettori
  sem_t *sem_caposc_free;
  sem_t *sem_caposc_data;
} TS;

/*-------Thread LETTORI-------*/
//struttura dati dei thread comuni lettore
typedef struct thread_letto {
  pthread_cond_t *cv;  // condition variables condiviso con thread lettori
  int *lettoindex;  // indice nel buffer
  char **buffer;
  pthread_mutex_t *lettori_mutex;    // mutex condiviso con thread lettori
  sem_t *sem_capolet_free;
  sem_t *sem_capolet_data;
} TL;