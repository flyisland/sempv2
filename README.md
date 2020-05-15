# Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2

## Goals

* [X] Backing up the config of a VPN to a JSON file
* [X] Restore a VPN from a JSON file
* [X] Delete a VPN
* [X] Update the VPN with the configuration file

## Installation

Install the package locally with:

```bash
$ pip install .
```

## Usage

### VPN

Run `sempv2 vpn` to show the help message:

```bash
$ Usage: sempv2 vpn [OPTIONS] COMMAND [ARGS]...

  Backing Up and Restoring Solace PubSub+ VPN

Options:
  --help  Show this message and exit.

Commands:
  backup   Fetches the whole configuration of a VPN
  delete   Delete the VPN
  restore  Restore the VPN with the configuration file
  update   Update the VPN with the configuration file
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
