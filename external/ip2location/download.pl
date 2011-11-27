#!/usr/bin/perl -w
###############################################################################
# IP2Location Download Client
###############################################################################
# Perl script to download IP2Location(tm) batabase from the server.
# Note: User subscription login and password required.
#
# There is no warranty or guarantee conveyed by the author/copyright holder of
# this script. By obtaining, installing, and using this program, you agree and
# understand that the author and copyright holder are not responsible for any
# damages caused under any conditions due to the malfunction of the script(s)
# on your server or otherwise.
#
# REVISION HISTORY
# ================
# 1.0.0   Initial Release
# 1.1.0   Support IP2Location DB11 + DB12 + DB13 + DB14
# 1.2.0   Change URL to IP2Location.com
# 2.0.0   Support IP2Location DB15 + DB16 + DB17 + DB18
#         Support IP2Proxy PX1
#         Support Command Prompt in Windows as EXE
# 2.1.0   Support Proxy Server
# 2.2.0   Support CIDR + ACL
# 3.0.0   Support IP2Location DB19 + DB20
#
# Copyright (C) 2005-2010 IP2Location.com. All rights reserved.
#
###############################################################################
use Getopt::Long;
use strict;
$|++;
#eval("use LWP 5.6.9;"); die "[ERROR] LWP 5.6.9 or greater required.\n" if $@;
eval("use LWP;"); die "[ERROR] LWP library required.\n" if $@;

my $VERSION = "3.0.0";
my $opt_package = "";
my $opt_login = "";
my $opt_password = "";
my $opt_output = "";
my $opt_proxy = "";
my $help = 0;

my $result = GetOptions('package=s' => \$opt_package,
	'login:s' => \$opt_login,
	'password:s' => \$opt_password,
	'output:s' => \$opt_output,
	'proxy:s' => \$opt_proxy,
	'help' => \$help);

if ($help) {
	&print_help;
	exit(0);
}

my $final_data = "";
my $total_size = 0;
my $expiry_date = "";
my $database_version = "";

my $urlversion = "http://www.ip2location.com/download/downloaderversion.txt";
my $urlinfo = "http://www.ip2location.com/downloadinfo.aspx";
my $url = "http://www.ip2location.com/download.aspx";

my $login = '';
my $password = '';
my $filename = '';
my $output = '';
my $package = '';
my $proxy = '';

if ($opt_package ne "") {
	$package = $opt_package;
} else {
	&print_help;
	print "[Error] Missing -package command line switch or parameter.\n";
	exit(0);
}

if ($opt_login ne "") {
	$login = $opt_login;
} else {
	&print_help;
	print "[Error] Missing -login command line switch or parameter.\n";
	exit(0);
}

if ($opt_password ne "") {
	$password = $opt_password;
} else {
	&print_help;
	print "[Error] Missing -password command line switch or parameter.\n";
	exit(0);
}

if ($opt_proxy ne "") {
	$proxy = lc($opt_proxy);
} 


$package = uc($package);

if ($package eq "DB1") { $filename = "IPCountry-FULL.zip"; $output = "IP-COUNTRY-FULL.ZIP"; }
elsif ($package eq "DB2") { $filename = "IPISP-FULL.zip"; $output = "IP-COUNTRY-ISP-FULL.ZIP"; }
elsif ($package eq "DB3") { $filename = "IP-COUNTRY-REGION-CITY-FULL.ZIP";  $output = $filename; }
elsif ($package eq "DB4") { $filename = "IP-COUNTRY-REGION-CITY-ISP-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB5") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB6") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ISP-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB7") { $filename = "IP-COUNTRY-REGION-CITY-ISP-DOMAIN-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB8") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ISP-DOMAIN-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB9") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB10") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-ISP-DOMAIN-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB11") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB12") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB13") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-TIMEZONE-NETSPEED-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB14") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB15") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-AREACODE-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB16") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-AREACODE-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB17") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-TIMEZONE-NETSPEED-WEATHER-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB18") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-AREACODE-WEATHER-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB19") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ISP-DOMAIN-MOBILE-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB20") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-AREACODE-WEATHER-MOBILE-FULL.ZIP"; $output = $filename; }
elsif ($package eq "DB1BIN") { $filename = "IP-COUNTRY.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB2BIN") { $filename = "IP-COUNTRY-ISP.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB3BIN") { $filename = "IP-COUNTRY-REGION-CITY.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB4BIN") { $filename = "IP-COUNTRY-REGION-CITY-ISP.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB5BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB6BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ISP.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB7BIN") { $filename = "IP-COUNTRY-REGION-CITY-ISP-DOMAIN.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB8BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ISP-DOMAIN.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB9BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB10BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-ISP-DOMAIN.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB11BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB12BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB13BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-TIMEZONE-NETSPEED.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB14BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB15BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-AREACODE.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB16BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-AREACODE.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB17BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-TIMEZONE-NETSPEED-WEATHER.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB18BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-AREACODE-WEATHER.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB19BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ISP-DOMAIN-MOBILE.BIN.ZIP"; $output = $filename; }
elsif ($package eq "DB20BIN") { $filename = "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-AREACODE-WEATHER-MOBILE.BIN.ZIP"; $output = $filename; }
elsif ($package eq "PX1") { $filename = "IP2PROXY-IP-COUNTRY.ZIP"; $output = $filename; }
elsif ($package eq "DB1CIDR") { $filename = "IP2LOCATION-IP-COUNTRY-CIDR.ZIP"; $output = $filename; }
elsif ($package eq "DB1ACL") { $filename = "IP2LOCATION-IP-COUNTRY-ACL.ZIP"; $output = $filename; }
else {
	print "[Error] Unknown -package command line parameter.";
	exit(0);
}

