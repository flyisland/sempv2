# Project Name

Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2

### Todo

- [ ] Problem with DELETE: Cannot delete the ACL profile because there are client-usernames configured against it in not shutdown state  
- [ ] update: ask user for confirmation before deleting objects  
- [ ] new script to build a cluster consist of multiple borkers with one config file  

### In Progress


### Done ✓

- [x] generate definitions from online spec  
- [x] Add --showDefault to Backup command to show  all properties even with default value  
- [x] Tools, auto generate definition fils from  SEMPv2 open api  
- [x] Add definition of "topicEndpoints"  
- [x] Add definition of "topicEndpointTemplates"  
- [x] Add definition of "sequencedTopics"  
- [x] Add definition of "replicatedTopics"  
- [x] Add definition of "replayLogs"  
- [x] Add definition of "queueTemplates"  
- [x] Add definition of "mqttSessions"  
- [x] Add definition of "mqttRetainCaches"  
- [x] add --update-password to  enable/disable whether to update the read-only property "password"  
- [x] Click with sub-command options  
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

