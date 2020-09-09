# PHP code zur Server-Administration

Mail versenden

```
# bool mail ( string $to , string $subject , string $message [, mixed $additional_headers [, string $additional_parameters ]] )
# -f parameter sets return path
echo "<? mail('<receiver>','<subject>','<message>','From:<sender>', '-f<receiver>');"|php
```

