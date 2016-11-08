%define _buildid %{nil}

%if 0%{?rhel} >= 7
  %define with_systemd 1
%else
  %define with_upstart 1
%endif

Name:      ec2-net-utils
Summary:   A set of tools for automatic discovery and configuration of network interfaces in AWS cloud
Version:   1.0
Release:   2%{?_buildid}%{?dist}
License:   Apache License 2.0
Group:     System Tools
Packager:  Baurzhan Konurbayev <baurzhan_konurbayev@epam.com>
Source0:   53-ec2-network-interfaces.rules
Source1:   75-persistent-net-generator.rules
Source2:   ec2net-functions
Source3:   ec2net.hotplug
Source4:   ec2ifup
Source5:   ec2ifdown
Source6:   ec2dhcp.sh
Source7:   ec2ifup.8
Source8:   ec2ifscan
Source9:   elastic-network-interfaces.conf
Source10:  ec2ifscan.8

Source20:  ixgbevf.conf
Source21:  acpiphp.modules

# rhel stuff
Source30:  elastic-network-interfaces.service
Source31:  ec2-ifup@.service

URL:       http://developer.amazonwebservices.com/connect/entry.jspa?externalID=1825
BuildArch: noarch
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires:  initscripts
Requires:  bash >= 4
Requires:  curl
Requires:  iproute
%if %{with upstart}
Requires:  upstart
%endif
%if %{with systemd}
BuildRequires: systemd-units
%endif

%description
A set of tools for automatic discovery and configuration of network interfaces in AWS cloud.

%prep

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/sbin
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/network-scripts/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dhcp/dhclient.d/
%if %{with upstart}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/init/
%endif
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8/

install -m755 %{SOURCE4} $RPM_BUILD_ROOT/sbin/
install -m755 %{SOURCE5} $RPM_BUILD_ROOT/sbin/
install -m755 %{SOURCE8} $RPM_BUILD_ROOT/sbin/
install -m644 %{SOURCE0} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/
%if %{with upstart}
install -m644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/
%endif
install -m644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/network-scripts/
install -m755 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/network-scripts/
install -m755 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/dhcp/dhclient.d/
%if %{with upstart}
install -m644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/init
%endif
install -m644 %{SOURCE7} $RPM_BUILD_ROOT%{_mandir}/man8/ec2ifup.8
ln -s ./ec2ifup.8.gz $RPM_BUILD_ROOT%{_mandir}/man8/ec2ifdown.8.gz
install -m644 %{SOURCE10} $RPM_BUILD_ROOT%{_mandir}/man8/ec2ifscan.8

%if %{with systemd}
%{__install} -d -m 0775 ${RPM_BUILD_ROOT}%{_unitdir}
%{__install} -m 0644 %{SOURCE30} ${RPM_BUILD_ROOT}%{_unitdir}
%{__install} -m 0644 %{SOURCE31} ${RPM_BUILD_ROOT}%{_unitdir}
%endif

# add module configs
install -m644 -D %{SOURCE20} $RPM_BUILD_ROOT/etc/modprobe.d/ixgbevf.conf
install -m755 -D %{SOURCE21} $RPM_BUILD_ROOT/etc/sysconfig/modules/acpiphp.modules

%clean
rm -rf $RPM_BUILD_ROOT

%files
/sbin/ec2ifup
/sbin/ec2ifdown
/sbin/ec2ifscan
%{_sysconfdir}/udev/rules.d/53-ec2-network-interfaces.rules
%if %{with upstart}
%{_sysconfdir}/udev/rules.d/75-persistent-net-generator.rules
%endif
%{_sysconfdir}/modprobe.d/ixgbevf.conf
%{_sysconfdir}/sysconfig/modules/acpiphp.modules
%{_sysconfdir}/sysconfig/network-scripts/ec2net-functions
%{_sysconfdir}/sysconfig/network-scripts/ec2net.hotplug
%{_sysconfdir}/dhcp/dhclient.d/ec2dhcp.sh
%if %{with upstart}
%{_sysconfdir}/init/elastic-network-interfaces.conf
%endif
%{_mandir}/man8/ec2ifup.8.gz
%{_mandir}/man8/ec2ifdown.8.gz
%{_mandir}/man8/ec2ifscan.8.gz

%if %{with systemd}
%{_unitdir}/elastic-network-interfaces.service
%{_unitdir}/ec2-ifup@.service
%endif

%if %{with systemd}
%post
%systemd_post elastic-network-interfaces.service
%systemd_post ec2-ifup@.service

%preun
%systemd_preun elastic-network-interfaces.service
%systemd_preun ec2-ifup@.service

%postun
%systemd_postun elastic-network-interfaces.service
%systemd_postun ec2-ifup@.service
%endif