# TODO
# - make --with-libradius compile
#
# Conditional build:
%bcond_without	kerberos5	# build with GSSAPI support
%bcond_with	radius		# build with radius support
%bcond_with	hip		# build with Host Identity Protocol support
#
Summary:	User-space IPsec tools for the Linux IPsec implementation
Summary(pl.UTF-8):	Narzędzia przestrzeni użytkownika dla linuksowej implementacji IPsec
Name:		ipsec-tools
Version:	0.7
Release:	2
License:	BSD
Group:		Networking/Admin
Source0:	http://dl.sourceforge.net/ipsec-tools/%{name}-%{version}.tar.bz2
# Source0-md5:	c0a586924edde35264ecfe94ad1c261f
Source1:	%{name}-racoon.init
Source2:	%{name}-racoon.sysconfig
URL:		http://ipsec-tools.sourceforge.net/
# http://downloads.sourceforge.net/openhip/ipsec-tools-0.6.6-hip.patch
Patch0:		%{name}-hip.patch
BuildRequires:	autoconf >= 2.52
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
%{?with_kerberos5:BuildRequires:	krb5-devel}
BuildRequires:	libtool
BuildRequires:	linux-libc-headers >= 7:2.5.54
BuildRequires:	openldap-devel >= 2.4.6
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	pam-devel
# http://portal-to-web.de/tacacs/libradius.php ?
%{?with_radius:BuildRequires:	libradius-devel}
BuildRequires:	readline-devel
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	libipsec = %{version}-%{release}
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
Summary:	PFKeyV2 library
Summary(pl.UTF-8):	Biblioteka PFKeyV2
Group:		Libraries

%description -n libipsec
PFKeyV2 library.

%description -n libipsec -l pl.UTF-8
Biblioteka PFKeyV2.

%package -n libipsec-devel
Summary:	PFKeyV2 library - development files
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki PFKeyV2
Group:		Development/Libraries
Requires:	libipsec = %{version}-%{release}

%description -n libipsec-devel
PFKeyV2 library - development files.

%description -n libipsec-devel -l pl.UTF-8
Pliki nagłówkowe biblioteki PFKeyV2.

%package -n libipsec-static
Summary:	PFKeyV2 static library
Summary(pl.UTF-8):	Biblioteka statyczna PFKeyV2
Group:		Development/Libraries
Requires:	libipsec-devel = %{version}-%{release}

%description -n libipsec-static
PFKeyV2 static library.

%description -n libipsec-static -l pl.UTF-8
Biblioteka statyczna PFKeyV2.

%prep
%setup -q
%{?with_hip:%patch0 -p1}

%{__sed} -i 's!@INCLUDE_GLIBC@!!g' src/Makefile.am
%{__sed} -i 's/-Werror//' configure.ac
%{__sed} -i 's/-R$libradius_dir\/lib//' configure.ac

%build
%{__libtoolize}
%{__aclocal} -I .
%{__autoconf}
%{__autoheader}
%{__automake}

%configure \
	--enable-adminport \
	--enable-rc5 \
	--enable-idea \
	--enable-hybrid \
	--enable-frag \
	%{?with_kerberos5:--enable-gssapi} \
	--enable-stats \
	--enable-dpd \
	--enable-fastquit \
	--enable-natt \
	--enable-security-context \
	--with-kernel-headers=%{_includedir} \
	--with-readline \
	%{?with_radius:--with-libradius} \
	--with-libpam \
	--with-libldap \
	--enable-shared

%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,racoon,sysconfig}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/racoon
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/racoon
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
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/racoon
%attr(750,root,root) %dir %{_sysconfdir}/racoon
%attr(600,root,root) %{_sysconfdir}/racoon/*.txt
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/racoon/*.txt
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/racoon/*.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/racoon
%dir %{_localstatedir}/racoon
%{_mandir}/man[58]/*

%files -n libipsec
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libipsec.so.*.*.*
%attr(755,root,root) %{_libdir}/libracoon.so.*.*.*

%files -n libipsec-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libipsec.so
%attr(755,root,root) %{_libdir}/libracoon.so
%{_libdir}/libipsec.la
%{_libdir}/libracoon.la
%{_includedir}/libipsec
%{_includedir}/racoon
%{_mandir}/man3/*

%files -n libipsec-static
%defattr(644,root,root,755)
%{_libdir}/libipsec.a
%{_libdir}/libracoon.a
