# Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2

## Goals

* [X] Backing up the config of a VPN to a JSON file
* [X] Restore a VPN from a JSON file
* [X] Delete a VPN

## Installation

Install the package locally with:

```bash
$ pip install .
```

## Usage

Run `sempv2` to show the help message:

```bash
Usage: sempv2 [OPTIONS] COMMAND [ARGS]...

  Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2 protocol

Options:
  -u, --admin-user TEXT      The username of the management user  [default:
                             admin]
  -p, --admin-password TEXT  The password of the management user, could be set
                             by env variable [SOL_ADMIN_PWD]  [default: admin]
  -h, --host TEXT            URL to access the management endpoint of the
                             broker  [default: http://localhost:8080]
  --help                     Show this message and exit.

Commands:
  backup   Fetch the whole configuration of a VPN
  delete   Delete the VPN
  restore  Restore the VPN with the configuration file
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
* [How To Package Your Python Code](https://python-packaging.readthedocs.io/en/latest/index.html)
* [Setuptools Integration](https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration)
