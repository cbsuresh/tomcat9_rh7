%define __jar_repack %{nil}
%define debug_package %{nil}
%define tomcat_home /opt/tomcat9
%define tomcat_user_home /home/tomcat
%define tomcat_group tomcat
%define tomcat_user tomcat
%define tomcat_uid 790
%define tomcat_gid 790

# distribution specific definitions
%define use_systemd (0%{?rhel} && 0%{?rhel} >= 7)

%if 0%{?rhel}  == 6
Requires(pre): shadow-utils
Requires: initscripts >= 8.36
Requires(post): chkconfig
%endif

%if 0%{?rhel}  == 7
Requires(pre): shadow-utils
Requires: systemd
BuildRequires: systemd
%endif

# end of distribution specific definitions

Summary:    Apache Servlet/JSP Engine
Name:       tomcat
Version:    9.0.24
Release:    1%{?dist}
BuildArch:  noarch
License:    Apache 
Group:      Applications/Internet
URL:        https://tomcat.apache.org/
Vendor:     Apache Software Foundation
Packager:   Suresh Babu Chorampalli Bharat <schorampalli@usda.gov>
Source0:    apache-tomcat-%{version}.tar.gz
Source1:    %{name}.service
Source2:    %{name}.init
Source3:    %{name}.logrotate
Requires:   jre >= 1.8
BuildRoot:  %{_tmppath}/tomcat-%{version}-%{release}-root-%(%{__id_u} -n)

Provides: tomcat
Provides: tomcat9

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.


%prep
%setup -q -n apache-tomcat-%{version}

%build

%install
install -d -m 755 %{buildroot}/%{tomcat_home}/
cp -R * %{buildroot}/%{tomcat_home}/

# Remove *.bat -->BAT files for Windows Installs--.
rm -f %{buildroot}/%{tomcat_home}/bin/*.bat

# Clean webapps Put webapps in app/tomcat/webapps and link back --WEBAPPS--.
mkdir -p /app/tomcat/webapps
# chown -R %{tomcat_uid}.%{tomcat_group} /app/%{name}
cp -Rp /opt/tomcat9/webapps/* /app/tomcat/webapps  > /dev/null 2>&1 || :
/bin/rm -rf %{buildroot}/%{tomcat_home}/webapps
install -d -m 755 %{buildroot}%{tomcat_home}/webapps
cd %{buildroot}/%{tomcat_home}/
/bin/rm -rf webapps
ln -sf /app/%{name}/webapps webapps
cd -

# Put conf in /etc/ and link back.
install -d -m 755 %{buildroot}/%{_sysconfdir}
mv %{buildroot}/%{tomcat_home}/conf %{buildroot}/%{_sysconfdir}/%{name}
/bin/rm -rf %{buildroot}/%{tomcat_home}/conf
cd %{buildroot}/%{tomcat_home}/
ln -sf %{_sysconfdir}/%{name} conf
cd -


# Put logging in /var/log and link back ---LOGGING---.
rm -rf %{buildroot}/%{tomcat_home}/logs
install -d -m 755 %{buildroot}/var/log/%{name}/
cd %{buildroot}/%{tomcat_home}/
ln -sf /var/log/%{name}/ logs
cd -

%if %{use_systemd}
# install systemd-specific files
%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
%{__install} -m644 %SOURCE1 \
        $RPM_BUILD_ROOT%{_unitdir}/%{name}.service
%else
# install SYSV init stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_initrddir}
%{__install} -m755 %{SOURCE2} \
   $RPM_BUILD_ROOT%{_initrddir}/%{name}
%endif

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%{__install} -m 644 -p %{SOURCE3} \
   $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%pre
mkdir -p %{tomcat_user_home}
getent group %{tomcat_group} >/dev/null || groupadd -r %{tomcat_group} -g %{tomcat_gid} 
getent passwd %{tomcat_user} >/dev/null || /usr/sbin/useradd --comment "Tomcat Daemon User" --shell /sbin/nologin -M -r -g %{tomcat_group} -u %{tomcat_uid} --home %{tomcat_user_home} %{tomcat_user}
chown -R %{tomcat_uid}.%{tomcat_group} %{tomcat_user_home}
chmod 700 %{tomcat_user_home}

%files
%defattr(-,%{tomcat_user},%{tomcat_group})
%{tomcat_home}/*
/var/log/%{name}/

%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*

%if %{use_systemd}
%{_unitdir}/%{name}.service
%else
%{_initrddir}/%{name}
%endif


%post
# Register the tomcat service
if [ $1 -eq 1 ]; then
%if %{use_systemd}
    /usr/bin/systemctl preset %{name}.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl enable %{name}.service >/dev/null 2>&1 ||:
    /bin/chown -R %{tomcat_uid}.%{tomcat_group} /var/log/tomcat
    /bin/chown -R %{tomcat_uid}.%{tomcat_group} /app/%{name}
%else
    /sbin/chkconfig --add %{name}
    /sbin/chkconfig --level 2345 %{name} on 
%endif

cat <<BANNER
----------------------------------------------------------------------

Please find the official documentation for tomcat here:
* https://tomcat.apache.org/

Apache Tomcat RN for %{name}.%{version} completed Install successfully.

----------------------------------------------------------------------
BANNER
fi

%preun
if [ $1 -eq 0 ]; then
%if %use_systemd
    /usr/bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl stop %{name}.service >/dev/null 2>&1 ||:
    /usr/sbin/userdel -f %{name}
    /bin/rm -rf %{tomcat_home}
%else
    /sbin/service %{name} stop > /dev/null 2>&1
    /sbin/chkconfig --del %{name} 
    /usr/sbin/userdel -f %{name}
    /bin/rm -rf %{tomcat_home}
%endif
fi

%postun
%if %use_systemd
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 ||:
%endif
if [ $1 -ge 1 ]; then
    /sbin/service %{name}  status  >/dev/null 2>&1 || exit 0
fi


%changelog
* Sat Sep 28 2019 Suresh Chorampalli  <schorampalli@usda.gov>
- Initial release Tomcat 9.0.24.
