ArchiveCategoryBot
===========
**Autori**: 
- Mario Cetrangolo
- Manlio Santonastaso

**ArchiveCategoryBot** è un bot intelligente per Telegram in grado di fornire
un archivio sicuro dove l'utente può organizzare i vari documenti/file in categorie grazie all'apprendimento automatico
(machine learning) di un classificatore capace di categorizzare (business,entertainment,sport,tech,politics) i vari documenti inseriti. Inoltre offre 
la possibilità di tradurre i vari documenti, scaricare ed eliminare. 
Le funzionalità offerte dal bot sono:

-   **Login e registrazione**: l’utente può registrarsi al bot
    inserendo il nome dell'archivio 
-   **Upload File**: l’utente può inserire qualsiasi file, dopodichè 
    verrà categorizzato in una delle cinque categorie (business,entertainment,sport,tech,politics)
    oppure la possibilità di creare una nuova categoria.
-   **Translate**: l'utente ha la possibilità di tradurre i documenti/file 
    inseriti in cinque lingue (italiano,inglese,francese,tedesco e cinese)
-   **Scarica file**: l'utente ha la possibilità di scaricare i documenti/file
    inseriti tramite una ricerca per nome oppure una ricera totale passando
    dallo storage, categorie fino ad arrivare al file desiderato
-   **Cancella file**: l'utente ha la possibilità di eliminare i documenti/file
    inseriti tramite una ricerca per nome oppure una ricera totale passando
    dallo storage, categorie fino ad arrivare al file desiderato

Il bot è stato sviluppato in Python ed è stato pubblicato sul canale
Telegram ed utilizza i seguenti servizi:

-   **AppService**: Per effettuare hosting dell'applicazione su cloud.
-   **BotService**: Per sviluppare, testare e pubblicare il bot
    in Azure.
-   **AzureSQL**: Per conservare i dati persistenti relativi agli utenti
    e allo storage in particolare modo ai container(categorie) e ai blob(file)
    inseriti. 
-   **Azure Cognitive services for Language**: per creare un modello di Intelligenza
    Artificiale per classificare il testo non strutturato in classi personalizzate.
-   **FunctionApp HttpTrigger**: Viene attivata alla ricezione di una
    richiesta HTTP (post) da parte del bot che fornisce nome dello storage, 
    accountkey, nome archivio in modo tale da eliminare nello storage account
    file nei container temporanei.
-   **Translator**: per tradurre documenti complessi in 5 lingue (nel nostro caso)
    ma potenzialmente in tutte le lingue, mantenendo al tempo stesso la struttura
    del documento originale e il formato dei dati
-   **ConvertApi**: non è un servizio di azure, ma è stato utile per convertire i file/
    documenti in file di testo in modo tale da passare il contenuto al servizio
    Cognitive services for Language per classificare il documento/file.

Prerequisiti
------------
-   Una sottoscrizione ad Azure
-   Python 3.7
-   Azure CLI
-   Bot Framework Emulator
-   Ngrok
-   Visual Studio Code con le estensioni App Service e Functions
-   Installare ODBC Driver 17 for SQL Server.

Installazione
-------------
Clonare la repository Github e installare in un ambiente virtuale i
pacchetti richiesti con il comando:
```sh
pip install -r requirements.txt
```


Risorse
-------

### Resource Group

È necessario creare un resource group in cui inserire le varie risorse.

### Web App

1.  Aprire il prompt dei comandi per accedere al portale di Azure con il
    comando.
```sh
az login
```

1.  Impostare la sottoscrizione predefinita da usare
```sh
az account set --subscription "&lt;azure-subscription&gt;"
```
1.  Creare la registrazione dell’applicazione con il comando
```sh
az ad app create --display-name "displayName" --password "AtLeastSixteenCharacters_0" --available-to-other-tenants
```

È necessario registrare i valori **appID** e **secret** dopo
l’esecuzione del comando precedente. 

### Servizio dell’applicazione bot

Eseguire distribuzione tramite modello arm con un nuovo gruppo di risorse
```sh
az deployment sub create --template-file "<path-to-template-with-new-rg.json" --location <region-location-name> --parameters appId="<app-id-from-previous-step>" appSecret="<password-from-previous-step>" botId="<id or bot-app-service-name>" botSku=F0 newAppServicePlanName="<new-service-plan-name>" newWebAppName="<bot-app-service-name>" groupName="<new-group-name>" groupLocation="<region-location-name>" newAppServicePlanLocation="<region-location-name>" --name "<bot-app-service-name>"
```

