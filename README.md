
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
<!-- [![Pre-commit Status](https://github.com/OpenEMS/odoo-openems/actions/workflows/pre-commit.yml/badge.svg?branch=14.0)](https://github.com/OpenEMS/odoo-openems/actions/workflows/pre-commit.yml?query=branch%3A14.0) -->
<!-- [![Build Status](https://github.com/OpenEMS/odoo-openems/actions/workflows/test.yml/badge.svg?branch=14.0)](https://github.com/OpenEMS/odoo-openems/actions/workflows/test.yml?query=branch%3A14.0) -->
<!-- [![codecov](https://codecov.io/gh/OpenEMS/odoo-openems/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OpenEMS/odoo-openems) -->
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Odoo for OpenEMS Backend

This repository provides a Odoo addon to use Odoo as Metadata provider for OpenEMS Backend

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OpenEMS Association e.V.
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->

## How to create a docker container for testing

### 1. Create Folder

```shell
mkdir openems-odoo/
cd openems-odoo/
```

### 2. Get odoo addons

```shell
mkdir addons

git clone https://github.com/OCA/partner-contact.git -b 18.0 ./addons/oca-partner-contact
git clone https://github.com/OCA/web.git -b 18.0 ./addons/oca-web
git clone https://github.com/OpenEMS/odoo-openems.git -b 18.0 ./addons/odoo-openems

chmod -R +rx addons/
```

### 3. Create `docker-compose.yaml`

```YAML
services:
  web:
    image: odoo:18.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./addons/odoo-openems/openems:/mnt/extra-addons/openems
      - ./addons/oca-web/web_m2x_options:/mnt/extra-addons/web_m2x_options
      - ./addons/oca-partner-contact/partner_firstname:/mnt/extra-addons/partner_firstname

  db:
    image: postgres:18
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
```

> **NOTE**: for more information about base image see: https://hub.docker.com/_/odoo/

### 4. Start Container

```shell
docker compose up -d
```

## Keycloak

To integrate Keycloak as a OAuth provider in Odoo, you need to install the following OCA module:
<br/>
[auth_oidc](https://github.com/OCA/server-auth/tree/18.0/auth_oidc)


## Multi Session Odoo

If you wish to enable multiple connections for the same account with an OAuth provider in Odoo, you'll need to install this OCA module:
<br/>
[auth_oauth_multi_token](https://github.com/OCA/server-auth/tree/18.0/auth_oauth_multi_token)
