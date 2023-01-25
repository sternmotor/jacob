# Atlassian jira hints

## Filters

Project filter with nested sorting:

    project = AD AND NOT ((status = Geschlossen OR status = Abgelehnt OR status = Fertig) AND updated > -100d )   ORDER BY priority DESC, created DESC


## Comments


Editor keyboard shortcuts

* `/`: Suche
* `a`: assign issue / Vorgang zuweisen
* `c`: create issue / Vorgang erstellen
* `m`: write comment / Kommentar erstellen
* `?`: Keyboard shortcut help
* `g a`: Board view ("go agile")
* `g i`: Show issues/ Vorgänge anzeigen
* `g d`: Show dashboard
* `z`: clear issue view / fokussierte Darstellung von Vorgängen


## General

* After 8h each Jira session will be terminated.
* View all filters or dashboards: search (magnifying glass top right or "/"), below you will find several things, all of them will be displayed
* Set start view (tickets, dashboards or boards): Top right User > Personal Settings > Jira Start Page.
* Set personal notifications: Top right User > Personal Settings > Notifications