**esempio**
```sh
az deployment sub create --template-file "C:\Users\cetra\Desktop\cloud\Progetto\Archive_Category\deploymentTemplates\template-with-new-rg.json" --location westeurope --parameters appId="appid" appSecret="password" botId="ArchiveCategoryBot" botSku=F0 newAppServicePlanName="appservicebot" newWebAppName="newWebappname" groupName="ArchiveCategoryBot-RG" groupLocation="westeurope" newAppServicePlanLocation="westeurope" --name "ArchiveCategoryBot" 
```


Assegnare ID app e password nel file config.py


------------------------------------
Creare il provider Azure AD identity
------------------------------------
### Servizio dell’applicazione bot

1.  Nel browser passare al **portale di Azure**.
2.  Nel pannello di sinistra selezionare **Crea una nuova risorsa**.
3.  Nel pannello di destra cercare i tipi di risorsa che includono la
    parola *bot* e scegliere **Registrazione canali bot**.
4.  Fare clic su **Crea**.
5.  Nel pannello **Registrazione canali bot** immettere le informazioni
    richieste. 
6.  Fare clic su **Creazione automatica password e ID app** e
    selezionare **Crea nuovo**.
7.  Fare clic su **Crea ID app nel portale di registrazione
    dell'app**. Verrà aperta una nuova pagina.
8.  Nella pagina **Registrazioni per l'app** fare clic su **Nuova
    registrazione** in alto a sinistra.
9.  Immettere il nome dell'applicazione bot che si intende registrare,
    ad esempio BotTipBooks. Per ogni bot è necessario specificare un
    nome univoco.
10. Per **Tipi di account supportati** selezionare *Account in qualsiasi
    directory dell'organizzazione (qualsiasi directory di Azure AD -
    Multi-tenant) e account Microsoft personali (ad esempio,
    Skype, Xbox)*.
11. Fare clic su **Register**. Al termine, Azure visualizza una pagina
    di panoramica per la registrazione dell'app.
12. Copiare il valore di **ID applicazione (client)** e salvarlo in
    un file.
13. Nel pannello di sinistra fai clic su **Certificati e segreti**.

    1.  In *Segreti client* fare clic su **Nuovo segreto client**.
    2.  Aggiungere una descrizione per identificare questo segreto
        rispetto ad altri che potrebbero essere necessari per creare
        per l'app.
    3.  Impostare **Scadenza** su **Mai**.
    4.  Scegliere **Aggiungi**.
    5.  Copiare il nuovo segreto client e salvarlo in un file

14. Tornare alla finestra *Registrazione canali bot* e copiare il valore
    di **ID app** e **Segreto client** rispettivamente nelle
    caselle **ID app Microsoft** e **Password**.
15. Fare clic su **OK**.
16. Fare infine clic su **Crea**.

### Provider di identità Azure AD

1.  Aprire il pannello **Azure Active Directory** nel portale di
    Azure. Se non ci si trova nel tenant corretto, fare clic su **Cambia
    directory** per passare al tenant corretto.
2.  Aprire il pannello **Registrazioni per l'app**.
3.  Nel pannello **Registrazioni per l'app** fare clic su **Nuova
    registrazione**.
4.  Compilare i campi obbligatori e creare la registrazione per l'app.

    1.  Assegnare un nome all'applicazione.
    2.  Selezionare le opzioni per **Tipi di account supportati** per
        l'applicazione. 
    3.  Per **URI di reindirizzamento**

        1.  Selezionare **Web**.
        2.  Impostare
            l'URL su https://token.botframework.com/.auth/web/redirect.

    4.  Fare clic su **Register**. Dopo la creazione, Azure visualizza
        la pagina **Panoramica** per l'app. Registrare il valore di **ID
        applicazione (client)**. Questo valore verrà usato in un secondo
        momento come *ID client* quando si crea la stringa di
        connessione e si registra il provider di Azure ad con la
        registrazione bot. Registrare anche il valore di **ID della
        directory (tenant)**. Questa operazione verrà usata anche per
        registrare l'applicazione del provider con il bot.

