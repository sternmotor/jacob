# Logstash filtering

## Debugging logstash

* run in foreground:
```
/usr/share/logstash/bin/logstash "--path.settings" "/etc/logstash" --pipeline.workers 4 --config.reload.automatic --config.reload.interval 2s  
```

* dateparser debugging:
```
echo "Apr 15 15:57:52" | /usr/share/logstash/bin/logstash -e 'input { stdin {} } filter { date { match => [ "message", "MMM d HH:mm:ss", "MMM dd HH:mm:ss"] } }'
```

## Metadata
* Metadata field is not visible after output and cacn be used for filtering

```
filter {
  grok { match => [ "message", "%{HTTPDATE:[@metadata][timestamp]}" ] }
  date { match => [ "[@metadata][timestamp]", "dd/MMM/yyyy:HH:mm:ss Z" ] }
}
```

## Filtering log lines

### "Dissect" fixed elements in line

Mapping example 
```
filter {
 dissect {
   mapping => {
     "message" => "%{timestamp->} %{duration} %{client_address} %{cache_result}/%{status_code} %{bytes} %{request_method} %{url} %{user} %{hierarchy_code}/%{server} %{content_type}"
    }
   remove_field => [“message”]
  }
}
```


### "Grok" filter regular expressions

Debugging grok expressions:
* [Grok construktor](http://grokconstructor.appspot.com/do/match#result)
* [Logstash patterns](https://github.com/logstash-plugins/logstash-patterns-core/blob/master/patterns/grok-patterns)
* [Logstash filter plugins](https://www.elastic.co/guide/en/logstash/current/filter-plugins.html)



Patterns

* WORD - pattern matching a single word
* NUMBER - pattern matching a positive or negative integer or floating-point number
* POSINT - pattern matching a positive integer
* IP - pattern matching an IPv4 or IPv6 IP address
* NOTSPACE - pattern matching anything that is not a space
* SPACE - pattern matching any number of consecutive spaces
* DATA - pattern matching a limited amount of any kind of data
* GREEDYDATA - pattern matching all remaining data

Pattern usage example
```
filter {
    grok {
        match => {
            "message" => "%{NUMBER:timestamp}%{SPACE}%{GREEDYDATA:rest}"
        }
    }
}
```

Performance
* have a look on this [discussion](https://www.elastic.co/blog/do-you-grok-grok)
* Add start and end anchors to grok expression (`^...$`) - prevents from deeper search in case whole line does not match
* do not match anything twice ... filter out timestamp, program first and subsequently care about message content, for example
```
filter {
  grok {
    "match" => { "message" => '^%{IPORHOST:clientip} %{DATA:process_name}\[%{NUMBER:process_id}\]: %{GREEDYDATA:message}$' },
    "overwrite" => "message"
  }
  grok {
    "match" => { "message" => [
      '^%{WORD:word_1} %{WORD:word_2} %{NUMBER:number_1} %{NUMBER:number_2} %{GREEDYDATA:data}$',
      '^%{WORD:word_1} %{NUMBER:number_1} %{NUMBER:number_2} %{NUMBER:number_3} %{DATA:data};%{NUMBER:number_4}$',
      '^%{DATA:data} | %{NUMBER:number}$'
    ]}
  }
)
```

Spit out grok errors
```
output {
  if "_grokparsefailure" in [tags] {
    # write events that didn't match to a file, "input" is name of pipeline
    file { "path" => "/var/log/logstash/errors-input-grok.log" }
  } else {
    elasticsearch { }
  }
}
```
