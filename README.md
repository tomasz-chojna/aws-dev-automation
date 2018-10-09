#AWS Dev CLI

The tool assumes that is being used on EC2 instance with a role that has a full access to EC2 and Route53, otherwise `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`env variables need to be configured.

SSH configuration (`~.ssh/config`) is assumed to be present at the host running CLI.

```bash
Host *.dev.app.com
User ubuntu
IdentityFile ~/.ssh/dev-key
StrictHostKeyChecking no
```



## Required environment variables

| Variable Name        | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| AWS_DEFAULT_REGION   | e.g. "eu-central-1"                                          |
| EC2_INSTANCE_TYPE    | e.g. "t3.small"                                              |
| EC2_AMI_ID           | Create you own AMI to make provisioning faster or re-use on of existing AWS images |
| EC2_SECURITY_GROUPS  | comma separated names of security groups, e.g. "ssh-access,http-access" |
| EC2_IAM_PROFILE_NAME | Name of the profile, which will be attached to EC2 intance during creation, automatically provides access to AWS services through a role, so there is no need to provide any access keys |
| EC2_INSTANCE_USER    | User with root permission, e.g. "ubuntu"                     |
| EC2_KEYPAIR_NAME     | Keypair name for SSH access                                  |
| EC2_NAME_TAG_PREFIX  | e.g. "dev-server-", when provisiong "test1" server, automatically "dev-server-test1" name will be attached |
| DOMAIN               | Domain registered in Route53, the tool will add a subdomain per server to it, e.g. "dev.app.com" and we can have "test.dev.app.com" subdomain automatically configured |
| DOMAIN_EMAIL         | Certbot requires email address to be provided when issuing a certicate |
| SLACK_WEBHOOK_URL    | When provisioning finishes, a notification is sent that new environment is ready for use |

## Usage

###Show available servers

```bash
$ fab dev.list
st0.dev.app.com (i-002a1073d4b6e938d) - running
st1.dev.app.com (i-0fc1d130d28a100a9) - running
```


### Provision a new server

```bash
$ fab dev.provision:name=st2
You are provisioning dev server instance st2.dev.app.com.
If there is an instance already created for that name, DNS record will be replaced, but the old instance will continue running.
If that's the case, make sure to terminate old instance.
Do you want to continue? [Y/n] Y
Creating EC2 instance (be patient, that takes some time)
[ubuntu@st2.dev.app.com] Executing task 'update_subdomain_ip'
Creating DNS record st2.dev.app.com for IP: 18.196.41.50 (waiting for propagation)
Installing SSL certificate
[ubuntu@st2.dev.app.com] Executing task 'install_ssl'
[ubuntu@st2.dev.app.com] sudo: apt-get install -y nginx python-certbot-nginx
[ubuntu@st2.dev.app.com] out: nginx is already the newest version (1.15.4-1~xenial).
[ubuntu@st2.dev.app.com] out: python-certbot-nginx is already the newest version (0.25.0-2+ubuntu16.04.1+certbot+1).
[ubuntu@st2.dev.app.com] out: 0 upgraded, 0 newly installed, 0 to remove and 254 not upgraded.
[ubuntu@st2.dev.app.com] out:

[ubuntu@st2.dev.app.com] run: sudo certbot certonly --nginx -d st2.dev.app.com --renew-by-default --email admin@app.com --agree-tos -n
[ubuntu@st2.dev.app.com] out: Saving debug log to /var/log/letsencrypt/letsencrypt.log
[ubuntu@st2.dev.app.com] out: Plugins selected: Authenticator nginx, Installer nginx
[ubuntu@st2.dev.app.com] out: Starting new HTTPS connection (1): acme-v02.api.letsencrypt.org
[ubuntu@st2.dev.app.com] out: Obtaining a new certificate
[ubuntu@st2.dev.app.com] out: Performing the following challenges:
[ubuntu@st2.dev.app.com] out: http-01 challenge for st2.dev.app.com
[ubuntu@st2.dev.app.com] out: Using default address 80 for authentication.
[ubuntu@st2.dev.app.com] out: Waiting for verification...
[ubuntu@st2.dev.app.com] out: Cleaning up challenges
[ubuntu@st2.dev.app.com] out:
[ubuntu@st2.dev.app.com] out: IMPORTANT NOTES:
[ubuntu@st2.dev.app.com] out:  - Congratulations! Your certificate and chain have been saved at:
[ubuntu@st2.dev.app.com] out:    /etc/letsencrypt/live/st2.dev.app.com/fullchain.pem
[ubuntu@st2.dev.app.com] out:    Your key file has been saved at:
[ubuntu@st2.dev.app.com] out:    /etc/letsencrypt/live/st2.dev.app.com/privkey.pem
[ubuntu@st2.dev.app.com] out:    Your cert will expire on 2019-01-07. To obtain a new or tweaked
[ubuntu@st2.dev.app.com] out:    version of this certificate in the future, simply run certbot
[ubuntu@st2.dev.app.com] out:    again. To non-interactively renew *all* of your certificates, run
[ubuntu@st2.dev.app.com] out:    "certbot renew"
[ubuntu@st2.dev.app.com] out:  - Your account credentials have been saved in your Certbot
[ubuntu@st2.dev.app.com] out:    configuration directory at /etc/letsencrypt. You should make a
[ubuntu@st2.dev.app.com] out:    secure backup of this folder now. This configuration directory will
[ubuntu@st2.dev.app.com] out:    also contain certificates and private keys obtained by Certbot so
[ubuntu@st2.dev.app.com] out:    making regular backups of this folder is ideal.
[ubuntu@st2.dev.app.com] out:  - If you like Certbot, please consider supporting our work by:
[ubuntu@st2.dev.app.com] out:
[ubuntu@st2.dev.app.com] out:    Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
[ubuntu@st2.dev.app.com] out:    Donating to EFF:                    https://eff.org/donate-le
[ubuntu@st2.dev.app.com] out:
[ubuntu@st2.dev.app.com] out:

Updating hostname
[ubuntu@st2.dev.app.com] Executing task 'update_hostname'
[ubuntu@st2.dev.app.com] run: sudo bash -c "echo st2.dev.app.com > /etc/hostname"
[ubuntu@st2.dev.app.com] run: sudo hostname st2.dev.app.com
Provisioning has been completed. You can start deploying your code!
```

### EC2 instance lifecycle commands

As EC2 instances by default release the IP address after they are stopped (if it's not a static Elastic IP Address),
that would make our instance unavailable after restart. In order to prevent that situation, when starting the instance
Route53 DNS record is updated with a new IP.

```bash
$ fab dev.start:name=st2
```


```bash
$ fab dev.stop:name=st2
```

```bash
$ fab dev.terminate:name=st2
```
