## Secure your servers using iptables
`iptables` is a highly flexible firewall utility built for Linux operating systems. It allows you to define various rules for the incoming and outgoing connections. For example, you could instruct `iptables` to only accept connections from specific ports such as 80, 443, and 22, and neglect any other ports.

> You can also instruct `iptables` to allow/deny certain ip addresses as well.  

## Installation
The very first thing to do is to install `iptables`, on Ubuntu you may run:
```bash
sudo apt-get install -y iptables iptables-persistent
```

By default, `iptabels` rules will be saved in the RAM, which means they will be lost in the next restart, Fortunately, there is an easy way to persist the rules using the `iptables-persistent` package (we’ll see that later in the post).

## Understanding the basics
`iptables` uses the chains concept, the chain contains a set of rules. There are three chains defined by default:
* **INPUT**: Traffic inbound to the server.
* **FORWARD**: Traffic forwarded (routed) to other locations.
* **OUTPUT**: Traffic outbound from the server.

For example, if you want to allow port 80, then you must append a rule in the `INPUT` chain instructing `iptables` to allow port 80.

Let’s list the rules in all the chains:
```bash
sudo iptables -L -v
```

You should get the following output:
```text
Chain INPUT (policy ACCEPT 9 packets, 636 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 5 packets, 568 bytes)
 pkts bytes target     prot opt in     out     source               destination
```

The output shows that we have no rules defined for any of the chains.

In addition to chains, `iptables` uses two policies to allow/block traffic:
* `ACCEPT`.
* `DROP`.

Let me explain policies in a simplified way.

What do you want `iptables` to do if the connection doesn’t match any of the existing rules?

For example, if you’ve allowed connections from port 80, 443 and 22, then what would you do if somebody tries to access your server through port 8800?

The default policy is `ACCEPT`, which means allowing all the connections that don’t match any of the existing rules. But that’s an insecure behaviour.

Changing the default policy to `DROP` allows us to have more control over the connections, so we just accept the ones that we need through the rules.

## Avoid self-blocking
It’s imperative to avoid what’s so-called self-blocking in `iptables`.

Self-blocking happens when we block the network traffic by adding some rules, but those rules will not be applied to the current **established** and **related** incoming/outgoing traffic.

For example, if you change the policy to `DROP` without allowing the established connections, then you’ll be kicked out of the server.

Please be aware that if you persist the `iptables` rules, then there is no way to connect to the server again.

> It’s **mandatory** to follow the instructions/commands in this post in order.  

SSH to your server and run the following commands:
```bash
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

sudo iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT
```

Now, you should be safe, this means that all the established connections remain intact.

## Loopback Network
Time to create some rules:
```bash
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT
```

This command tells `iptables` to accept loopback connections so that the server can send/receive anything from `127.0.0.1/localhost`; this is useful if you have some services that reside on the same server; for example, MySQL, Redis, etc.…

> By default, MySQL uses `127.0.0.1` in the `bind-address` flag to know from where it should listen for connections. Read more about `bind-address` [here](https://serversforhackers.com/c/mysql-network-security).  

Let’s demystify the commands:
* `-A INPUT`: appends a new rule to the `INPUT` chain.
* `-i lo`: the network interface, `lo` means the loopback network.
*  `-j ACCEPT`: accept the connection.

## Allowing Specific Ports
Let’s continue defining more rules:
```bash
## Accept connections from port 22 (SSH)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

## Accept connections from port 80 (HTTP)
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT

## Accept connections from port 443 (HTTPS)
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

This time, we used the `—dport` flag to specify a port number, you can also use the `-s` flag for ip addresses:
```bash
## Block an IP address 
sudo iptables -A INPUT -s 210.10.85.65 -j DROP
```

We’ve defined a few rules, perfect, so now, we can safely instruct `iptables` to change the default policy to `DROP`:
```bash
sudo iptables -A INPUT -j DROP
```

Persist the rules:
```bash
sudo service netfilter-persistent save
sudo service netfilter-persistent restart
```

## Flushing 
You can easily flush (*remove*) all the rules by running the following commands:
```bash
sudo iptables -F INPUT
sudo iptables -F OUTPUT
sudo iptables -F FORWARD
```

## Where to go from here?
If you want to know more about `iptables` consider reading the following article:
[Iptables Essentials: Common Firewall Rules and Commands | DigitalOcean](https://www.digitalocean.com/community/tutorials/iptables-essentials-common-firewall-rules-and-commands)
