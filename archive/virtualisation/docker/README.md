In order to avoid the delay in the creation and deletion of the container, you can leave the container running for faster execution.

Dockerfile:
```
CMD tail -f /dev/null
```

start container like 
```
if <container-run>
then
    docker exec -t vim /run.sh
else
    docker run --rm -d -v $PWD:/home --name vim ...
    docker exec -t vim /run.sh
fi
```


