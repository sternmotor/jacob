# Bash Input/output

Securely ask for password
```bash
# get admin password for firewall interactively
echo -n 'Enter firewall "admin" user password: '
Prompt=''
while IFS= read -p "$Prompt" -r -s -n 1 char
do
    # Enter - accept password
    if [[ $char == $'\0' ]] ; then
        break
    fi
    # Backspace
    if [[ $char == $'\177' ]] ; then
        Prompt=$'\b \b'
        AdminPassword="${AdminPassword%?}"
    else
        Prompt='*'
        AdminPassword+="$char"
    fi
done
echo
```
