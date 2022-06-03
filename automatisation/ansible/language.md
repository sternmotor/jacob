# Ansible language


Handle bool variables in jinja files

```
{{ 'yes' if nscd_netgroup_enable_cache|bool else 'no' }}
```

Special tags

* `['never', 'debug']` : run only when 'debug' tag is specified
* `['always', 'debug']` : run unless `--skip-tags always` is specified