5.  Nel riquadro di spostamento fare clic su **Certificati e
    segreti** per creare un segreto per l'applicazione.

    1.  In **Segreti client** fare clic su **Nuovo segreto client**.
    2.  Aggiungere una descrizione per identificare questo segreto
        rispetto ad altri che potrebbero essere necessari per creare per
        l'app, ad esempio bot login.
    3.  Impostare **Scadenza** su **Mai**.
    4.  Scegliere **Aggiungi**.
    5.  Prima di chiudere questa pagina, registrare il segreto. Questo
        valore verrà usato successivamente come *segreto client* quando
        si registra l'applicazione Azure AD con il bot.

6.  Nel riquadro di spostamento fare clic su **Autorizzazioni API** per
    aprire il pannello **Autorizzazioni API**. È consigliabile impostare
    in modo esplicito le autorizzazioni API per l'app.

    1.  Fare clic su **Aggiungi un'autorizzazione** per visualizzare il
        riquadro **Richiedi le autorizzazioni dell'API**.
    2.  Per questo esempio selezionare **API Microsoft** e **Microsoft
        Graph**.
    3.  Scegliere **Autorizzazioni delegate** e assicurarsi che le
        autorizzazioni necessarie siano selezionate. Inserire le
        autorizzazioni:

		-   **openid**
		-   **profile**
		-   **Mail.Read**
		-   **Mail.Send**
		-   **User.Read**
		-   **User.ReadBasic.All**

	4.  Fare clic su **Aggiungi autorizzazioni**. 

A questo punto si ha un'applicazione Azure AD configurata.

### Registrare l’applicazione AD con il bot

1.  Passare alla pagina di registrazione ai canali bot del bot nel
    portale di Azure.
2.  Fare clic su **Impostazioni**.
3.  Sotto **OAuth Connection Settings** (Impostazioni di
    connessione OAuth) nella parte inferiore della pagina fare clic
    su **Aggiungi impostazione**.
4.  Compilare il modulo come segue:

    1.  **Nome**. immettere un nome per la connessione. Sarà usato nel
        codice del bot.
    2.  **Provider di servizi**. Selezionare **Azure Active Directory
        V2**. Quando si seleziona questa opzione, vengono visualizzati i
        campi specifici di Azure AD.
    3.  **ID client**. Immettere l'ID applicazione (client) registrato
        per il provider di identità Azure AD V2.
    4.  **Segreto client**. Immettere il segreto registrato per il
        provider di identità Azure AD V2.
    5.  **URL di scambio di token**. Lasciarlo vuoto perché è usato per
        SSO solo in Azure AD V2.
    6.  **ID tenant**. Immettere common.
    7.  Per gli **ambiti**, immettere i nomi dell'autorizzazione scelta
        dalla registrazione dell'applicazione. A scopo di test, è
        possibile immettere solo: openid profile.
    8.  Fare clic su Salva.

Aggiornare nel codice del bot il file config.py.

-   Impostare **ConnectionName** sul nome dell’impostazione di
    connessione OAuth aggiunto al bot.
-   Impostare **MicrosoftAppId** e **MicrosoftAppPassword** sull’ID app
    e il segreto del bot. (se non sono stati messi in precedenza)
-----------------------------------


### Classificazione del testo personalizzata

### Creare una nuova risorsa di Azure e un nuovo account di archiviazione BLOB di Azure
Prima di poter usare la classificazione del testo personalizzata, dovrai creare una risorsa in lingua di Azure, che ti fornirà le credenziali necessarie per creare un progetto e iniziare ad addestrare un modello. Avrai anche bisogno di un account di archiviazione di Azure, in cui puoi caricare il tuo set di dati che verrà utilizzato per creare il tuo modello.

 1. Passare al **portale di Azure** per creare una nuova risorsa della lingua di Azure. Se ti viene chiesto di selezionare funzionalità aggiuntive, seleziona **Classificazione del testo personalizzata e NER personalizzato**. Quando crei la tua risorsa, assicurati che abbia i seguenti parametri.
    a. Posizione: West US 2 o WEST Europe
    b. Fascia di Prezzo: Piano tariffario Standars (S)
 2. Nella sezione **Riconoscimento di entità nominative personalizzate (NER) e classificazione personalizzata (anteprima)**, seleziona un account di archiviazione esistente o seleziona **Crea un nuovo account di archiviazione**. Tieni presente che questi valori sono per questo avvio rapido e non necessariamente i valori dell'account di archiviazione che vorrai usare negli ambienti di produzione.
    a. Nome: Nome qualsiasi.
    b. Prestazioni: Standard.
    c. Tipo di conto: Archiviazione (uso generico v1).
    d. Replica: Archiviazione con ridondanza locale (LRS).
    e. Posizione: Qualsiasi posizione più vicina a te, per la migliore latenza.
    
