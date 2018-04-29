# Traceroute
A [traceroute](https://en.wikipedia.org/wiki/Traceroute) implemented in [Python 2.7](https://www.python.org/download/releases/2.7/).

![Demo](https://i.imgur.com/xsQ4GXX.png)

## Usage

You must have [Python 2.7](https://www.python.org/download/releases/2.7/) and [sudo](https://www.sudo.ws/) access.

To download and run the program, use the following commands:

```
git clone https://github.com/terindhadda/traceroute.git
cd traceroute
sudo python traceroute.py www.google.com
```

You can also use the following options:

* `--port` or `-p` to specify the port (default is 33434)
* `--max-hops` or `-m` to specify the maximum number of hops (default is 30 hops)
* `--timeout` or `-t` to specify the timeout in seconds (default is 5 seconds)
