# Zabbix Syntax
## Calculated Items

* Item > Formula
```
last(otrs.tickets.pendingthirdparty) 
+ last(otrs.tickets.pendingcustomer) 
+ last(otrs.tickets.pendingclose) 
+ last(otrs.tickets.pendingreminder)
```

