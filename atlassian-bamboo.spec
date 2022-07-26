%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-bamboo
Epoch: 100
Version: 8.2.5
Release: 1%{?dist}
Summary: Atlassian Bamboo
License: Apache-2.0
URL: https://www.atlassian.com/software/bamboo
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: chrpath
BuildRequires: fdupes
Requires(pre): shadow-utils
Requires: java

%description
Bamboo is a continuous integration and deployment tool that ties
automated builds, tests and releases together in a single workflow.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%install
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm755 -d %{buildroot}/opt/atlassian/bamboo
cp -rfT bamboo %{buildroot}/opt/atlassian/bamboo
install -Dpm644 -t %{buildroot}%{_unitdir} bamboo.service
chmod a+x %{buildroot}/opt/atlassian/bamboo/bin/start-bamboo.sh
chmod a+x %{buildroot}/opt/atlassian/bamboo/bin/stop-bamboo.sh
find %{buildroot}/opt/atlassian/bamboo -type f -name '*.so' -exec chrpath -d {} \;
find %{buildroot}/opt/atlassian/bamboo -type f -name '*.bak' -delete
find %{buildroot}/opt/atlassian/bamboo -type f -name '*.orig' -delete
find %{buildroot}/opt/atlassian/bamboo -type f -name '*.rej' -delete
fdupes -qnrps %{buildroot}/opt/atlassian/bamboo

%check

%pre
set -euxo pipefail

BAMBOO_HOME=/var/atlassian/application-data/bamboo

if [ ! -d $BAMBOO_HOME -a ! -L $BAMBOO_HOME ]; then
    mkdir -p $BAMBOO_HOME
fi

if ! getent group bamboo >/dev/null; then
    groupadd \
        --system \
        bamboo
fi

if ! getent passwd bamboo >/dev/null; then
    useradd \
        --system \
        --gid bamboo \
        --home-dir $BAMBOO_HOME \
        --no-create-home \
        --shell /usr/sbin/nologin \
        bamboo
fi

chown -Rf bamboo:bamboo $BAMBOO_HOME
chmod 0750 $BAMBOO_HOME

%post
set -euxo pipefail

BAMBOO_CATALINA=/opt/atlassian/bamboo

chown -Rf bamboo:bamboo $BAMBOO_CATALINA
chmod 0700 $BAMBOO_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%{_unitdir}/bamboo.service
/opt/atlassian/bamboo

%changelog
