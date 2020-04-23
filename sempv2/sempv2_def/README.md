# JSON Format


```json: aclProfiles.json
{
    "key_names": [
        "aclProfileName"
    ],
    "sub_elements": [
        "clientConnectExceptions",
        "publishExceptions",
        "subscribeExceptions"
    ],
    "built_in_elements_quote_plus": [
        "default"
    ],
    "defaults": {
        "clientConnectDefaultAction": "disallow",
        "publishTopicDefaultAction": "disallow",
        "subscribeTopicDefaultAction": "disallow"
    }
}
```



| Key                          | Memo                                                         |
| ---------------------------- | ------------------------------------------------------------ |
| File name                    | `aclProfiles` is the collection name of this resource in the sempv2 url. |
| key_names                    | the array of key attributes to compose the REST id uri of this resource |
| sub_elements                 | Sub elements of this resource                                |
| built_in_elements_quote_plus | some resource has default objects, like the "default" user of each VPN, which will not accept the DELETE action |
|                              | attribues with default value                                 |