Summary:	User-space IPsec tools for the Linux IPsec implementation
Name:		ipsec-tools
Version:	0.2.2
Release:	1
License:	BSD
Group:		Networking/Admin
Source0:	http://dl.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
# Source0-md5: b5493f7a2997130a4f86c486c9993b86
URL:		http://ipsec-tools.sourceforge.net/
BuildRequires:	kernel-headers >= 2.5.54
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
IPsec-Tools is a port of the KAME Project's IPsec tools to the Linux
IPsec implementation. IPsec-Tools provides racoon, an IKE daemon; libipsec,
a PFKey implementation; and setkey, a security policy and security
association database configuration utility.

%prep
%setup  -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc NEWS README ChangeLog
%config %{_sysconfdir}/racoon/*
/sbin/*
/lib/*
%{_includedir}/*
%{_mandir}/man[358]/*
%{_sbindir}/racoon
