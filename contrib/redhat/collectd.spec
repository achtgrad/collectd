
%define with_java %(test -z "$JAVA_HOME" ; echo $?)

Summary:	Statistics collection daemon for filling RRD files.
Name:		collectd
Version:	4.10.0sq1
Release:	7%{?dist}
Source:		http://collectd.org/files/%{name}-%{version}.tar.gz
License:	GPL
Group:		System Environment/Daemons
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
BuildPrereq:	lm_sensors-devel, rrdtool-devel, libpcap-devel, net-snmp-devel, libstatgrab-devel, libxml2-devel, libiptcdata-devel, autoconf, automake, flex, bison, libtool
# libcurl deps
BuildPrereq:	curl-devel,libidn-devel,openssl-devel
Requires:	rrdtool, perl-Regexp-Common, libstatgrab
Packager:	Sam Quigley <quigley@squareup.com>
Vendor:		collectd development team <collectd@verplant.org>


%description
collectd is a small daemon which collects system information periodically and
provides mechanisms to monitor and store the values in a variety of ways. It
is written in C for performance. Since the daemon doesn't need to startup
every time it wants to update the values it's very fast and easy on the
system. Also, the statistics are very fine grained since the files are updated
every 10 seconds.


%package apache
Summary:	apache-plugin for collectd.
Group:		System Environment/Daemons
Requires:	collectd = %{version}, curl
%description apache
This plugin collects data provided by Apache's `mod_status'.

%package dns
Summary:       DNS traffic analysis module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}
%description dns
This plugin collects DNS traffic data.

%package email
Summary:	email-plugin for collectd.
Group:		System Environment/Daemons
Requires:	collectd = %{version}, spamassassin
%description email
This plugin collects data provided by spamassassin.

%package ipmi
Summary:       IPMI module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}
%description ipmi
This plugin for collectd provides IPMI support.

%package mysql
Summary:	mysql-module for collectd.
Group:		System Environment/Daemons
Requires:	collectd = %{version}, mysql
%description mysql
MySQL querying plugin. This plugins provides data of issued commands, called
handlers and database traffic.

%package nginx
Summary:	nginx-plugin for collectd.
Group:		System Environment/Daemons
Requires:	collectd = %{version}, curl
%description nginx
This plugin gets data provided by nginx.

%package -n perl-Collectd
Summary:       Perl bindings for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%description -n perl-Collectd
This package contains Perl bindings and plugin for collectd.


%package ping
Summary:       ping module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}
%description ping
This plugin for collectd provides network latency statistics.


%package postgresql
Summary:       PostgreSQL module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}
%description postgresql
PostgreSQL querying plugin. This plugins provides data of issued commands,
called handlers and database traffic.


%package rrdtool
Summary:       RRDTool module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}, rrdtool
%description rrdtool
This plugin for collectd provides rrdtool support.


%package sensors
Summary:	libsensors-module for collectd.
Group:		System Environment/Daemons
Requires:	collectd = %{version}, lm_sensors
%description sensors
This plugin for collectd provides querying of sensors supported by lm_sensors.

%package snmp
Summary:	snmp-module for collectd.
Group:		System Environment/Daemons
Requires:	collectd = %{version}, net-snmp
%description snmp
This plugin for collectd allows querying of network equipment using SNMP.


%package web
Summary:        Contrib web interface to viewing rrd files
Group:          System Environment/Daemons
Requires:       collectd = %{version}
Requires:       collectd-rrdtool = %{version}
Requires:       perl-HTML-Parser, perl-Regexp-Common, rrdtool-perl, httpd
%description web
This package will allow for a simple web interface to view rrd files created by
collectd.

%ifnarch ppc ppc64 sparc sparc64
%package virt
Summary:       Libvirt plugin for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}
%description virt
This plugin collects information from virtualized guests.
%endif


