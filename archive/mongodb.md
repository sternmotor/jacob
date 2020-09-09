# MongoDB

Show size of all databases
```
mongo
db.adminCommand("listDatabases").databases.forEach(function (d) {
    mdb = db.getSiblingDB(d.name);
    printjson(mdb.stats());
})
```
