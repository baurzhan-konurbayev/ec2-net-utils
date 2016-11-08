## ec2-net-utils for RHEL/systemd/upstart

This is a fork of Amazon's ec2-utils with modifications to support Elastic Network Interfaces (ENI) under systemd.

The spec file produces RPM ec2-net-utils.  The ec2-net-utils RPM contains ENI support.  It allows you to attach an ENI to a running instance and have it work as you would expect.

## Install

Copy folders SOURCES and SPECS into the folder ~/rpmbuild/
Under the folder ~/rpmbuild/SPECS run 'rpmbuild -ba ec2-utils.spec'

* Imporant! Don't forget to enable the `elastic-network-interfaces` systemd unit, or ENI's won't work at boot!

## OS Support

* ✓ RHEL 6/7

## How does it work

A udev rule runs `ec2net.hotplug` when a device is added or removed, which is a script that writes interface config, including source route setup.  It relies on the primary interface having come up so it can query AWS metadata.

Another udev rule starts the `ec2-ifup@` service when an interface is added, and a third one runs `/sbin/ifdown` on device removal.  The original version from AWS relied on net.hotplug to do this.

Finally, `elastic-network-interfaces.service` is run late in the boot process.  It calls `ec2ifscan` which fires another udev add event for any interface which is not configured.  This handles the case of booting with an ENI that `ec2net.hotplug` hasn't had a chance to configure yet.

## Complications

* udev add events are fired during boot, during 'attach', and a second time during boot for the unconfigured case.  Meanwhile, network-scripts expects to manage any interface with a cfg that exists at boot.  So the udev events have to be ignored in the appropriate cases.
* Fedora 20 uses a kernel feature (address lifetime) which removes expired addresses, even if dhclient isn't running.  So dhclient must be kept running or the address will be dropped.
* Systemd kills any long-running processes that are spawned by scripts that are run by udev.  To be kept alive, dhclient must be started by a service started by udev (hence `ec2-ifup@`).

## This is a mess!

Yeah, but it's not easy to untangle it from network-scripts without porting to NetworkManager, and it's not clear if NetworkManager is even the way forward (with systemd-networkd on the horizon).  If Amazon Linux ever switches to systemd, they'll probably come up with a cleaner solution.