### Carica dati di esempio nel contenitore BLOB
Dopo aver creato un account di archiviazione di Azure e averlo collegato alla risorsa Lingua, dovrai caricare i file di esempio nella directory radice del contenitore per questo avvio rapido. Questi file verranno successivamente utilizzati per addestrare il tuo modello.
  1. Scarica i dati da questo link http://mlg.ucd.ie/files/datasets/bbc.zip. Estrai il file zip e all'interno troverai 2.225 documenti dal sito web di notizie della bbc              corrispondenti a storie in cinque aree tematiche dal 2004 a 2005. Queste aree sono:
     - Business
     - Entertainment
     - Politics
     - Sport
     - Tech
  2. Nel portale di Azure passare all'account di archiviazione creato e selezionarlo.
  3. Nel tuo account di archiviazione, seleziona **Contenitori** dal menu a sinistra, che si trova sotto **Archiviazione dati** . Nella schermata visualizzata, seleziona **+          Contenitore **. Assegna al contenitore il nome dati di esempio e lascia il livello di accesso pubblico predefinito.
  4. Dopo aver creato il tuo contenitore, fai clic su di esso. Quindi seleziona il pulsante Carica per selezionare i file .txt scaricati in precedenza.
  
  
### Crea un progetto di classificazione personalizzato
  1. Accedi a Language Studio . Apparirà una finestra che ti consentirà di selezionare il tuo abbonamento e la risorsa Lingua. Seleziona la risorsa che hai creato nel passaggio      precedente.
  2. Nella sezione **Classifica testo** di Language Studio, seleziona la **classificazione del testo personalizzata** dai servizi disponibili e selezionala.
 
  3. Seleziona **Crea nuovo progetto** (nome da inserire nel file config.py) dal menu in alto nella pagina dei tuoi progetti. La creazione  di un progetto ti consentirà di            etichettare i dati, addestrare, valutare, migliorare e distribuire i tuoi modelli.
  4. Se hai creato la tua risorsa utilizzando i passaggi precedenti, il passaggio di **archiviazione Connect** sarà già completato. In caso contrario, devi assegnare ruoli per        il tuo account di archiviazione prima di connetterlo alla tua risorsa.
 
        - La tua risorsa ha il ruolo di **proprietario (owner) o collaboratore (contributor)** nell'account di archiviazione
        - La risorsa ha il ruolo di **proprietario dei dati del BLOB (Storage blob data owner) di archiviazione o collaboratore (Storage blob data contributor)** dei dati del             BLOB di archiviazione nell'account di archiviazione.
        - La tua risorsa ha il ruolo di **lettore (Reader)** nell'account di archiviazione.
        
Per impostare i ruoli appropriati nel tuo account di archiviazione:
- Vai alla pagina del tuo account di archiviazione nel portale di Azure.
- Seleziona **Controllo accessi (IAM)** nel menu di navigazione a sinistra.
- Seleziona **Aggiungi per aggiungere assegnazioni** di ruolo e scegli il ruolo appropriato per la tua risorsa Lingua.
- Seleziona **Identità gestita** in Assegna accesso a.
- Seleziona **Membri** e trova la tua risorsa. Nella finestra che appare, seleziona il tuo abbonamento e **Lingua** come identità gestita. È possibile cercare i nomi               utente nel campo. Seleziona. Ripetere l'operazione per tutti i ruoli.

	
 5. Seleziona il tipo di progetto. Per questo avvio rapido, creeremo un progetto di classificazione multietichetta in cui è possibile assegnare più classi allo stesso file.         Quindi fare clic su Avanti . Ulteriori informazioni sui tipi di progetto
 
  
 6. Inserisci le informazioni sul progetto, inclusi un nome, una descrizione e la lingua dei file nel tuo progetto. Non potrai modificare il nome del tuo progetto in un             secondo momento.
      - Consiglio: Il tuo set di dati non deve essere interamente nella stessa lingua. Puoi avere più file, ognuno con diverse lingue supportate. Se il tuo set di dati                   contiene file di lingue diverse o se prevedi lingue diverse durante il runtime, seleziona abilita set di dati multilingue quando inserisci le informazioni di base per il         tuo progetto.
      
 7. Seleziona il contenitore in cui hai caricato i tuoi dati. Quando ti viene chiesto se i tuoi file sono già contrassegnati da classi, seleziona Sì e scegli il file                 disponibile. Quindi fare clic su **Avanti** .
   9. Rivedi i dati inseriti e seleziona **Crea progetto**.
  
