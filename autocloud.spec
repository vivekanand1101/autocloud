%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname autocloud
%global commit0 415c74f8df1cdebbf25034bd0218d34faf466d24
%global gittag0 GIT-TAG
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})


Name:           autocloud
Version:        0.1
Release:        4%{?dist}
Summary:        A test framework to test Fedora cloud images
Group:          Applications/Internet
License:        GPLv3
URL:            http://github.com/kushaldas/autocloud
Source0:        https://github.com/kushaldas/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  fedmsg
BuildRequires:  python-sqlalchemy
BuildRequires:  python-redis
BuildRequires:  python-retask
BuildRequires:  python-sqlalchemy-utils
BuildRequires:  python-flask
BuildRequires:  systemd

%description
A test framework which automatically downloads and tests Fedora cloud image
builds from koji.

%package common
Summary: autocloud common library

Requires: python-psycopg2

%description common
This package contains the common libraries required by other autocloud
components.

%package web
Summary: Autocloud web interface

Requires: %{name}-common = %{version}-%{release}
Requires: python-flask
Requires: python-flask-restless
Requires: httpd
Requires: mod_wsgi

%description web
This package is for web interface for autocloud.

%package backend
Summary: autocloud backend
Requires: %{name}-common = %{version}-%{release}
Requires: fedmsg-hub
Requires: tunir
Requires: python-sqlalchemy
Requires: python-redis
Requires: python-retask
Requires: python-sqlalchemy-utils
Requires: redis
Requires: fedmsg
Requires: koji


%description backend
This runs a daemon which keeps listening to fedmsg and dispatches messages
to autocloud service for process images.


%prep
%setup -q -n %{name}-%{commit0}

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/fedmsg.d/
%{__cp} fedmsg.d/autocloud.py %{buildroot}%{_sysconfdir}/fedmsg.d/.
%{__cp} fedmsg.d/endpoints-autocloud.py %{buildroot}%{_sysconfdir}/fedmsg.d/.

%{__mkdir_p} %{buildroot}%{_datadir}/%{modname}/
%{__mkdir_p} %{buildroot}/%{_sysconfdir}/httpd/conf.d
install -m 644 apache/%{modname}.wsgi %{buildroot}%{_datadir}/%{modname}/%{modname}.wsgi
install -m 644 apache/%{modname}.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/%{modname}.conf
install -m 644 autocloud_job.py %{buildroot}%{_datadir}/%{modname}/autocloud_job.py
install -m 644 createdb.py %{buildroot}%{_datadir}/%{modname}/createdb.py
mv autocloud/web/static/ %{buildroot}%{_datadir}/%{modname}

%{__mkdir_p} %{buildroot}%{_sbindir}
install -m 755 autocloud_job %{buildroot}%{_sbindir}/autocloud_job

mkdir -p %{buildroot}%{_sysconfdir}/%{modname}/
install -m 644 config/%{modname}.cfg %{buildroot}%{_sysconfdir}/%{modname}/%{modname}.cfg

%{__mkdir_p} %{buildroot}%{_unitdir}
%{__install} -pm644 autocloud.service \
%{buildroot}%{_unitdir}/autocloud.service

rm -rf %{buildroot}%{_datadir}/%{modname}/static/bootstrap

%files common
%doc README.md
%license LICENSE
%dir %{python_sitelib}/%{modname}/
%dir %{_sysconfdir}/%{modname}/
%dir %{_datadir}/%{modname}
%{python_sitelib}/%{modname}/__init__.py*
%{python_sitelib}/%{modname}/models.py*
%{python_sitelib}/%{modname}/utils/*
%{python_sitelib}/%{modname}-%{version}-py%{pyver}.egg-info/
%config(noreplace) %{_sysconfdir}/fedmsg.d/autocloud.py*
%config(noreplace) %{_sysconfdir}/fedmsg.d/endpoints-autocloud.py*
%config(noreplace) %{_sysconfdir}/%{modname}/%{modname}.cfg
%{_datadir}/%{modname}/createdb.py*

%files web
%{python_sitelib}/%{modname}/web/*
%{_datadir}/%{modname}/%{modname}.wsgi
%{_datadir}/%{modname}/static/*
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{modname}.conf

%files backend
%{python_sitelib}/%{modname}/consumer.py*
%{python_sitelib}/%{modname}/producer.py*
%{_datadir}/%{modname}/autocloud_job.py*
%{_sbindir}/autocloud_job
%{_unitdir}/autocloud.service


%changelog
* Wed Sep 23 2015 Praveen Kumar <kumarpraveen.nitdgp@gmail.com> 0.1-4
- Add createdb to proper location
- Remove db creation during rpmbuild

* Wed Sep 23 2015 Kushal Das <kushal@fedoraproject.org> - 0.1-3
- Fixes dependencies

* Tue Sep 22 2015 Ratnadeep Debnath <rtnpro@gmail.com> - 0.1-2
- Updating SPEC based on suggestions from review request.

* Mon Aug 31 2015 Ratnadeep Debnath <rtnpro@gmail.com> - 0.1-1
- Initial packaging.
