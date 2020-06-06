# Backing Up and Restoring Solace PubSub+ Configs with SEMPv2

## Goals

* [X] Backing up the config of a VPN or a DMR-cluster to a JSON file
* [X] Restore a VPN or a DMR-cluster from a JSON file
* [X] Delete a VPN or a DMR-cluster
* [X] Update the VPN or DMR-cluster with the configuration file

## Installation

Install the package locally with:

```bash
$ pip install .
```

## Usage

### VPN

Run `sempv2 vpn` to show the help message:

```bash
$ sempv2
Usage: sempv2 [OPTIONS] COMMAND [ARGS]...

  Backing Up and Restoring Solace PubSub+ Configs with SEMPv2 protocol

Options:
  --version                  Show the version and exit.
  -u, --admin-user TEXT      The username of the management user  [default:
                             admin]
  -p, --admin-password TEXT  The password of the management user, could be set
                             by env variable [SOL_ADMIN_PWD]  [default: admin]
  -h, --host TEXT            URL to access the management endpoint of the
                             broker  [default: http://localhost:8080]
  --curl-only                Output curl commands only, no effect on BACKUP
                             command  [default: False]
  -v, --verbose              Enables verbose mode.
  --help                     Show this message and exit.

Commands:
  cluster  Backing Up and Restoring the Setting of PubSub+ DMR Cluster
  vpn      Backing Up and Restoring the Setting of PubSub+ VPN

$ sempv2 vpn --help
Usage: sempv2 vpn [OPTIONS] COMMAND [ARGS]...

  Backing Up and Restoring the Setting of PubSub+ VPN

Options:
  --help  Show this message and exit.

Commands:
  backup   Fetches the whole configuration of a VPN
  delete   Delete the VPN
  restore  Restore the VPN with the configuration file
  update   Update the VPN with the configuration file

$ sempv2 cluster --help
Usage: sempv2 cluster [OPTIONS] COMMAND [ARGS]...

  Backing Up and Restoring the Setting of PubSub+ DMR Cluster

Options:
  --help  Show this message and exit.

Commands:
  backup   Fetches the whole configuration of a Cluster
  delete   Delete the Cluster
  restore  Restore the Cluster with the configuration file
  update   Update the Cluster with the configuration file
```

## Jinja2 Template

`sempv2` supports [Jinja2](https://jinja.palletsprojects.com) template in the configuration json file, so you could create 10 queues as below:

```json
    "queues": [
{% for n in range(1,10) %} 
        {
            "egressEnabled": true,
            "ingressEnabled": true,
            "maxMsgSpoolUsage": 1500,
            "permission": "no-access",
            "queueName": "q{{n}}"
        },
{% endfor %}
```

## Reference

* [Solace Element Management Protocol](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html)