### Allena il tuo modello
In genere, dopo aver creato un progetto, importare i dati e iniziare a contrassegnare le entità al suo interno per addestrare il modello di classificazione. Per questo avvio rapido, utilizzerai il file di dati con tag di esempio scaricato in precedenza e archiviato nell'account di archiviazione di Azure.

Un modello è l'oggetto di apprendimento automatico che verrà addestrato per classificare il testo. Il tuo modello imparerà dai dati di esempio e sarà in grado di classificare i ticket di supporto tecnico in seguito.

Per iniziare ad addestrare il tuo modello:
  1. Seleziona **Train** dal menu a sinistra.
  2. Seleziona **Addestra** un nuovo modello e digita il nome del modello nella casella di testo          sottostante.
  3. Clicca sul pulsante **Train** in fondo alla pagina.

### Deploy il tuo modello
In genere, dopo aver addestrato un modello, dovresti rivedere i suoi dettagli di valutazione e apportare miglioramenti se necessario. In questo avvio rapido, distribuirai semplicemente il tuo modello e lo renderai disponibile per la tua prova.

Dopo che il tuo modello è stato addestrato, puoi distribuirlo. La distribuzione del modello ti consente di iniziare a utilizzarlo per classificare il testo, utilizzando Analyze API .

 1. Seleziona Distribuisci modello dal menu a sinistra.

 2. Seleziona il modello che desideri distribuire, quindi seleziona Distribuisci modello .

### Metti alla prova il tuo modello
Dopo aver distribuito il modello, puoi iniziare a usarlo per la classificazione del testo. Utilizzare i seguenti passaggi per inviare la prima richiesta di classificazione del testo.

  1. Seleziona **Modello di prova** dal menu a sinistra.

  2. Seleziona il modello che vuoi testare.

  3. Utilizzando uno dei file scaricati in precedenza, aggiungi il testo del file alla casella di          testo. Puoi anche caricare un .txtfile.

  4. Fare clic su **Esegui il test**.

  5. Nella scheda **Risultato** , puoi vedere le classi previste per il tuo testo. Puoi anche                  visualizzare la risposta JSON nella scheda **JSON **.
 
 Per ulteriori informazioni visitare il link seguente: https://docs.microsoft.com/en-us/azure/cognitive-services/language-service/custom-classification/quickstart?pivots=language-studio
 
Dopo aver addestrato il modelli, distribuito e testato inserire nel file config.py endpoint, chiave, nome del progetto e nome del deploy.
1. Vai alla pagina della panoramica delle risorse nel portale di azure
2. Dal menu sul lato sinistro, seleziona **Chiavi ed Endpoint** . Utilizzerai l'endpoint e la  chiave per le richieste API

     
### Guida all'esecuzione
Per potere utillizare il servizio si è utilizzato l'sdk. Nel seguente link https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_multi_category_classify.py c'è il codice che permette di usufruire del servizio 

   


richieste nel service lingua creato 
AZURE_TEXT_ANALYTICS_ENDPOINT = "https://westeurope.api.cognitive.microsoft.com/")
ed la chiave 1

###file json di configurazione



#servizio translate

nome che andrà nel file config endpoint
piano tariffario Standard S1

copiare in chiavi ed endpoint il campo traduzione documento che andrà a finire nel file config
copiare key 1 




### Azure SQL

Per creare un database singolo nel portale di Azure, questo argomento di
avvio rapido inizia dalla pagina SQL di Azure.

1.  Passare alla pagina Selezionare l’opzione di distribuzione SQL.
2.  In **Database SQL** lasciare l'opzione **Tipo di risorsa** impostata
    su **Database singolo** e selezionare **Crea**.
