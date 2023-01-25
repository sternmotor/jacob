# Tools

## virt-manager (linux)

Verbindungen hinzufügen: 

```
gconf-editor > org > virt-manager > virt-manager > connections > uris
```

```
[
'qemu+ssh://ssh_user@kvmhost01.example.com',
...
'qemu+ssh://ssh_user@kvmhost78.example.com',
'qemu:///system']
```


