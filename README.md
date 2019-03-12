# Kubernetes config dump tool

This will dump kubernetes objects through the API based on the config file.
Currently it can authenticate to k8s using a service account's token. That
means you'll have to create a service account, grant it permissions to list
and get the specified resources using a clusterrole and clusterrolebinding.
Examples can be found in examples/ directory.

## Setup

### Python initialization

```bash
$ virtualenv -p /usr/bin/python3 venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Kubernetes initialization

Now, create the service account and grant it the rights:

```bash
$ kubectl create -f examples/serviceaccount.yml
$ kubectl create -f examples/clusterrole.yml
$ kubectl create -f examples/clusterrolebinding.yml
```

Then get the token of the secret:

```bash
$ kubectl get secret $(kubectl get serviceaccount cluster-object-dump --template='{{ with index .secrets 0 }}{{ .name }}{{ end }}') --template='{{ .data.token }}' | base64 -d
```

### Configuration

You can use the config.yml.sample as a starting point. Copy that to config.yml. Fill in the `server` and `token` fields. You should make the master's ca certificate available to the
script, specify its location with the `ca` setting. This is usually located on the master at `/etc/kubernetes/pki/ca.crt`.

Now running the script would produce output under `dest` directory, or if left empty, then in the current working directory.

