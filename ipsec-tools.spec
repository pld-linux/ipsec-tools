#
# Conditional build:
%bcond_without	kerberos5	# build without GSSAPI support
#
Summary:	User-space IPsec tools for the Linux IPsec implementation
Summary(pl):	Narz�dzia przestrzeni u�ytkownika dla linuksowej implementacji IPsec
Name:		ipsec-tools
Version:	0.3.1
Release:	0.1
License:	BSD
Group:		Networking/Admin
Source0:	http://dl.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
# Source0-md5:	16612755f96e6453bacdbeff5be72759
Source1:	%{name}-racoon.init
# sourceforge req. 849112 - Eliminate delay before beginning phase 2 negotiation
#Patch0:         %{name}-noph2delay.patch
Patch1:		%{name}-salen.patch
Patch2:		%{name}-install.patch
URL:		http://ipsec-tools.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
%{?with_kerberos5:BuildRequires:	heimdal-devel}
BuildRequires:	libtool
BuildRequires:	linux-libc-headers >= 7:2.5.54
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	perl-base
Requires:	libipsec = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
IPsec-Tools is a port of the KAME Project's IPsec tools to the Linux
IPsec implementation. IPsec-Tools provides racoon, an IKE daemon;
libipsec, a PFKey implementation; and setkey, a security policy and
security association database configuration utility.

%description -l pl
IPsec-Tools to port narz�dzi IPsec z projektu KAME do linuksowej
implementacji IPsec. IPsec-Tools dostarczaj�: racoona - demona IKE;
libipsec - implementacj� PFKey; oraz setkey - narz�dzie konfiguracyjne
do polityki bezpiecze�stwa oraz asocjacyjnej bazy danych
bezpiecze�stwa.

%package -n libipsec
Summary:	PFKeyV2 library
Summary(pl):	Biblioteka PFKeyV2
Group:		Libraries

%description -n libipsec
PFKeyV2 library.

%description -n libipsec -l pl
Biblioteka PFKeyV2.

%package -n libipsec-devel
Summary:	PFKeyV2 library - development files
Summary(pl):	Pliki nag��wkowe biblioteki PFKeyV2
Group:		Development/Libraries
Requires:	libipsec = %{version}-%{release}

%description -n libipsec-devel
PFKeyV2 library - development files.

%description -n libipsec-devel -l pl
Pliki nag��wkowe biblioteki PFKeyV2.

%package -n libipsec-static
Summary:	PFKeyV2 static library
Summary(pl):	Biblioteka statyczna PFKeyV2
Group:		Development/Libraries
Requires:	libipsec-devel = %{version}-%{release}

%description -n libipsec-static
PFKeyV2 static library.

%description -n libipsec-static -l pl
Biblioteka statyczna PFKeyV2.

%prep
%setup -q
#%patch0 -p1
%patch1 -p1
%patch2 -p1

%{__perl} -pi -e 's!include-glibc!!g' src/Makefile.am
%{__perl} -pi -e 's!<gssapi/gssapi\.h>!"/usr/include/gssapi.h"!' src/racoon/gssapi.h
%{__perl} -pi -e 's/-O //' src/racoon/configure.in

%build
cd src/racoon
install /usr/share/automake/config.* .
%{__aclocal}
%{__autoconf}
cd -
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}

%configure \
	%{?with_kerberos5:--enable-gssapi} \
	--with-kernel-headers=/usr/include \
	--enable-shared

touch src/.includes

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/racoon

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
%doc NEWS README ChangeLog
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) %{_sysconfdir}/rc.d/init.d/racoon
%attr(750,root,root) %dir %{_sysconfdir}/racoon
%config(noreplace) %verify(not mtime md5 size) %{_sysconfdir}/racoon/*.txt
%config(noreplace) %verify(not mtime md5 size) %{_sysconfdir}/racoon/*.conf
%{_mandir}/man[58]/*

%files -n libipsec
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.*.*.*

%files -n libipsec-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_includedir}/libipsec
%{_mandir}/man3/*

%files -n libipsec-static
%defattr(644,root,root,755)
%{_libdir}/lib*.a
