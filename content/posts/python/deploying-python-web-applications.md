Gunicorn is one of the most popular WSGI HTTP Server for Python web applications.

In this post, I'll be showing you how to run your Python web application by using Gunicorn, Supervisor - as a process manager - and NGINX- as a reverse proxy -.

## Prerequisites
You don't need to be a Python professional to read this post, a basic knowledge of Python could be enough.

I assume you know basic Linux administration like installing packages and using a text editor like vim or nano.

I use Ubuntu 18.04 here, but you are not tied to this version since Gunicorn is available in earlier versions of Ubuntu.

> Gunicorn requires Python version 2.x >= 2.6 or Python 3.x >= 3.4.

## Web Server Gateway Interface
So, what this fancy name is? Gunicorn!!

Gunicorn is a Python WSGI HTTP Server, it's compatible with most Python web frameworks, it's fast and easy to implement.

Hold a sec! what WSGI is? Are you confusing me for the first time? :-o

Well, I'm not, but this is what Gunicorn is :-D so let's talk a bit about WSGI.

Python is a general-purpose programming language, we can create many types of applications by using Python, something like a web application, desktop application, mobile application, etc...

If we are writing a web application then we need a webserver to handle our application's HTTP requests, the web server itself doesn't understand or know anything about our application, all it knows is to send/receive HTTP requests:

![Web Server](/static/img/python/deploying-flask-application/001.png)

It's too simple, and actually, this is how HTTP protocol works, our application receives an HTTP request and responds by an HTTP response.

Most of the web servers are written in C/C++, therefore, they cannot run Python code - or any other programming language - directly, this means that an intermediate layer is needed in between.

This intermediate layer is called a bridge or interface, the interface sits between our application and the webserver and defines how the Python application interacts with the webserver.

One of the most popular interfaces is CGI - Common Gateway Interface - the upside of CGI is that it supports all the programming languages.

CGI is not a program rather a specification in which defines how the application interacts with the webserver.

The webserver has to be configured properly for the CGI scripts; All the webservers like Nginx, Apache, IIS, etc... have configurations for the CGI, this means that we need to tell the webserver about our CGI interface.

CGI starts a new process whenever it receives a request and ends that process at the end of the request, this means that on each single HTTP request a new process will be started which makes CGI too slow.

FastCGI was created to solve the CGI slowness issues.

FastCGI allows the process to serve multiple requests - instead of a single one in CGI case -.

Gunicorn is a Python WSGI HTTP Server for UNIX, it's an intermdiate layer between our Python application and our web server.

## Installing and configuring Gunicorn
Go ahead and install it via pip:

```bash
pip3 install gunicorn
```

If you are using `virtualenv`, then consider installing it as follows:

```bash
source YOUR_PROJECT_PATH/bin/activate
pip3 install gunicorn
```

Run the Gunicorn web server as follows:

```bash
gunicorn main:app -b 127.0.0.1:8000 --name="MyApp" --workers=3 --reload --user=USER_RUNNING_THIS_PROCESS
```

After executing this command Gunicorn will be running on port 8000, but we need a more efficient way to control this process, like restarting if it dies, and running it in the background, this is the supervisor duty.

## Supervisor
Supervisor is one of the most efficient process managers, it's fast, easy and powerful, it can be installed on Linux, Mac, and Windows.

We need supervisor to take care of our Gunicorn process as I mentioned earlier, so go ahead and install it:

```bash
sudo apt install supervisor
```

After installing it, we need to configure our gunicorn process.

So, in `/etc/supervisor/conf.d` create a new file named myapp.conf where myapp is your application name, and put the following content inside it:

```ini
[program:{myapp}]
directory=/var/www/{myapp}
command=/home/{mtapp}/.local/bin/gunicorn main:app -b 127.0.0.1:8000 --name="{MyApp}" --reload --workers=3 --user={myappuser}
user=myappuser
autostart=true
autorestart=true
stderr_logfile=/var/log/myapp.err.log
stdout_logfile=/var/log/myapp.out.log
```

> Please note that you need to modify all the curly braces placeholder to corresponding ones of your application.

This is a very simple configuration file that supervisor needs to run our gunicorn app.

Supervisor doesn't know about this configurtion yet, we have to tell it by two commands:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

Now our gunicorn process is up and running.

![Gunicorn](/static/img/python/deploying-flask-application/002.png)

## How many workers?
One of the most frequent questions when it comes to gunicorn configuration is how many workers do we need for our server?

In our supervisor configuration file, I set a number of 3, but is that correct?

This question has been answered in [gunicorn docs](http://docs.gunicorn.org/en/stable/settings.html#workers), but it's still ambiguous for many people.

So, I found a [brilliant solution](http://dhilipsiva.com/2015/10/22/appropriate-number-of-gunicorn-workers.html) which shows us how many workers do we need on our server.

This solution gets the number of CPU cores, and make the 2n+1 formula.

If you don't want to rack your brain, then just replace the --workers=3 in  supervisor config file and replace it with the following line:

```bash
--workers=$(( 2 * `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 ))
```

After changing the configuration, remember to reread and update supervisor as follows:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

## NGINX
NGINX is one of the most popular web servers and reverse proxy, it's easy and powerful.

But why do we need a reverse proxy?

Gunicorn is a WSGI compliant, in other words, it's meant to be as a web gateway for Python applications, in spite of its name.

By using a reverse proxy such as NGINX, we are going to have a more powerful web server, for example, we might need to use load balancing by adding more servers.

> [Gunicorn docs recommends to use a reverse proxy.](http://docs.gunicorn.org/en/stable/deploy.html)

So, go ahead and install NGINX as follows:

```bash
sudo apt install nginx -y
```

cd to `/etc/nginx/conf.d` and create a new file named myapp.conf where myapp.conf is your application name, and put the following content inside it:

```nginx
server {
    server_name myapp.example.com
    listen 80;
    
    location / {
        proxy_pass "http://127.0.0.1:8000";
        proxy_set_header HOST $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

This is the minimal setup for our application, if you want to add more features like gzip, caching static files, SSL, http2 then you might need to visit this [gist](https://gist.github.com/denji/8359866).
