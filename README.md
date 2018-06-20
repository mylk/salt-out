## What tries to solve

If you use salt for deployment you may have noticed that the output isn't really a helping hand.
Let's say you deploy an application to 50 servers and one of them goes bad.

By default, salt spits a long YAML output per server with every executed command and its result.
So, you will find yourself trying to examine salt's output to find what went wrong and on which
server.

Also, there is no clear indication that everything goes fine, unless you wait till the end
of the deployment where the exit code of the salt command answers your question.

## How it tries to solve this

Passing salt's output through `salt-out` you can clearly see the deployment's result on each
server, as soon as salt returns it.

You will also clearly see the failed deployment command and the error thrown.

Also, if your deployment prints out debugging messages with specific prefixes (`[DEBUG]`, `[WARNING]`),
`salt-out` will let them be shown too.

You can use `salt-out` either in your terminal or in a CI job.

## Installation

Clone this repository:

```
git clone https://github.com/mylk/salt-out.git
```

Enter the project's directory:

```
cd salt-out
```

Install `salt-out`:

```
sudo make install
```

Install the `salt-out` wrapper (see its purpose on the next section):

```
sudo make wrapper_install
```

Of course you can uninstall both anytime:

```
sudo make uninstall
sudo make wrapper_uninstall
```

## How to use it

### The wrapper

You can just use the wrapper script, which encapsulates the execution of the salt command and pipe its
output to `salt-out`. For example:

```
saltoutw [...]
```

In place of `[...]` you have to put the salt options you already use.

The wrapper is really convenient, as `salt-out` needs a couple of salt options to be set (see the next section)
and that gets you out of the trouble setting them yourself.

### The "no wrapper" way

Otherwise, you can put `salt-out` at the end of your salt command and pass through its output to `salt-out`.
You will also have to add a couple of options to the salt command.
For example:

```
salt --verbose --out=json --out-indent=-1 [...] | saltout
```

In place of `[...]` you have to put the salt options you already use.

The `--out=json` option will just turn salt's output to JSON, instead of YAML, making parsing it more easy.
Also `--out-indent=-1` will print each server output to a single line and that helps us to parse JSON
more easily.

## Available options

- `--no-colors`

  Show no colors, suitable for environments that cannot display colors, like CI tools.

- `--raw-dir`

  Save raw input (the output of salt) to the given directory.

## Output example

```
Executing job with jid 20180206153050043647
[  OK  ] server1 (1.1 min)
[  OK  ] server2 (1.1 min)
[ FAIL ] server3 (0.8 min)
Reason:
systemctl reload php7.0-fpm.service && systemctl reload nginx.service
Job for nginx.service failed. See 'systemctl status nginx.service' and 'journalctl -xn' for details.

[  OK  ] server4 (1.1 min)
```

## Run it with fixtures

There are a few fixtures included in the project, inside the directory `test/fixtures`.
Of course you can use them to run `salt-out` against them using the deployment simulator,
which just echos the content of the fixtures with a short sleep between them.

```
./scripts/deploy_simulator.py | src/saltout.py
```
