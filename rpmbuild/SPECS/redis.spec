%define realname redis

%define orgnize neu

%define realver 5.0.5

%define srcext tar.gz

# Common info

Name: %{realname}

Version: %{realver}

Release: %{orgnize}%{?dist}

Summary:Redis is a memory database software

License:GPL

Source0: %{realname}-%{realver}%{?extraver}.%{srcext}

Source1: redis.service

Source2: redis.conf

Source3: redis

# BuildRequires: gcc jemalloc

%description

Redis is a database base on memory

%post

echo "redis soft nofile 65535" >> /etc/security/limits.conf

echo "redis hard nofile 65535" >> /etc/security/limits.conf

echo "redis soft nproc 65535" >> /etc/security/limits.conf

echo "redis hard nproc 65535" >> /etc/security/limits.conf

echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
sysctl -p


egrep "^redis" /etc/passwd >& /dev/null
if [ $? -ne 0 ]
then
    useradd redis -s /sbin/nologin -M
fi

chown redis.redis -R /redis


if [ "$(cat /etc/redhat-release|sed -r 's/.* ([0-9]+)\..*/\1/')" == "6" ];then
  iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 6379 -j ACCEPT;
  /etc/rc.d/init.d/iptables save
  service iptables restart
  chkconfig redis on
  service redis start
fi

if [ "$(cat /etc/redhat-release|sed -r 's/.* ([0-9]+)\..*/\1/')" == "7" ];then
  firewall-cmd --zone=public --add-port=6379/tcp --permanent
  firewall-cmd --reload
  systemctl daemon-reload
  systemctl start %{name}
fi

%prep

%setup -q -n %{realname}-%{realver}%{?extraver}
#%patch -p1

%build

yum install -y jemalloc

sed -i "s#\$(PREFIX)/bin#%{buildroot}/usr/bin#g" src/Makefile

make -j $(nproc)

%install
%__make install
%__install -D -m755 %{S:1}  %{buildroot}/%{_sysconfdir}/systemd/system/%{name}.service
%__install -D -m755 %{S:2}  %{buildroot}/%{_sysconfdir}/%{name}.conf
%__install -D -m755 %{S:3}  %{buildroot}/%{_sysconfdir}/init.d/%{name}
%__mkdir -p %{buildroot}/redis/{lib,log,run}

%preun

/usr/bin/redis-cli -p 6379 -a redis shutdown &> /dev/null

%postun 

rm -rf /%{name}

userdel -r %{name} &>/dev/null

sed -i "/redis soft nofile 65535/d" /etc/security/limits.conf

sed -i "/redis hard nofile 65535/d" /etc/security/limits.conf

sed -i "/redis soft nproc 65535/d" /etc/security/limits.conf

sed -i "/redis hard nproc 65535/d" /etc/security/limits.conf

sed -i '/vm.overcommit_memory = 1/d' /etc/sysctl.conf
%clean
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_DIR/%{name}-%{version}
%files
%config %{_sysconfdir}/systemd/system/%{name}.service
%config %{_sysconfdir}/%{name}.conf
%config %{_sysconfdir}/init.d/%{name}
%config /redis/lib
%config /redis/log
%config /redis/run
%config /usr/bin/redis-benchmark
%config /usr/bin/redis-check-aof
%config /usr/bin/redis-check-rdb
%config /usr/bin/redis-cli
%config /usr/bin/redis-sentinel
%config /usr/bin/redis-server
%doc
%changelog
