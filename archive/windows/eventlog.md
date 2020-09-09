EVENT INFORMATIONEN FÜR PROGRAMM-AKTION❌
Scheduled Tasks können per Event getriggert werden. Wird als Aktion "Programm starten" ausgewählt, können hier Event-spezifische Daten als Parameter übergeben werden. 

Zum Beispiel: 

zbxsend windows.backup.lastevent $(EventID)
Um $(EventID) verwenden zu können, muss im exportieren Task-XML folgender Eintrag eingefügt werden, bevor der Task wieder importiert wird:

<Triggers>
    <EventTrigger>
        ...
        <ValueQueries>
            <Value name="EventID">Event/System/EventID</Value>
        </ValueQueries>
    </EventTrigger>
</Triggers>
Die verfügbaren  "Values" bzw. Pfade (z.B. Event/System/Level) können in der Ereignisanzeige beim entsprechenden Event unter "Ereigniseigenschaften" > "Details" > "XML-Ansicht" herausgesucht werden.