Some servers limit the incoming network connections to a certain amount, such as 128.

Limiting the incoming network connections could significantly impact the performance of your server, so it doesn’t accept more than the specified number of connections even though you have a powerful server that can handle thousands of connections simultaneously.

Linux uses the `somaxconn` config to limit the number of incoming connections.

The value of `somaxconn` might vary from one distribution to another; in Ubuntu, the default value is `4096` connections.

Run the following command to know the default value of `somaxconn` on your server:
```bash
sysctl net.core.somaxconn
```

Anyway, let’s do some benchmarking.

> Please install [Apache Benchmark](https://httpd.apache.org/docs/2.4/programs/ab.html)on your machine.   

First of all, let’s change the value of `somaxconn` to 100:

```bash
echo 100 > /proc/sys/net/core/somaxconn

# remember to reload nginx
sudo service nginx reload
```

Then, use Apache Benchmark to send 500 requests:

```bash
ab -n 500 -l -c 150 -k -H "Accept-Encoding: gzip, deflate" http://example.com/
```

Here, I’m sending 500 requests with 150 concurrent connections.

> `-c` *concurrency*: Number of multiple requests to perform at a time.  


Result:

```text
Concurrency Level:      120
Time taken for tests:   5.215 seconds
Complete requests:      500
Failed requests:        0
Non-2xx responses:      373
Keep-Alive requests:    373
Total transferred:      1280928 bytes
HTML transferred:       1039564 bytes
Requests per second:    95.88 [#/sec] (mean)
Time per request:       1251.513 [ms] (mean)
Time per request:       10.429 [ms] (mean, across all concurrent requests)
Transfer rate:          239.88 [Kbytes/sec] received
```

As you might have noticed, I made 500 requests, but only 127 requests have been executed successfully. The rest, which is 373, failed.

> The `Non-2xx responses` shows the total number of the requests that return less than 200 status code in their responses.  

If you try to access the website through a web browser, you might encounter a `502 Bad Gateway` because Nginx can’t handle more connections.

## Increase the incoming connections
This time, let’s increase the incoming connections to `1000`:
```bash
 echo 1000 > /proc/sys/net/core/somaxconn
```

And then let’s execute the same benchmarking command, but with 1000 requests instead of 500:
```bash
ab -n 1000 -l -c 200 -k -H "Accept-Encoding: gzip, deflate" http://157.90.226.65/usr
```

Result:
```text
Concurrency Level:      200
Time taken for tests:   39.830 seconds
Complete requests:      1000
Failed requests:        0
Keep-Alive requests:    0
Total transferred:      9066911 bytes
HTML transferred:       7698000 bytes
Requests per second:    25.11 [#/sec] (mean)
Time per request:       7966.077 [ms] (mean)
Time per request:       39.830 [ms] (mean, across all concurrent requests)
Transfer rate:          222.30 [Kbytes/sec] received
```

This time all the 1000 request were succeed.

If you restart your server, then the value of the `somaxconn` will be lost, so to persist it, let’s create a new configuration file in `/etc/sysctl.d/` folder:

```bash
echo "net.core.somaxconn=10000" > /etc/sysctl.d/network-tunning.conf
```

As you might have noticed, this time I increased the value of `somaxconn` to 10.000, which should be fine.

I hope you enjoyed reading this short post.