#!/bin/bash
# Keep credentials out of process arguments and healthcheck output.
set -eu
umask 077
options=$(mktemp)
trap 'rm -f "$options"' EXIT
escape_option() {
  escaped=${1//\\/\\\\}
  escaped=${escaped//\"/\\\"}
  escaped=${escaped//$'\n'/\\n}
  escaped=${escaped//$'\r'/\\r}
}
escape_option "$MYSQL_USER"
user=$escaped
escape_option "$MYSQL_PASSWORD"
password=$escaped
printf '[client]\nuser="%s"\npassword="%s"\nhost=127.0.0.1\nprotocol=tcp\n' "$user" "$password" > "$options"
mysql --defaults-extra-file="$options" --connect-timeout=3 --batch --skip-column-names --execute='SELECT 1' >/dev/null 2>&1
