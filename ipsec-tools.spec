Summary:	User-space IPsec tools for the Linux IPsec implementation
Name:		ipsec-tools
Version:	0.2.2
Release:	1
License:	BSD
Group:		Networking/Admin
Source0:	http://dl.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
# Source0-md5: b5493f7a2997130a4f86c486c9993b86
Source1:	%{name}-racoon.init
Patch0:		%{name}-ac_am.patch
URL:		http://ipsec-tools.sourceforge.net/
BuildRequires:	kernel-headers >= 2.5.54
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	autoconf
BuildRequires:	automake
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
IPsec-Tools is a port of the KAME Project's IPsec tools to the Linux
IPsec implementation. IPsec-Tools provides racoon, an IKE daemon; libipsec,
a PFKey implementation; and setkey, a security policy and security
association database configuration utility.

%package -n libipsec
Summary:        PFKeyV2 library
Group:          Development/Libraries

%description -n libipsec
PFKeyV2 library.

%package -n libipsec-devel
Summary:        PFKeyV2 library - development files
Group:          Development/Libraries

%description -n libipsec-devel
PFKeyV2 library - development files.

%package -n libipsec-static
Summary:        PFKeyV2 static library
Group:          Development/Libraries

%description -n libipsec-static
PFKeyV2 static library.

%prep
%setup  -q
%patch0 -p1

%build
cd src/racoon
install %{_datadir}/automake/config.* .
%{__aclocal}
%{__autoconf}
cd -
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/racoon

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

%post -n libipsec -p /sbin/ldconfig
%postun -n libipsec -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README ChangeLog
%{_sbindir}/*
%attr(755,root,root) %{_sbindir}/racoon
%attr(754,root,root) %{_sysconfdir}/rc.d/init.d/racoon
%attr(750,root,root) %dir %{_sysconfdir}/racoon
%config(noreplace) %verify(not mtime md5 size) %{_sysconfdir}/racoon/*.txt
%config(noreplace) %verify(not mtime md5 size) %{_sysconfdir}/racoon/*.conf
%{_mandir}/man[58]/*

%files -n libipsec
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.*

%files -n libipsec-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%attr(755,root,root) %{_libdir}/lib*.la
%{_includedir}/libipsec
%{_mandir}/man3/*

%files -n libipsec-static
%defattr(644,root,root,755)
%{_libdir}/lib*.a
