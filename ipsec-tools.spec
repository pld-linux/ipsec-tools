# TODO
# - make --with-libradius compile
#

# Conditional build:
%bcond_without	kerberos5	# build with GSSAPI support
%bcond_without	ldap		# build with LDAP support
%bcond_with	radius		# build with radius support
%bcond_with	hip		# build with Host Identity Protocol support
#
Summary:	User-space IPsec tools for the Linux IPsec implementation
Summary(pl.UTF-8):	Narzędzia przestrzeni użytkownika dla linuksowej implementacji IPsec
Name:		ipsec-tools
Version:	0.8.2
Release:	1
License:	BSD
Group:		Networking/Admin
Source0:	http://downloads.sourceforge.net/ipsec-tools/%{name}-%{version}.tar.bz2
# Source0-md5:	d53ec14a0a3ece64e09e5e34b3350b41
Source1:	%{name}-racoon.init
Source2:	%{name}-racoon.sysconfig
Source3:	%{name}.tmpfiles
URL:		http://ipsec-tools.sourceforge.net/
# http://downloads.sourceforge.net/openhip/ipsec-tools-0.6.6-hip.patch
Patch0:		%{name}-hip.patch
Patch1:		%{name}-gssapi.patch
Patch2:		%{name}-support-glibc-2.20.patch
Patch3:		%{name}-link.patch
BuildRequires:	autoconf >= 2.52
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
%{?with_kerberos5:BuildRequires:	heimdal-devel}
BuildRequires:	libselinux-devel
BuildRequires:	libtool
BuildRequires:	linux-libc-headers >= 7:2.6
%{?with_ldap:BuildRequires:	openldap-devel >= 2.4.6}
BuildRequires:	openssl-devel >= 0.9.8s
BuildRequires:	pam-devel
# http://portal-to-web.de/tacacs/libradius.php ?
%{?with_radius:BuildRequires:	libradius-devel}
BuildRequires:	readline-devel
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	libipsec = %{version}-%{release}
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# requires adminsock_path symbol from binary
%define		skip_post_check_so	libracoon.so.*

# needed to use /var/run/racoon as sockdir
%define		_localstatedir		/var/run

%description
IPsec-Tools is a port of the KAME Project's IPsec tools to the Linux
IPsec implementation. IPsec-Tools provides racoon, an IKE daemon;
libipsec, a PFKey implementation; and setkey, a security policy and
security association database configuration utility.

%description -l pl.UTF-8
IPsec-Tools to port narzędzi IPsec z projektu KAME do linuksowej
implementacji IPsec. IPsec-Tools dostarczają: racoona - demona IKE;
libipsec - implementację PFKey; oraz setkey - narzędzie konfiguracyjne
do polityki bezpieczeństwa oraz asocjacyjnej bazy danych
bezpieczeństwa.

%package -n libipsec
Summary:	Shared libipsec and libracoon libraries
Summary(pl.UTF-8):	Biblioteki współdzielone libipsec i libracoon
Group:		Libraries

%description -n libipsec
Shared libipsec and libracoon libraries.

%description -n libipsec -l pl.UTF-8
Biblioteki współdzielone libipsec i libracoon.

%package -n libipsec-devel
Summary:	Header files for libipsec and racoon libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek libipsec i racoon
Group:		Development/Libraries
Requires:	libipsec = %{version}-%{release}

%description -n libipsec-devel
Header files for libipsec and racoon libraries.

%description -n libipsec-devel -l pl.UTF-8
Pliki nagłówkowe bibliotek libipsec i racoon.

%package -n libipsec-static
Summary:	Static libipsec and libracoon libraries
Summary(pl.UTF-8):	Biblioteki statyczne libipsec i libracoon
Group:		Development/Libraries
Requires:	libipsec-devel = %{version}-%{release}

%description -n libipsec-static
Static libipsec and libracoon libraries.

%description -n libipsec-static -l pl.UTF-8
Biblioteki statyczne libipsec i libracoon.

%prep
%setup -q
%{?with_hip:%patch0 -p1}
%patch1 -p1
%patch2 -p1
%patch3 -p1

%{__sed} -i 's!@INCLUDE_GLIBC@!!g' src/Makefile.am
%{__sed} -i 's/-Werror//' configure.ac
%{__sed} -i 's/-R\$[^ ]*\/lib//' configure.ac

%build
%{__libtoolize}
%{__aclocal} -I .
%{__autoconf}
%{__autoheader}
%{__automake}

%configure \
	--enable-adminport \
	--enable-dpd \
	--enable-frag \
	%{?with_kerberos5:--enable-gssapi} \
	--enable-hybrid \
	--enable-idea \
	--enable-natt \
	--enable-rc5 \
	--enable-security-context \
	--enable-shared \
	--enable-stats \
	--with-kernel-headers=%{_includedir} \
	--with-libldap%{!?with_ldap:=no} \
	--with-libpam \
	%{?with_radius:--with-libradius} \
	--with-readline

%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,racoon,sysconfig} \
	$RPM_BUILD_ROOT/usr/lib/tmpfiles.d

%{__make} -j1 install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/racoon
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/racoon
install %{SOURCE3} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf
install src/racoon/samples/*.txt src/racoon/samples/*.conf $RPM_BUILD_ROOT%{_sysconfdir}/racoon

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add racoon
if [ -f /var/lock/subsys/racoon ]; then
	/etc/rc.d/init.d/racoon restart 1>&2
else
	echo "Type \"/etc/rc.d/init.d/racoon start\" to start racoon." 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/racoon ]; then
		/etc/rc.d/init.d/racoon stop >&2
	fi
	/sbin/chkconfig --del racoon
fi

%post	-n libipsec -p /sbin/ldconfig
%postun	-n libipsec -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README ChangeLog src/racoon/{doc,samples} src/setkey/sample*
%attr(755,root,root) %{_sbindir}/plainrsa-gen
%attr(755,root,root) %{_sbindir}/racoon
%attr(755,root,root) %{_sbindir}/racoonctl
%attr(755,root,root) %{_sbindir}/setkey
%attr(754,root,root) /etc/rc.d/init.d/racoon
%attr(750,root,root) %dir %{_sysconfdir}/racoon
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/racoon/*.txt
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/racoon/*.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/racoon
/usr/lib/tmpfiles.d/%{name}.conf
%dir %{_localstatedir}/racoon
%{_mandir}/man5/racoon.conf.5*
%{_mandir}/man8/plainrsa-gen.8*
%{_mandir}/man8/racoon.8*
%{_mandir}/man8/racoonctl.8*
%{_mandir}/man8/setkey.8*

%files -n libipsec
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libipsec.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libipsec.so.0
%attr(755,root,root) %{_libdir}/libracoon.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libracoon.so.0

%files -n libipsec-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libipsec.so
%attr(755,root,root) %{_libdir}/libracoon.so
%{_libdir}/libipsec.la
%{_libdir}/libracoon.la
%{_includedir}/libipsec
%{_includedir}/racoon
%{_mandir}/man3/ipsec_*.3*

%files -n libipsec-static
%defattr(644,root,root,755)
%{_libdir}/libipsec.a
%{_libdir}/libracoon.a
