# CKAN to DSpace Migration Tool

## Prerequisites

* Python >= 3.5
* python-requests

Run `pip -r requirements.txt` to install the required dependencies


## Configuration

The configuration tool requires the following parameters to be set in `config.ini`:

```
[ckan]
RootUrl: Root url of CKAN installation
RestUrl: CKAN rest url path

[dspace]
RootUrl: Root url of DSpace installation
RestUrl: DSpace rest url path
CommunityId: Id of DSpace community to import the data into (optional)
UserEmail: DSpace user's email
UserPassword: DSpace user's password
```

If no `CommunityId` is specified the tool queries the list of existing communities and imports the data into the first community in the list.

## Running

Run `python migrate.py --help` for instructions.

### Available Commands

**list-ckan**

Lists the public contents of the configured ckan repository.

**list-dspace**

Lists the public contents of the configured dspace repository.

**migrate-ckan-to-dspace**

Migrate the configured ckan repository to dspace. This command assumes that the dspace repository contains at least one community.
