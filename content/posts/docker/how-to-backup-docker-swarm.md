It is no secret that backing up Swarm is mandatory, In this article, I’ll show you how to take a full Swarm backup and how to restore this backup if something bad happens, but before I dig into that, let me mention some tips:

- I assume you are running Ubuntu or any equivalent Linux distro.
- Swarm configurations are saved in /var/lib/docker/swarm directory.
- You can use any manager to take the backup, for example, if you have three managers you can use any one of them to make a full backup of Swarm.
- Be away from the leader-manager as much as you can, and use another manager.
- A scheduled backup is highly recommended.

The very 1st step to do is to stop Docker:

```bash
sudo service docker stop
```

Create the backup by compressing the /var/lib/docker/swarm in a tarball:

```bash
tar -czvf swarm.backup.tar /var/lib/docker/swarm/
```

Our backup is ready now 🙂

If something bad happens and you (really) want to restore the backup, then you can simply unzip the tarball as follows:

```bash
service docker stop

rm -Rf /var/lib/docker/swarm

tar -zxvf swarm.backup.tar -C /var/lib/docker
```

Well, that wasn’t enough! We have to initiate Swarm again! What? Really? Yes.. but with a magic flag:

```bash
docker swarm init --force-new-cluster
```
