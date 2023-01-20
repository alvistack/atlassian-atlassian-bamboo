# Copyright 2022 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-bamboo
Epoch: 100
Version: 9.1.1
Release: 1%{?dist}
Summary: Atlassian Bamboo
License: Apache-2.0
URL: https://www.atlassian.com/software/bamboo
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: -post-build-checks
Requires(pre): chrpath
Requires(pre): fdupes
Requires(pre): patch
Requires(pre): shadow-utils
Requires(pre): wget

%description
Bamboo is a continuous integration and deployment tool that ties
automated builds, tests and releases together in a single workflow.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%install
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm755 -d %{buildroot}/opt/atlassian/bamboo
install -Dpm644 -t %{buildroot}%{_unitdir} bamboo.service
install -Dpm644 -t %{buildroot}/opt/atlassian/bamboo atlassian-bamboo.patch

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

BAMBOO_DOWNLOAD_URL=http://product-downloads.atlassian.com/software/bamboo/downloads/atlassian-bamboo-9.1.1.tar.gz
BAMBOO_DOWNLOAD_DEST=/tmp/atlassian-bamboo-9.1.1.tar.gz
BAMBOO_DOWNLOAD_CHECKSUM=513de3563824520447d992b58368713ac8a87ddfe8fbbd0882d9a802094d70c7

BAMBOO_CATALINA=/opt/atlassian/bamboo

wget -c $BAMBOO_DOWNLOAD_URL -O $BAMBOO_DOWNLOAD_DEST
echo -n "$BAMBOO_DOWNLOAD_CHECKSUM $BAMBOO_DOWNLOAD_DEST" | sha256sum -c -

mkdir -p $BAMBOO_CATALINA
find $BAMBOO_CATALINA -mindepth 1 | grep -v atlassian-bamboo.patch | xargs rm -rf || echo $?
tar zxf $BAMBOO_DOWNLOAD_DEST -C $BAMBOO_CATALINA --strip-components=1

cat $BAMBOO_CATALINA/atlassian-bamboo.patch | patch -p1
chmod a+x $BAMBOO_CATALINA/bin/start-bamboo.sh
chmod a+x $BAMBOO_CATALINA/bin/stop-bamboo.sh
find $BAMBOO_CATALINA -type f -name '*.so' -exec chrpath -d {} \;
find $BAMBOO_CATALINA -type f -name '*.bak' -delete
find $BAMBOO_CATALINA -type f -name '*.orig' -delete
find $BAMBOO_CATALINA -type f -name '*.rej' -delete
fdupes -qnrps $BAMBOO_CATALINA

chown -Rf bamboo:bamboo $BAMBOO_CATALINA
chmod 0700 $BAMBOO_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%dir /opt/atlassian/bamboo
%{_unitdir}/bamboo.service
/opt/atlassian/bamboo/atlassian-bamboo.patch

%changelog
