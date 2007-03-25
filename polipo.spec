Summary:	Polipo - a caching web proxy
Summary(pl.UTF-8):	Polipo - mały serwer cache-proxy
Name:		polipo
Version:	1.0.0
Release:	0.1
Epoch:		0
License:	distributable
Group:		Networking/Daemons
Source0:	http://www.pps.jussieu.fr/~jch/software/files/polipo/%{name}-%{version}.tar.gz
# Source0-md5:	e9db1fadbce47b8664351d14510bd5c9
Source1:	%{name}.init
Patch0:		%{name}-Makefile.patch
URL:		http://www.pps.jussieu.fr/~jch/software/polipo/
BuildRequires:	autoconf
BuildRequires:	texinfo
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Polipo is a caching web proxy designed to be used as a personal cache
or a cache shared among a few users.

%description -l pl.UTF-8
Polipo jest buforującym serwerem proxy przeznaczonym do użycia
prywatnego lub dla niewielkiej liczby użytkowników.

%prep
%setup -q
%patch0 -p1

%build
%{__make} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags}" \
	PREFIX="%{_prefix}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}
install -d $RPM_BUILD_ROOT%{_datadir}/info

install -D %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install -D config.sample $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config
touch $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/forbidden

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX="%{_prefix}"

# /etc/sysconfig/polipo
cat << EOF > $RPM_BUILD_ROOT/etc/sysconfig/%{name}
# Customized setings for %{name}

# Nice level:
SERVICE_RUN_NICE_LEVEL="+1"

EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1
/sbin/chkconfig --add %{name}
if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi
	/sbin/chkconfig --del %{name}
fi

%postun
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%files
%defattr(644,root,root,755)
%doc CHANGES COPYING INSTALL README
%attr(755,root,root) %{_bindir}/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/config
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/forbidden
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_datadir}/%{name}
%dir %{_var}/cache/%{name}
%{_mandir}/man1/*
%{_infodir}/*
