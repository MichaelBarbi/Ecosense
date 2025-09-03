# EcoSense

Piattaforma di monitoraggio ambientale tramite sensori IoT simulati in tempo reale

# 1. Descrizione generale

L'idea di base è di simulare un’azienda specializzata nella produzione e vendita di sensori IoT
per l’ambiente con l'obiettivo di sviluppare una piattaforma web integrata che unisca
funzionalità di e-commerce e monitoraggio ambientale in tempo reale.

La piattaforma si rivolge a utenti che desiderano un sistema semplice ed efficace per
controllare, tramite sensori, i parametri ambientali come temperatura, umidità, livelli di salinità,
ecc.

Gli utenti potranno acquistare sensori, registrarli nel sistema, organizzarli in
gruppi (per esempio, un gruppo di sensori per una serra o per il recinto di una tartaruga) e
monitorarne i dati in tempo reale.

# 2. Tipologia di utenti

## 2.1 Customer

####

```
Acquisto di sensori
L'utente può selezionare i sensori dal catalogo e completare l'acquisto dalla pagina di
checkout.
```
```
Registrazione di sensori
Alla consegna (simulata) del sensore, l'utente, dopo aver compiuto l'accesso alla
piattaforma, potrà registrare il sensore acquistato inserendo nell'apposito portale web il
codice di registrazione e la password del prodotto, con l'eventualità di assegnare un
titolo esaustivo al medesimo per facilitarne il riconoscimento.
```
```
Gestione dei gruppi di sensori
La piattaforma mette a disposizione la possibilità di organizzare uno o più sensori
all'interno di gruppi. Ogni gruppo è una raccolta logica di sensori. Questa scelta mira a
facilitare la gestione di molteplici sensori e dei diversi luoghi d'interesse.
```
```
Monitoraggio in tempo reale
L'utente potrà visualizzare in tempo reale le misurazioni dei sensori accedendo al
gruppo di cui fanno parte.
```
```
Ticket
Per ogni tipologia di richiesta o di errore, l'utente può mettersi in contatto con un
operatore mediante l'apertura di un ticket.
```

## 2.2 Staff

I membri staff sono quelle figure che hanno accesso al portale di back-office dell'applicazione.

A differenza dei customer, i membri staff non si registrano manualmente per mezzo di una
pagina di registrazione, bensì, il loro account viene precedentemente creato da un utente con i
permessi da superuser. Questa scelta è motivata dal fatto che si vuole evitare la possibilità che
un generico utente possa registrarsi come utente staff.

A qualsiasi dipendente dell'azienda verrà creato appunto un account nel quale lo username
corrisponde alla mail, la quale possederà il dominio aziendale per rispettare gli standard.

L'accesso al portale avviene invece nella pagina di login che è condivisa fra tutti gli utenti.

A questo stato finale del progetto, si riconoscono due tipologie di membri staff: i technical e i
sales user.

In seguito alcuni vincoli su questi gruppi di permessi:
```
Un utente staff può essere:
-Solo technical
-Solo sales
-Entrambi
-Indipendentemente dal ruolo dell'utente staff, entrambi avranno comunque accesso alla
lista di ordini effettuati dai customer e al portale dei ticket.
```

### 2.2.1 Technical user staff

Questi membri svolgeranno il ruolo di monitoraggio e assistenza tecnica dei sensori.
Avranno a disposizione un elenco dei sensori registrati e, per ognuno, la possibilità di
visualizzare le misurazioni rilevate in passato e quelle che stanno venendo trasmesse inquesto
momento.

Inoltre, avranno anche il compito di inserire, modificare ed eliminare i sensori fisici.

## 2.2.2 Sales user staff

Questi membri avranno accesso alle informazioni relative al settore delle vendite.

In particolare:
```
-Un pannello nel quale revisionare le statistiche di mercato più inerenti:
-Grafico a barre con i sensori più venduti
-Grafico a torta con la distribuzione geografica dei sensori
-Grafico a linee con il numero di ordini mensili nell'arco dell'anno corrente
-Grafico a linee con i profitti mensili nell'arco dell'anno corrente.
-L'aggiunta, l'eliminazione e la modifica dei sensori nel catalogo.
```

# 3. Dettagli tecnici
```
-Backend: Django
-Frontend: Django Templates, (HTML, CSS, Javascript, Boostrap)
-Lingua dell'applicazione: Inglese
-Protocolli:
-HTTP: Richieste di risorse web
-WebSocket: Django Channels per la comunicazione in tempo reale
-Database: Postgresql
-Simulatore sensori: Applicazione Python multithread che invia dati periodici tramite
WebSocket
-Autenticazione e permessi: Sistema integrato Django, con gruppi personalizzati
-Web Server: daphne per permettere la gestione di richieste asincrone e l'integrazione
con il protocollo WebSocket
```

# 4. Cenni sulla sicurezza
```
Si utilizzano i validatori delle password native di django per le password degli utenti per
evitare che siano troppo deboli.
```
```
Per ogni sensore sono associati 3 codici che sono cifrati nel database:
-Codice di regisrazione che identifica univocamente un sensore fisico acquistabile
da utilizzare per identificare quale sensore l'utente sta registrando.

-Password per offrire maggiore affidabilità nella fase di autenticazione della
registrazione.

-API KEY che viene inviata in automatico ad ogni misurazione dal sensore per
attestare l'origine del mittente.
```




