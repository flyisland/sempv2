# Project Name

Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2

### Todo

- [ ] Click with sub-command options  
- [ ] add --include-password to  enable/disable whether to update the read-only property "password"  
- [ ] Tools, auto generate definition fils from  SEMPv2 open api  
- [ ] Add --showDefault to Backup command to show  all properties even with default value  
- [ ] Add definition of "mqttRetainCaches"  
- [ ] Add definition of "mqttSessions"  
- [ ] Add definition of "queueTemplates"  
- [ ] Add definition of "replayLogs"  
- [ ] Add definition of "replicatedTopics"  
- [ ] Add definition of "sequencedTopics"  
- [ ] Add definition of "topicEndpointTemplates"  
- [ ] Add definition of "topicEndpoints"  

### In Progress


### Done ✓

- [x] Add Update command, compare the JSON file with online VPN, and perform actions only needed.  
- [x] Add  --curl to Restore command to generate curl  command line  
- [x] Add definition of "authorizationGroups"  
- [x] Add definition of "authenticationOauthProviders"  
- bug: Not allowed to modify the trusted common name list while the consumer is enabled. 2019-09-03  
- support "nextPageUri" in the response 2019-09-02  
- add template support for config file 2019-08-15  
- don't touch "Names starting with '#' are reserved" in backup, restore and delete 2019-08-15  
- remove elements with empty body 2019-08-14  
- remove properties with default value 2019-08-14  
- Add delete support 2019-08-14  

