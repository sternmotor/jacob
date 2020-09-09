# Bash file handling

Compress folder ignoring git files
```bash
tar --exclude-vcs -cjpf /srv/delme.tbz2 *
```

Move file to back with ISO time stamp
```bash
mv 1.bin{,.bak_$(date -Iseconds)}
```
