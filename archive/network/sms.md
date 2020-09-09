# Secure SMS sending

Send SMS over SSL-secured Rest API for Password transfer (where email would be a security hole)
* provider: [CM telekom](https://www.cm.com/products/text/sms/) 
* [API documentation](https://docs.cmtelecom.com/bulk-sms) - sending is done via simple Json POST requests
* [Pricing](https://www.cm.com/de-de/dienste/preise/sms)
* API linux curl example:
```bash
    #!/bin/bash -eu

    SMSAPI_ADDR='https://sgw01.cm.nl/json/gateway.ashx'
    SMSAPI_PASS='00000000-0000-0000-0000-000000000000'

    send_sms() {
        # example: send_sms "monitoring" "00491792319160 00491792319161" "all down"

        local FROM="$1"
        local NUMBERS="$2"
        local TEXT="$3"
        
        # assemble json request: auth
        local PostData="
        {
            \"messages\": {
                \"authentication\": { \"producttoken\": \"$SMSAPI_PASS\" },
                \"msg\": [
                    { \"from\": \"$FROM\", \"to\": [
        "
        # add numbers
        for NUMBER in $NUMBERS; do
            PostData="$PostData                        { \"number\": \"$NUMBER\" },"
        done
        PostData="${PostData%,}" # remove last comma to retrieve proper json

        # add body
        PostData="$PostData
                        ],
                        \"body\": { \"content\": \"$TEXT\" }
                    }
                ]
            }
        }"

        # send data
        curl \
            --header 'Content-Type: application/json' \
            --header 'Accept: application/json' \
            --request POST \
            --data "$PostData" \
            "$SMSAPI_ADDR"
    }
```

* API python example:
    ```python
    # assemble API query data
    Message = {
        'from' : args.sender,
        'to' : [{ 'number' : nu} for nu in args.numbers ],
        'body' : {
            'content' : args.message
        },
    }

    Payload = json.dumps( {
            'messages' : {
                'authentication' : {
                    'producttoken' : args.password,
                },
                'msg' : [ Message ],
            }
        }
    )

    # push request to api
    logging.info("""Sending: '{0}' to "{1}" for {2}""".format(
            Payload, args.address, ', '.join(args.numbers)
        )
    )

    RequestHeaders = {
        'Content-Type' : 'application/json',
        'Accept' : 'application/json',
    }
    Response = requests.post(SMSAPI_ADDR, data=Payload, headers=RequestHeaders)

    # evaluate response
    ResponseData = Response.json()
    logging.debug(ResponseData)
    if ResponseData['errorCode'] > 0:
        logging.error('Network connection to "{0}" succeeded but server response is bad'.format(args.address))
        sys.exit(1)
    else:
        logging.info('ok')
    ```
