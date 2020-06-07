# Create a DMR Cluster

## Topology

We'll create a DMR Cluster consist of two brokers, the `Local` and the `Remote`, and there is a internal link from the `Local` and the `Remote`.

    +-------+          +--------+
    | Local +--------->+ Remote |
    +-------+          +--------+

## Variables - vars.j2

First, update the file `vars.j2` according to your setup.

    {% set dmrClusterName="cluster-test" %}
    {% set authenticationBasicPassword = "default" %}
    {% set localNodeName = "29315f44a7eb" %}
    {% set remoteNodeName = "solace01" %}
    {% set remoteAddress = "23.100.94.197" %}

You could have the Node Name of the broker by running `show router-name` in CLI mode.

    29315f44a7eb> show router-name
    
    Router Name:          29315f44a7eb
    Mirroring Hostname:   Yes
    
    Deferred Router Name: 29315f44a7eb
    Mirroring Hostname:   Yes
    
    Unique Id:            07:32:b3:72:f2:b4:7a:62
    
    29315f44a7eb>
    
## How to Run It

    $sempv2 -h localhost -u admin -p admin cluster restore ./cluster-local.json
    $sempv2 -h remotehost -u admin -p admin cluster restore ./cluster-remote.json
