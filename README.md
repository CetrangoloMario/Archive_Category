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
    comando
```sh
az login
```

1.  Impostare la sottoscrizione predefinita da usare
```sh
az account set --subscription "&lt;azure-subscription&gt;"
```
1.  Creare la registrazione dell’applicazione con il comando
```sh
az ad app create --display-name "displayName" --password "AtLeastSixteenCharacters_0" --available-to-other-tenants```
È necessario registrare i valori** appID** e **secret** dopo
l’esecuzione del comando precedente. Vengono utilizzati nel comando successivo

### Servizio dell’applicazione bot

Eseguire distribuzione tramite modello arm con un nuovo gruppo di risorse
az deployment sub create --template-file "<path-to-template-with-new-rg.json" --location <region-location-name> --parameters appId="<app-id-from-previous-step>" appSecret="<password-from-previous-step>" botId="<id or bot-app-service-name>" botSku=F0 newAppServicePlanName="<new-service-plan-name>" newWebAppName="<bot-app-service-name>" groupName="<new-group-name>" groupLocation="<region-location-name>" newAppServicePlanLocation="<region-location-name>" --name "<bot-app-service-name>"

""esempio""
az deployment sub create --template-file "C:\Users\cetra\Desktop\cloud\Progetto\Archive_Category\deploymentTemplates\template-with-new-rg.json" --location westeurope --parameters appId="appid" appSecret="password" botId="ArchiveCategoryBot" botSku=F0 newAppServicePlanName="appservicebot" newWebAppName="newWebappname" groupName="ArchiveCategoryBot-RG" groupLocation="westeurope" newAppServicePlanLocation="westeurope" --name "ArchiveCategoryBot" 
------------------------------------------------


Copiare il valore di **ID applicazione (client)** e salvarlo in
    un file.
------------------------------------------------

Assegnare ID app e password nel file config.py
---------------------------------------------------


Creare il provider Azure AD identity
Questa sezione illustra come creare un provider Azure AD di identità che usa OAuth2 per autenticare il bot. È possibile usare endpoint Azure AD v1 o Azure AD v2.
 Suggerimento

È necessario creare e registrare l'applicazione Azure AD in un tenant in cui sia possibile dare il consenso per delegare le autorizzazioni richieste da un'applicazione.
Aprire il pannello Azure Active Directory nel portale di Azure. Se non ci si trova nel tenant corretto, fare clic su Cambia directory per passare al tenant corretto. Per istruzioni sulla creazione di un tenant, vedere Accedere al portale e creare un tenant.
Aprire il pannello Registrazioni per l'app.
Nel pannello Registrazioni per l'app fare clic su Nuova registrazione.
Compilare i campi obbligatori e creare la registrazione per l'app.
Assegnare un nome all'applicazione.
Selezionare le opzioni per Tipi di account supportati per l'applicazione. Tutte queste opzioni sono appropriate per questo esempio.
Per URI di reindirizzamento
Selezionare Web.
Impostare l'URL su https://token.botframework.com/.auth/web/redirect.
Fare clic su Register.
Dopo la creazione, Azure visualizza la pagina Panoramica per l'app.
Registrare il valore di ID applicazione (client) . Questo valore verrà utilizzato in un secondo momento come ID client quando si crea la stringa di connessione e si registra il provider Azure AD con la registrazione del bot.
Registrare anche il valore di ID della directory (tenant) . Verrà anche utilizzato per registrare l'applicazione provider con il bot.


Nel riquadro di spostamento fare clic su Certificati e segreti per creare un segreto per l'applicazione.
In Segreti client fare clic su Nuovo segreto client.
Aggiungere una descrizione per identificare questo segreto rispetto ad altri che potrebbero essere necessari per creare per l'app, ad esempio bot login.
Impostare Scadenza su Mai.
Scegliere Aggiungi.
Prima di chiudere questa pagina, registrare il segreto. Questo valore verrà usato successivamente come segreto client quando si registra l'applicazione Azure AD con il bot.