if ($opt_output ne "") {
	$output = $opt_output;
}

&check_info();  
&download();    
&check_update();

sub check_info() {
	my $ua;
	my $response;
	my $message;
	my @data;
	my $localpackage = $package;
	
	if ($package eq "DB1CIDR") {
		$localpackage = "DB1";
	} elsif ($package eq "DB1ACL") {
		$localpackage = "DB1";
	}
	
	$ua = LWP::UserAgent->new( );
	if ($proxy ne "") {
		$ua->proxy('http', $proxy);
	}
	
	$response = $ua->get($urlinfo . "?email=$login&password=$password&productcode=$localpackage");
	$message = $response->content();
	@data = split(/\;/, $message);
	if ($data[0] eq "OK")
	{
		$total_size = $data[3];
		$expiry_date = $data[1];
		$database_version = $data[2];
	} elsif ($data[0] eq "EXPIRED") {
		print "[Error] This download account has been expired since $data[1]. Please visit http://www.ip2location.com to renew the subscription.";
		exit(0);
	} elsif ($data[0] eq "INVALID") {
		print "[Error] Invalid account name or password.";
		exit(0);
	} elsif ($data[0] eq "NOPERMISSION") {
		print "[Error] This download account could not download required database because of permission issue.";
		exit(0);
	} else {
		print "[Error] Unknown issue $message. Please contact support\@ip2location.com.";
		exit(0);
	}
}

sub download() {
	print_header();
	print "Downloading ", $output, " ...\n";
	
	my $ua;
	my $response;
	
	$ua = LWP::UserAgent->new( );
	if ($proxy ne "") {
		$ua->proxy('http', $proxy);
	}
	push @{ $ua->requests_redirectable }, 'POST';
	
	my %form;
	
	$form{'login'} = $login;
	$form{'password'} = $password;
	$form{'btnDownload'} = "btnDownload";
	
	$response = $ua->post($url . "?productcode=$package", \%form, ':content_cb' => \&callback );
	
	die "$url error: ", $response->status_line unless $response->is_success;
	
	open OUT1, ">$output" or die;
	binmode(OUT1);
	print OUT1 $final_data;
	close OUT1;
}

sub check_update() {
	my $ua;
	my $response;
	my $message;
	$ua = LWP::UserAgent->new();
	if ($proxy ne "") {
		$ua->proxy('http', $proxy);
	}
	$response = $ua->get($urlversion);
	$message = $response->content();
	$message =~ s/\.//g;
	my $thisversion = $VERSION;
	$thisversion =~ s/\.//g;
	
	if ($message > $thisversion) {
		print "[IMPORTANT] New script version detected. Please download the latest version from http://www.ip2location.com/download/download.pl.zip";
	}
}

sub callback {
   my ($data, $response, $protocol) = @_;
   $final_data .= $data;
   print progress_bar( length($final_data), $total_size, 25, '=' );
}

sub progress_bar {
    my ( $got, $total, $width, $char ) = @_;
    $width ||= 25; $char ||= '=';
    my $num_width = length($total);
    sprintf "|%-${width}s| Got %${num_width}s bytes of %s (%.2f%%)\r", 
        $char x (($width-1)*$got/$total). '>', 
        $got, $total, 100*$got/+$total;
}

sub  print_help {
	print_header();
	print <<HELP
 This program download the latest IP2Location database from server.

Command Line Syntax:
$0 -package <package> -login <login> -password <password> -output <output> -proxy <proxy_server>
 
  package  - Database Package (DB1, DB2...DB20, PX1 or DB1BIN, DB2BIN...DB20BIN)
  login    - Login
  password - Password
  proxy    - Proxy Server with Port (Optional)
  output   - Output Filename (Optional)

Please contact support\@ip2location.com for technical support.

HELP
}

sub  print_header {
	print <<HEADER
------------------------------------------------------------------------
 IP2Location Download Client (Version $VERSION)
 URL: http://www.ip2location.com
------------------------------------------------------------------------
HEADER
}
