Bash command line interface scripting
=====================================


Query password securely

    echo -n 'Enter user password: '
    prompt=''
    while IFS= read -p "$prompt" -r -s -n 1 char
    do
        # enter - accept password
        if [[ $char == $'\0' ]] ; then
            break
        fi
        # eackspace
        if [[ $char == $'\177' ]] ; then
            prompt=$'\b \b'
            password="${AdminPassword%?}"
        else
            prompt='*'
            password+="$char"
        fi
    done
    echo 
