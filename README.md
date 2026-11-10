# Avunu server auth addons

OAuth sign-in that links a first-time Google (or other) login to the Odoo user who
already has that email, instead of failing with "You do not have access to this database
or your invitation has expired." It is a set of Odoo 18.0 modules built and maintained
by [Avunu LLC](https://avunu.net) for our own client work and published for anyone to
use. The repository extends [OCA/server-auth](https://github.com/OCA/server-auth) and
Odoo's `auth_oauth`.

## Modules

| Module | What it does | Licence |
| --- | --- | --- |
| [`auth_oauth_link_by_email`](auth_oauth_link_by_email/README.md) | On a first OAuth sign-in, links the active user whose login is the provider's verified email, for each provider that has the option on | AGPL-3.0-or-later |
| [`auth_oauth_link_by_email_multi_token`](auth_oauth_link_by_email_multi_token/README.md) | Installs itself with OCA `auth_oauth_multi_token` so the link happens before that module's user lookup | AGPL-3.0-or-later |

Each module's README explains why it exists and how it works.

## Branches

`18.0` is the default branch and the one pull requests go to. Its code targets Odoo
18.0, the series named in `.odoo-series`, and it is the branch to install or pin. When a
newer Odoo series is maintained, it gets its own branch (`19.0`, …).

## Install

Requires Odoo 18.0 and a PostgreSQL database. Installing a module pulls in the modules
it depends on (see below), and those must be on your `addons_path` first.

With a plain Odoo checkout, clone this repository on its `18.0` branch and add it to the
addons path:

```sh
git clone --branch 18.0 https://github.com/Avunu/server-auth-addons.git
odoo-bin --addons-path=odoo/addons,/path/to/server-auth-addons,<your other addons paths> \
  -d <database> -i auth_oauth_link_by_email --stop-after-init
```

With [odoo-nix](https://github.com/Avunu/odoo-nix), add the repository from the dev
shell. `odoo module add` accepts an `owner/repo` and a branch, adds it as a submodule,
and the addons path is regenerated from the folders present (run `direnv reload`
afterwards):

```sh
odoo module add Avunu/server-auth-addons 18.0
```

Then turn on **Link Existing Users by Email** on each OAuth provider that should use it.

## Dependencies

Each module's `__manifest__.py` is the source of truth.

| Module | Needs from Odoo, OCA or others | Python packages |
| --- | --- | --- |
| `auth_oauth_link_by_email` | `auth_oauth` (Odoo) | none |
| `auth_oauth_link_by_email_multi_token` | `auth_oauth_link_by_email` and `auth_oauth_multi_token` ([OCA/server-auth](https://github.com/OCA/server-auth)) | none |

## Development

The repository carries its own development environment, built by
[odoo-nix](https://github.com/Avunu/odoo-nix) in addons mode. OCB and the repositories
these modules depend on are flake inputs pinned in `flake.lock`, and the Python
environment is locked in `nix/`. You need Nix with flakes, and optionally direnv.

```sh
git clone https://github.com/Avunu/server-auth-addons.git && cd server-auth-addons
direnv allow                  # or: nix develop --no-pure-eval
devenv up                     # PostgreSQL, Odoo and Mailpit
odoo db provision             # a database with every module here installed
odoo test auth_oauth_link_by_email
```

After `nix flake update`, or when a module gains a `depends` or a Python requirement,
run `odoo project relock` and commit `flake.lock` and `nix/`. A new dependency on
another repository also needs its input and an `externalSources` entry in `flake.nix`.
See odoo-nix's
[A repository of addons](https://github.com/Avunu/odoo-nix/blob/main/docs/scaffolding/addons-repository.md).

## Tests

Odoo runs a module's tests when you install or update it with `--test-enable`. Select a
module's tests with a `--test-tags` filter and use a throwaway database:

```sh
odoo-bin -c odoo.conf -d <testdb> -i auth_oauth_link_by_email \
  --test-enable --test-tags /auth_oauth_link_by_email --stop-after-init
```

Both modules have automated tests; each README runs them with this same command.

## Licence

Every module is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE),
as its `__manifest__.py` also states (`AGPL-3`, Odoo's identifier for version 3).