3.  Nella scheda **Informazioni di base** del modulo **Crea database
    SQL** selezionare la **Sottoscrizione** di Azure corretta
    in **Dettagli del progetto**.
4.  In **Gruppo di risorse** selezionare il gruppo di risorse creato
    precedentemente e quindi fare clic su **OK**.
5.  In **Nome database** immettere *mySampleDatabase*.
6.  In **server** selezionare **Crea nuovo** e compilare il
    modulo **Nuovo server** con i valori seguenti:

    1.  **Nome server**: immettere *mysqlserver* e aggiungere alcuni
        caratteri per l'univocità. Non è possibile specificare un nome
        di server esatto da usare perché i nomi di tutti i server di
        Azure devono essere univoci a livello globale, non solo univoci
        all'interno di una sottoscrizione. Immettere quindi un valore
        come mysqlserver12345 e il portale segnala se è disponibile
        o meno.
    2.  **Account di accesso amministratore server**:
        digitare *azureuser*.
    3.  **Password**: immettere una password che soddisfi i requisiti e
        immetterla di nuovo nel campo **Conferma password**.
    4.  **Località**: selezionare una località dall'elenco a discesa.
    5.  Selezionare **OK**.

7.  Lasciare l'opzione **Usare il pool elastico SQL?** impostata
    su **No**.
8.  In **Calcolo e archiviazione** selezionare **Configura database**.
9.  Questo argomento di avvio rapido usa un database serverless, quindi
    selezionare **Serverless** e quindi **Applica**.
10. Selezionare Avanti: Rete nella parte inferiore della pagina.
11. Nella scheda Rete selezionare Endpoint pubblico in Metodo
    di connettività.
12. In Regole del firewall impostare Aggiungi indirizzo IP client
    corrente su Sì. Lasciare l'opzione Consenti alle risorse e ai
    servizi di Azure di accedere a questo server impostata su No.
13. Selezionare Avanti: Impostazioni aggiuntive nella parte inferiore
    della pagina.
14. In Regole del firewall impostare Aggiungi indirizzo IP client
    corrente su Sì. Impostare **consenti** alle risorse e ai servizi di
    Azure di accedere a questo server su Si.
15. Selezionare Rivedi e crea.
16. Selezionare **Crea.**


Nel file databaseManager.py inserire i parametri di configurazione
corretti per l’utilizzo del database.




### Function App

Per creare la function app per effettuare scraping da Visual Studio
Code:

1.  Aprire la cartella **Scraping** in Visual Studio Code
2.  Su command palette di VS Code eseguire il comando **Azure Function:
    Deploy to Function App…**
3.  Seguire la procedura guidata ricordando di selezionare **HTTP
    trigger** per l’attivazione della funzione.
4.  Conservare l’endpoint fornito alla fine della fase di deploy ed
    inserirlo nel file *config.py *del bot.

inserire all'interno del variabili d'ambiente id sottoscrizione (per provarlo in locale)
	
	
## Guida all'esecuzione

Il bot può essere testato in locale utilizzando Bot Framework Emulator e ngrok.

### Local hosting
#### Testare il bot utilizzando Bot Framework Emulator
1. Avviare il debug su VS Code
2. Avviare Bot Framework Emulator e selezionare 'Open Bot'.
3. Inserire i campi richiesti:
    * Bot URL: `http://localhost:3978/api/messages`
    * Microsoft App ID: presente nel file config.py
    * Microsoft App password: presente nel file config.py

#### Testare il bot su Telegram
Creare un nuovo bot per Telegram e nella sezione Canali del servizio bot configurare il bot inserendo il token.
1. Avviare ngrok
```sh
$ ./ngrok http -host-header=rewrite 3978
```
2. Recarsi nella sezione Impostazioni del servizio bot ed inserire come endpoint di messaggistica l'indirizzo https generato da ngok.
3. Testare il bot utilizzando Telegram.

### Cloud Hosting
1. Eseguire il deploy della web app utilizzando l'estensione per VS Code.
2. Assicurarsi che l'endpoint del servizio bot sia corretto (se è stato modificato). 
3. A questo punto è possibile testare il bot utilizzando Telegram o la web chat su Azure.


distribuisci azure: az webapp deployment source config-zip --resource-group "ArchiveCategoryBot-RG" --name "newWebappname" --src "C:\Users\manlio\Desktop\Archive_Category-main.zip"
