#! /bin/bash
MONTH=$(date +%m)
REDIS_HOST="127.0.0.1"
REDIS_DB=8
REDIS_PORT=6379

args=$(getopt -o l:p:g: -l login:,password:,package:,redis-port:,redis-host:,redis-db: -- "$@" )
eval set -- "$args"
for i; do
	case $i in
		-l|--login) LOGIN=$2; shift 2 ;;
		-p|--password) PASSWORD=$2; shift 2 ;;
		-g|--package)  PKG=$2; shift 2 ;; 
		--redis-port)  REDIS_PORT=$2; shift 2 ;;
		--redis-host)  REDIS_HOST=$2; shift 2 ;;
		--redis-db) REDIS_DB=$2; shift 2 ;;
	esac
done

die() {
	echo $1 >/dev/stderr
	exit 2
}

usage() {
	echo "Usage: $0 -g|--package PACKAGE -l|--login LOGIN -p|--password PASSWORD [--redis-port PORT] [--redis-host HOST] [--redis-db DB_NUMBER]"
	exit 1
}

depends_on() {
    which $1 &>/dev/null || die "$1 is missing!"
}

verify_zip() {
    [ -f "$1" ] || die "Can't find zip file $1" 
    unzip -l "$1" >/dev/null || die "zip file $1 is corrupted."
}

[ -n "$LOGIN" ] || usage
[ -n "$PASSWORD" ] || usage
[ -n "$USER" ] || usage
[ -n "$PKG" ] || usage

[ -z "$TEMP" ] && TEMP=/tmp
TMPDIR=$TEMP/ip2location/$MONTH

depends_on unzip
depends_on perl
# redis and python are kind of obvious, so no point in checking.

mkdir -p $TMPDIR
rm "$TMPDIR/*"
cd $(dirname $0)
./download.pl -package $PKG -login $LOGIN -password $PASSWORD -output "$TMPDIR/$PKG-$MONTH.zip" || \
	die "Failed to download, quitting"
verify_zip "$TMPDIR/$PKG-$MONTH.zip"
unzip -u -o -d $TMPDIR "$TMPDIR/$PKG-$MONTH.zip" 'IP*.CSV' || die "Failed to download, quitting"

PKG_FILE="$TMPDIR/IP*.CSV"
cd ../../src/
./geodis.py -i -f $PKG_FILE -n "$REDIS_DB" -H "$REDIS_HOST" -p "$REDIS_PORT" || die "Update failed, your database is empty"
