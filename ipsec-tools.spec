%bcond_without dist_kernel # use installed kernel

Summary:	User-space IPsec tools for the Linux IPsec implementation
Summary(pl):	Narzêdzia przestrzeni u¿ytkownika dla linuksowej implementacji IPsec
Name:		ipsec-tools
Version:	0.2.2
Release:	3
License:	BSD
Group:		Networking/Admin
Source0:	http://dl.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
# Source0-md5:	c7d6d7b89ffc102041daf6e9615ff9ab
Source1:	%{name}-racoon.init
Patch0:		%{name}-ac_am.patch
# Patch1 - remove CAST128 from the default conf
Patch1:         %{name}-racoon-conf.diff
# Patch2 - sourceforge req. 797347 - racoon segfaults
Patch2:         %{name}-fix.patch
# Patch3 - sourceforge req. 836863 - IPComp fixes
Patch3:         %{name}-ipcomp.patch
# Patch4 - sourceforge req. 837924 - sync with KAME 2003-11-06
Patch4:         %{name}-linux-ipsec-tools.diff-4.patch
# Patch5 - sourceforge req. 848639 - CRL not checked for OpenSSL 0.9.7
Patch5:         %{name}-crl-check.patch
# Patch6 - sourceforge req. 849062 - Update for IPComp incorrectly sending key
Patch6:         %{name}-ipcomp-libipsec.patch
# Patch7 - sourceforge req. 849112 - Eliminate delay before beginning phase 2 negotiation
Patch7:         %{name}-noph2delay.patch
# Patch8 - sourceforge req. 854376 - Reload handler patch
Patch8:         %{name}-reload.diff

URL:		http://ipsec-tools.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	perl
%{!?_with_dist_kernel:BuildRequires:	kernel-headers >= 2.5.54}
Requires:	libipsec = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
IPsec-Tools is a port of the KAME Project's IPsec tools to the Linux
IPsec implementation. IPsec-Tools provides racoon, an IKE daemon;
libipsec, a PFKey implementation; and setkey, a security policy and
security association database configuration utility.

%description -l pl
IPsec-Tools to port narzêdzi IPsec z projektu KAME do linuksowej
implementacji IPsec. IPsec-Tools dostarczaj±: racoona - demona IKE;
libipsec - implementacjê PFKey; oraz setkey - narzêdzie konfiguracyjne
do polityki bezpieczeñstwa oraz asocjacyjnej bazy danych
bezpieczeñstwa.

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
Summary(pl):	Pliki nag³ówkowe biblioteki PFKeyV2
Group:		Development/Libraries
Requires:	libipsec = %{version}

%description -n libipsec-devel
PFKeyV2 library - development files.

%description -n libipsec-devel -l pl
Pliki nag³ówkowe biblioteki PFKeyV2.

%package -n libipsec-static
Summary:	PFKeyV2 static library
Summary(pl):	Biblioteka statyczna PFKeyV2
Group:		Development/Libraries
Requires:	libipsec-devel = %{version}

%description -n libipsec-static
PFKeyV2 static library.

%description -n libipsec-static -l pl
Biblioteka statyczna PFKeyV2.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p0
%patch3 -p1
#%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

%build
perl -pi -e 's!include-glibc!!g' src/Makefile.am

cd src/racoon
install %{_datadir}/automake/config.* .

%{__aclocal}
%{__autoconf}
cd -

%configure \
	%{!?_with_dist_kernel:--with-kernel-headers=/usr/src/linux/include}

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
