# API client todos

## DOCS

### need to doc proxy and cert

### All docstrings re-done

## Tests package

### Make client config automatically determine adapter config

Solve for changing schemas.

### Test subclassing/strings/etc of all exceptions

In tests_pkg/test_exceptions.py

### add atexit to verify no badwolf leftovers

Actions leftover, need to determine how to clean up

### Permissions check not the same octal on windows

In tests_pkg/test_tools.py:test_simple_pathlib

### SQ keys unknown value unknown

in tests_api/test_api_users_devices.py:TestSavedQuery.test__get

"historical" and "filteredAdapters" in expressions

## CLI package

### Add flatten option for export

- external method, called by to_json & to_csv
- have to figure out how to handle multiple fields to flatten
- need to verify field actually supplied??

Concept:

```text

This:
|| h || swname || swver ||
|| xxx|| abc, def, ghi || 1,2,3 ||

becomes:

|| h || swname || swver ||
|| xxx|| abc || 1 ||
|| xxx|| def || 2 ||
|| xxx|| ghi || 3 ||

axonshell devices get \
    -q (specific_data.data.last_seen >= date("NOW - 30d")) \
    -f installed_software.name \
    --field-flatten installed_software
```

### Add ability to use normalized field names instead of internal field names

### Add export format: SQL dump

### Add export format: word

Would need to add optional package requirements.

### Add export format: pdf

Would need to add optional package requirements.

### Accept ini based config

In adapters cnx add. Unsure of this.

### Determine better way handle skips in prompts

In adapters cnx add. Maybe custom click type?

### Add --verbose/--no-verbose to silence echo_ok

### Add cert_human logic

### Add links to docs site in --help

## HTTP package

## API package

## enforcements.py: Needs work, awaiting REST API updates

Will need something like a public build_trigger method
public create will need to get sq!

### users_devices.py:UserDeviceMixin.get_by_saved_query: Need filters

Just like GUI. GUI processes it client side, so we have to do the same.

Concept:

```text
    --field-filter "eq:installed_software.name=Google Chrome||Google Chrome Installer"
    --field-filter "re:installed_software.name=.*google.*"
    --field-filter "in:installed_software.name=google"
    --field-filter "not:eq:installed_software.version=77"
    --field-filter "lte:2:installed_software.name"
    --field-filter "gt:2"
    --field-filter "gte:2"
```

### users_devices.py:UserDeviceMixin.get: Add logging for page rows fetched

This may no longer be necessary? Re-check.

### users_devices.py:Reports: new reports

#### Majority rule concept

- for a general field, say hostname
- get the values of hostname from ALL adapters in system
- find the value that is the MOST common value and add that as a value for a
  key majority_hostname

#### Field excludes

- both --field-exclude and --field-regex-exclude

#### Weighting concept

- for a general field, say hostname
- get the values of hostname from ALL adapters in system
- allow weighting on a 1-10 score
- if adapter x with a score of 10 has hostname1, add that as a value for a key
  weighted_hostname
- if adapter x with a score of 10 has NO hostname, fallback to adapter y with a score
  of 7

Concept:

```text
--field-weight hostname:aws=10,sccm=10,solwarinds=10,jamf=9,ad=9,bluecat=1
# (score aws as the heaviest)
weighted.hostname
```

#### User to Device correlation

- for each user
  - for each device
    find any users whose username matches last logged in user
    device[users] = found_users

#### Missing patches

Concept:

```text
axonshell devices get | axonshell devices get-missing-patches --patch KB293028424
```

#### Count of assets with matching installed_software.name values

Identify source of request, need more details.

#### Missing software

Similar to missing patches.

### users_devices.py:Reports.missing_adapters: show per node missing columns

Right now shows all nodes grouped

## REST API

### Schema's are defining required items that dont exist in items

In tests_api/test_api_adapters.py

### Some connection configs have empty client ID's

In tests_api/test_api_adapters.py

### adding cnx with parsed config instead of raw config breaks stuff

check if this is fixed.

### Add adapter description to adapter metadata

Currently only stored in:

```text
cortex/plugins/gui/frontend/src/constants/plugin_meta.js
```

### Add support for user add/delete/modify

### Add support for lifecycle endpoint

### Add support for discover phase

### add support for setting advanced settings

General adapter advanced settings:

```text
method=POST
path=/api/plugins/configs/carbonblack_defense_adapter/AdapterBase
body={
    "connect_client_timeout": 300,
    "fetching_timeout": 5400,
    "last_fetched_threshold_hours": 49,
    "last_seen_prioritized": false,
    "last_seen_threshold_hours": 43800,
    "minimum_time_until_next_fetch": null,
    "realtime_adapter": false,
    "user_last_fetched_threshold_hours": null,
    "user_last_seen_threshold_hours": null
}
```

Adapter specific advanced settings:

```text
method=POST
path=/api/plugins/configs/carbonblack_defense_adapter/CarbonblackDefenseAdapter
body={"fetch_deregistred":false}
```

### Modify date_fetched for adapter connection

Make it be last time any fetch happened

Currently it seems to be only for when fetch has been triggered
from "save" in adapters>connection page, and does not include when
last fetch happened from discover.

Pcode for determining last fetch:

```text
date_fetched = client["date_fetched"]
minutes_ago = tools.dt.minutes_ago(date_fetched)

if within is not None:
    if minutes_ago >= within:
        continue

if not_within is not None:
    if minutes_ago <= not_within:
        continue
```

### Process saved query expressions on add if none supplied

Currently, if you add a SQ via API without expressions, the query wizard will
be empty for that SQ due to no expressions. This would possibly mean moving
query wizard parsing from front end JS to API?

### Enforcements API needs love

### Add lifecycle from private API to public API

Allow for conditional "stuffs"