%if %with_java
%package java
Summary:	java-module for collectd.
Group:		System Environment/Daemons
Requires:	collectd = %{version}, jdk >= 1.6
BuildPrereq:	jdk >= 1.6
%description java
This plugin for collectd allows plugins to be written in Java and executed
in an embedded JVM.
%endif

%prep
rm -rf $RPM_BUILD_ROOT
%setup


%build
./build.sh
# bug 468067 "pkg-config --libs OpenIPMIpthread" fails
perl -p -i -e "s/OpenIPMIpthread/OpenIPMI/g" configure

./configure CFLAGS=-"DLT_LAZY_OR_NOW='RTLD_LAZY|RTLD_GLOBAL'" --prefix=%{_prefix} --sbindir=%{_sbindir} --mandir=%{_mandir} --libdir=%{_libdir} --sysconfdir=%{_sysconfdir} \
    %{!?with_java:"--with-java=$JAVA_HOME --enable-java"} \
    --disable-ascent \
    --disable-static \
    --disable-ipvs \
    --enable-mysql \
%ifnarch ppc ppc64 sparc sparc64
    --enable-sensors \
%endif
    --enable-email \
    --enable-apache \
    --enable-perl \
    --enable-unixsock \
    --enable-ipmi \
    --enable-postgresql \
    --enable-iptables \
    --enable-ping \
    --with-libiptc \
    --with-python \
    --with-perl-bindings=INSTALLDIRS=vendor \
    --disable-battery
make

%install
%{__rm} -rf contrib/SpamAssassin
%{__install} -d -m0755 %{buildroot}/%{_datadir}/collectd/collection3/

make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
mkdir -p $RPM_BUILD_ROOT/var/www/cgi-bin
cp contrib/redhat/init.d-collectd $RPM_BUILD_ROOT/etc/rc.d/init.d/collectd
cp contrib/collection.cgi $RPM_BUILD_ROOT/var/www/cgi-bin
mkdir -p $RPM_BUILD_ROOT/etc/collectd.d
mkdir -p $RPM_BUILD_ROOT/var/lib/collectd
### Clean up docs
find contrib/ -type f -exec %{__chmod} a-x {} \;

###Modify Config for Redhat Based Distros
sed -i 's:#BaseDir     "/usr/var/lib/collectd":BaseDir     "/var/lib/collectd":' $RPM_BUILD_ROOT/etc/collectd.conf
sed -i 's:#PIDFile     "/usr/var/run/collectd.pid":PIDFile     "/var/run/collectd.pid":' $RPM_BUILD_ROOT/etc/collectd.conf
sed -i 's:#PluginDir   "/usr/lib/collectd":PluginDir   "%{_libdir}/collectd":' $RPM_BUILD_ROOT/etc/collectd.conf
sed -i 's:#TypesDB     "/usr/share/collectd/types.db":TypesDB     "/usr/share/collectd/types.db":' $RPM_BUILD_ROOT/etc/collectd.conf
sed -i 's:#Interval     10:Interval     30:' $RPM_BUILD_ROOT/etc/collectd.conf
sed -i 's:#ReadThreads  5:ReadThreads  5:' $RPM_BUILD_ROOT/etc/collectd.conf
###Include broken out config directory
echo -e '\nInclude "/etc/collectd.d"' >> $RPM_BUILD_ROOT/etc/collectd.conf

##Move config contribs
cp contrib/redhat/apache.conf $RPM_BUILD_ROOT/etc/collectd.d/apache.conf
cp contrib/redhat/email.conf $RPM_BUILD_ROOT/etc/collectd.d/email.conf
cp contrib/redhat/sensors.conf $RPM_BUILD_ROOT/etc/collectd.d/sensors.conf
cp contrib/redhat/mysql.conf $RPM_BUILD_ROOT/etc/collectd.d/mysql.conf
cp contrib/redhat/nginx.conf $RPM_BUILD_ROOT/etc/collectd.d/nginx.conf
cp contrib/redhat/snmp.conf $RPM_BUILD_ROOT/etc/collectd.d/snmp.conf

