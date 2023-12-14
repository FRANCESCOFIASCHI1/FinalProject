# StringCountProject
Progetto finale del corso di laboratorio 2, con uso di concorrenza, segnali, server e client in C e Python.

Per l'implementazione delle comunicazione client-server ho usato 3 sendall che rispettivamente indicano: il tipo della connessione (Tipo A, Tipo B con le varie caratteristiche), il numero di byte che sto per inviare al server ossia la lunghezza della stringa ed infine la stringa stessa.

Per passare il numero di byte necesseri ho creato una funzione che ricoverte in integer i byte scritti nelle FIFO per capire la lunghezza della stringa che devo leggere

Il server differenzia il tipo di connessione dalla prima sendall che entrambi i due client fanno ed elabora ciò che gli viene mandato nei modi indicati

Nel client1 apro una connessione per ogni linea del file e le eseguo in parallelo
Nel client2 per ogni file apro una connessione anche queste in parallelo

Per il paradigma produttori-consumatori ho usato i semafori, due per ogni FIFO e due mutex che regolano l'accesso con mutua esclusione alle variabili condivise coe buffer e index di ogni FIFO

Il copo dei segnali blocca tutti i segnali per gestire e ritornare i valori richiesti per poi terminare tutti i cicli necessari

L'uso di "strtok_r" serve per mantenere un ordine di lettura per spezzare la frase tramite i delineatori dichiarati come variabile globale

Per utilizzare i client e il server come file eseguibili con il comando make ho dovuto dare i permessi per l'esecuzione

Tutte le funzioni tranne conta e aggiungi sono nel file "zdef.c" per accorciare la lunghezza del codice principale in modo tale che sia più leggibile
Le dichiarazioni di alcune variabili globali e di tutte le strutture dati dei vari thread CapoScrittore, CapoLettore e i relativi scrittori e lettori sono scritte nel file "zdef.h"

Nel server per gestire esecuzioni veloci prima che il server e archivio siano inizializzati e pronti all'uso ho utilizzato una try-except globale così da non creare errori quando invio un segnale di kill troppo velocemente prima che sia inizializzato il gestore dei segnali.

Nel server ho anche aggiunto un blocco dei segnali SIGINT e SIGTERM in modo che mentre viene gestita un interruzzione anche premendo ctrl+c non si interrompa il programma e chiuda correttamente archivio
