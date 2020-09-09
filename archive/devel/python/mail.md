# Python mail handling

Get mailbox contents
```
import imaplib 
import email    
import email.header
FOLDER = 'TraSo/Nagios'
    

def get_mails():
    m = imaplib.IMAP4_SSL('mail.traso.de')
    m.login('mann', 'xxxx')
    m.select(FOLDER)
    
    result, data = m.search(None, 'ALL')

    if result != 'OK':
        print('No messages found')
    else:
        for mail_id in data[0].split():
            result, data = m.fetch(mail_id, '(RFC822)')
            if result != 'OK':
                print('Error reading message "{0}"'.format(mail_id))
            msg = email.message_from_bytes(data[0][1])
            hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
            yield str(hdr).replace('\r\n','')
```