Nel riquadro di spostamento fare clic su Autorizzazioni API per aprire il pannello Autorizzazioni API. È consigliabile impostare in modo esplicito le autorizzazioni API per l'app.
Fare clic su Aggiungi un'autorizzazione per visualizzare il riquadro Richiedi le autorizzazioni dell'API.
Per questo esempio selezionare API Microsoft e Microsoft Graph.
Scegliere Autorizzazioni delegate e assicurarsi che le autorizzazioni necessarie siano selezionate. Questo esempio richiede queste autorizzazioni.
 Nota

Qualsiasi autorizzazione contrassegnata come CONSENSO AMMINISTRATORE OBBLIGATORIO richiederà l'accesso sia dell'utente che dell'amministratore del tenant, quindi cercare di evitare tali autorizzazioni per il bot.
openid
profile
Mail.Read
Mail.Send
User.Read
User.ReadBasic.All
Fare clic su Aggiungi autorizzazioni. La prima volta che un utente accede a questa app tramite il bot, sarà necessario concedere il consenso.
-------------------------------------

Registrare il Azure AD identity provider con il bot
Il passaggio successivo consiste nel registrare l'applicazione Azure AD appena creata con il bot.


Azure AD v2
Passare alla pagina di registrazione ai canali bot del bot nel portale di Azure.
Fare clic su Impostazioni.
Sotto OAuth Connection Settings (Impostazioni di connessione OAuth) nella parte inferiore della pagina fare clic su Aggiungi impostazione.
Compilare il modulo come segue:
Nome. immettere un nome per la connessione. Sarà usato nel codice del bot.
Provider di servizi. Selezionare Azure Active Directory v2. Quando si seleziona questa opzione, vengono visualizzati i campi specifici di Azure AD.
ID client. Immettere l'ID applicazione (client) registrato per il provider di identità Azure AD v2.
Segreto client. Immettere il segreto registrato per il provider di identità Azure AD v2.
URL Exchange token. Lasciare vuoto perché viene usato solo per l'accesso SSO Azure AD versione 2.
ID tenant. Immettere l'ID della directory (tenant) registrato in precedenza per l'app AAD o comune a seconda dei tipi di account supportati selezionati al momento della creazione dell'app Azure DD. Per decidere quale valore assegnare, seguire questi criteri:
Se durante la creazione dell'app Azure AD è stata selezionata l'opzione Account solo in questa directory dell'organizzazione (Solo Microsoft - Tenant singolo) , immettere l'ID tenant registrato in precedenza per l'app AAD.
Se invece è stata selezionata l'opzione Account in qualsiasi directory organizzativa (qualsiasi directory di Azure AD - Multi-tenant e account Microsoft personali, ad esempio Xbox, Outlook.com) oppure Account in qualsiasi directory dell'organizzazione (qualsiasi directory di Azure AD - Multi-tenant) , immettere il termine common invece di un ID tenant. In caso contrario, l'app AAD verificherà il tenant il cui ID è stato selezionato ed escluderà gli account MS personali.
Questo sarà il tenant associato agli utenti che possono essere autenticati. Per altre informazioni, vedere Tenancy in Azure Active Directory.
In Ambiti immettere i nomi dell'autorizzazione scelta dalla registrazione dell'applicazione. A scopo di test, è sufficiente immettere: openid profile .

 Nota

Per Azure AD versione 2, il campo Ambiti accetta un elenco di valori che distinguono tra maiuscole e minuscole, separati da spazi.
Fare clic su Salva.
 Nota

Questi valori consentono all'applicazione di accedere ai dati di Office 365 tramite l'API Microsoft Graph. Il campo URL scambio di token deve essere lasciato vuoto perché viene usato per SSO solo in Azure AD V2.
Testare la connessione
Fare clic sulla voce di connessione per aprire la connessione appena creata.
Fare clic su Test connessione nella parte superiore del riquadro delle impostazioni di connessione del provider di servizi.
La prima volta si dovrebbe aprire una nuova scheda del browser che elenca le autorizzazioni che l'app richiede e chiede di accettarle.
Fare clic Accept.
Verrà visualizzata la pagina Test connessione a <your-connection-name> riuscito.
Ora è possibile usare questo nome di connessione nel codice bot per recuperare i token dell'utente.
-----------------------------------


### Creazione servizio machine learning
**Prerequisiti**

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