# *.la files shouldn't be distributed.
rm -f %{buildroot}/%{_libdir}/{collectd/,}*.la

# Remove Perl hidden .packlist files.
find %{buildroot} -name .packlist -exec rm {} \;

# Remove Perl temporary file perllocal.pod
find %{buildroot} -name perllocal.pod -exec rm {} \;

# copy web interface
cp -ad contrib/collection3/* %{buildroot}/%{_datadir}/collectd/collection3/
rm -f %{buildroot}/%{_datadir}/collectd/collection3/etc/collection.conf
ln -s %{_sysconfdir}/collection.conf %{buildroot}/%{_datadir}/collectd/collection3/etc/collection.conf
chmod +x %{buildroot}/%{_datadir}/collectd/collection3/bin/*.cgi

# Move the Perl examples to a separate directory.
mkdir perl-examples
find contrib -name '*.p[lm]' -exec mv {} perl-examples/ \;


%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add collectd
/sbin/chkconfig collectd on

%preun
if [ "$1" = 0 ]; then
   /sbin/chkconfig collectd off
   /etc/init.d/collectd stop
   /sbin/chkconfig --del collectd
fi
exit 0

%postun
if [ "$1" -ge 1 ]; then
    /etc/init.d/collectd restart
fi
exit 0

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog INSTALL NEWS README contrib/
%config %attr(0644,root,root) /etc/collectd.conf
%attr(0755,root,root) /etc/rc.d/init.d/collectd
%attr(0755,root,root) %{_sbindir}/collectd
%attr(0755,root,root) %{_bindir}/collectd-nagios
%attr(0755,root,root) %{_sbindir}/collectdmon
%attr(0644,root,root) %{_mandir}/man1/*
%attr(0644,root,root) %{_mandir}/man5/*
%dir /etc/collectd.d

# client
%attr(0644,root,root) /usr/include/collectd/client.h
%attr(0644,root,root) /usr/include/collectd/lcc_features.h

%attr(0644,root,root) %{_libdir}/libcollectdclient.*
%attr(0644,root,root) %{_libdir}/pkgconfig/libcollectdclient.pc

# macro to grab binaries for a plugin, given a name
%define plugin_macro() \
%attr(0644,root,root) %{_libdir}/%{name}/%1.so 


%plugin_macro apcups
%plugin_macro bind
%plugin_macro conntrack
%plugin_macro contextswitch
%plugin_macro cpufreq
%plugin_macro cpu
%plugin_macro csv
%plugin_macro curl
%plugin_macro curl_xml
%plugin_macro df
%plugin_macro disk
%plugin_macro entropy
%plugin_macro exec
%plugin_macro filecount
%plugin_macro fscache
%plugin_macro hddtemp
%plugin_macro interface
%plugin_macro iptables
%plugin_macro irq
%plugin_macro load
%plugin_macro logfile
%plugin_macro madwifi

%plugin_macro match_empty_counter
%plugin_macro match_hashed
%plugin_macro match_regex
%plugin_macro match_timediff
%plugin_macro match_value

%plugin_macro mbmon
%plugin_macro memcached
%plugin_macro memory
%plugin_macro multimeter
%plugin_macro network
%plugin_macro nfs
%plugin_macro ntpd
%plugin_macro openvpn
%plugin_macro olsrd
%plugin_macro powerdns
%plugin_macro processes
%plugin_macro protocols
%plugin_macro python
%plugin_macro serial
%plugin_macro swap
%plugin_macro syslog
%plugin_macro table
%plugin_macro tail

%plugin_macro target_notification
%plugin_macro target_replace
%plugin_macro target_scale
%plugin_macro target_set

%plugin_macro tcpconns
%plugin_macro teamspeak2
%plugin_macro ted
%plugin_macro thermal
%plugin_macro unixsock
%plugin_macro uptime
%plugin_macro users
%plugin_macro uuid
%plugin_macro vmem
%plugin_macro vserver
%plugin_macro wireless
%plugin_macro write_http

%attr(0644,root,root) %{_datadir}/%{name}/types.db


%exclude /usr/share/collectd/postgresql_default.conf

%dir /var/lib/collectd

%if %with_java
%files java
%attr(0644,root,root) /usr/share/%{name}/java/org/collectd/api/*.class
%attr(0644,root,root) /usr/share/%{name}/java/org/collectd/java/*.class
%plugin_macro java
%endif

%files apache
%config %attr(0644,root,root) /etc/collectd.d/apache.conf
%plugin_macro apache

%files dns
%plugin_macro dns

%files email
%config %attr(0644,root,root) /etc/collectd.d/email.conf
%plugin_macro email

%files ipmi
%plugin_macro ipmi

%files mysql
%config %attr(0644,root,root) /etc/collectd.d/mysql.conf
%plugin_macro mysql

%files nginx
%config %attr(0644,root,root) /etc/collectd.d/nginx.conf
%plugin_macro nginx

%files -n perl-Collectd 
%attr(0644,root,root) /usr/lib/perl5/vendor_perl/5.8.8/Collectd.pm
%attr(0644,root,root) /usr/lib/perl5/vendor_perl/5.8.8/Collectd/Unixsock.pm
%attr(0644,root,root) /usr/lib/perl5/vendor_perl/5.8.8/Collectd/Plugins/OpenVZ.pm
%attr(0644,root,root) /usr/lib/perl5/vendor_perl/5.8.8/Collectd/Plugins/Monitorus.pm
%attr(0644,root,root) /usr/share/man/man3/Collectd::Unixsock.3pm.gz
%doc perl-examples/*
%doc %{_mandir}/man5/collectd-perl.5*
%doc %{_mandir}/man3/Collectd::Unixsock.3pm*
%plugin_macro perl

%files ping
%plugin_macro ping

%files postgresql
%plugin_macro postgresql

%files rrdtool
%plugin_macro rrdtool

%files sensors
%config %attr(0644,root,root) /etc/collectd.d/sensors.conf
%plugin_macro sensors

%files snmp
%attr(0644,root,root) /etc/collectd.d/snmp.conf
%plugin_macro snmp

%files web
/usr/share/collectd/collection3
%attr(0755,root,root) /var/www/cgi-bin/collection.cgi

%ifnarch ppc ppc64 sparc sparc64
%files virt
%plugin_macro libvirt
%endif


%changelog
* Fri Sep 17 2010 Sam Quigley <quigley@squareup.com> 4.10.0
- Version 4.10.0
- Lots of misc cleanup

* Tue Jan 04 2010 Rackspace <stu.hood@rackspace.com> 4.9.0
- New upstream version
- Changes to support 4.9.0
- Added support for Java/GenericJMX plugin

* Mon Mar 17 2008 RightScale <support@rightscale.com> 4.3.1
- New upstream version
- Changes to support 4.3.1
- Added More Prereqs to support more plugins
- Added support for perl plugin

* Mon Aug 06 2007 Kjell Randa <Kjell.Randa@broadpark.no> 4.0.6
- New upstream version

* Wed Jul 25 2007 Kjell Randa <Kjell.Randa@broadpark.no> 4.0.5
- New major releas
- Changes to support 4.0.5 

* Wed Jan 11 2007 Iain Lea <iain@bricbrac.de> 3.11.0-0
- fixed spec file to build correctly on fedora core
- added improved init.d script to work with chkconfig
- added %post and %postun to call chkconfig automatically

* Sun Jul 09 2006 Florian octo Forster <octo@verplant.org> 3.10.0-1
- New upstream version

* Tue Jun 25 2006 Florian octo Forster <octo@verplant.org> 3.9.4-1
- New upstream version

* Tue Jun 01 2006 Florian octo Forster <octo@verplant.org> 3.9.3-1
- New upstream version

* Tue May 09 2006 Florian octo Forster <octo@verplant.org> 3.9.2-1
- New upstream version

* Tue May 09 2006 Florian octo Forster <octo@verplant.org> 3.8.5-1
- New upstream version

* Fri Apr 21 2006 Florian octo Forster <octo@verplant.org> 3.9.1-1
- New upstream version

* Fri Apr 14 2006 Florian octo Forster <octo@verplant.org> 3.9.0-1
- New upstream version
- Added the `apache' package.

* Thu Mar 14 2006 Florian octo Forster <octo@verplant.org> 3.8.2-1
- New upstream version

* Thu Mar 13 2006 Florian octo Forster <octo@verplant.org> 3.8.1-1
- New upstream version

* Thu Mar 09 2006 Florian octo Forster <octo@verplant.org> 3.8.0-1
- New upstream version

* Sat Feb 18 2006 Florian octo Forster <octo@verplant.org> 3.7.2-1
- Include `tape.so' so the build doesn't terminate because of missing files..
- New upstream version

* Sat Feb 04 2006 Florian octo Forster <octo@verplant.org> 3.7.1-1
- New upstream version

* Mon Jan 30 2006 Florian octo Forster <octo@verplant.org> 3.7.0-1
- New upstream version
- Removed the extra `hddtemp' package

* Tue Jan 24 2006 Florian octo Forster <octo@verplant.org> 3.6.2-1
- New upstream version

* Fri Jan 20 2006 Florian octo Forster <octo@verplant.org> 3.6.1-1
- New upstream version

* Fri Jan 20 2006 Florian octo Forster <octo@verplant.org> 3.6.0-1
- New upstream version
- Added config file, `collectd.conf(5)', `df.so'
- Added package `collectd-mysql', dependency on `mysqlclient10 | mysql'

* Wed Dec 07 2005 Florian octo Forster <octo@verplant.org> 3.5.0-1
- New upstream version

* Sat Nov 26 2005 Florian octo Forster <octo@verplant.org> 3.4.0-1
- New upstream version

* Sat Nov 05 2005 Florian octo Forster <octo@verplant.org> 3.3.0-1
- New upstream version

* Tue Oct 26 2005 Florian octo Forster <octo@verplant.org> 3.2.0-1
- New upstream version
- Added statement to remove the `*.la' files. This fixes a problem when
  `Unpackaged files terminate build' is in effect.
- Added `processes.so*' to the main package

* Fri Oct 14 2005 Florian octo Forster <octo@verplant.org> 3.1.0-1
- New upstream version
- Added package `collectd-hddtemp'

* Fri Sep 30 2005 Florian octo Forster <octo@verplant.org> 3.0.0-1
- New upstream version
- Split the package into `collectd' and `collectd-sensors'

* Fri Sep 16 2005 Florian octo Forster <octo@verplant.org> 2.1.0-1
- New upstream version

* Mon Sep 10 2005 Florian octo Forster <octo@verplant.org> 2.0.0-1
- New upstream version

* Mon Aug 29 2005 Florian octo Forster <octo@verplant.org> 1.8.0-1
- New upstream version

* Sun Aug 25 2005 Florian octo Forster <octo@verplant.org> 1.7.0-1
- New upstream version

* Sun Aug 21 2005 Florian octo Forster <octo@verplant.org> 1.6.0-1
- New upstream version

* Sun Jul 17 2005 Florian octo Forster <octo@verplant.org> 1.5.1-1
- New upstream version

* Sun Jul 17 2005 Florian octo Forster <octo@verplant.org> 1.5-1
- New upstream version

* Mon Jul 11 2005 Florian octo Forster <octo@verplant.org> 1.4.2-1
- New upstream version

* Sat Jul 09 2005 Florian octo Forster <octo@verplant.org> 1.4-1
- Built on RedHat 7.3
