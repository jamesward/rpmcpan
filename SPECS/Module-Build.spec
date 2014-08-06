Name:           %{iov_prefix}-Module-Build
Version:        0.4206
Release:        1%{?dist}
Summary:        Build and install Perl modules
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/Module-Build/
Source0:        http://cpan.metacpan.org/authors/id/L/LE/LEONT/Module-Build-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  %{iov_prefix}
Requires:       %{iov_prefix}(CPAN::Meta) >= 2.110420
Requires:       %{iov_prefix}(ExtUtils::CBuilder) >= 0.27
Requires:       %{iov_prefix}(ExtUtils::Install) >= 0.3
Requires:       %{iov_prefix}(ExtUtils::Manifest) >= 1.54
Requires:       %{iov_prefix}(ExtUtils::Mkbootstrap)
Requires:       %{iov_prefix}(ExtUtils::ParseXS) >= 2.21
Requires:       %{iov_prefix}(Module::Metadata) >= 1.000002
Requires:       %{iov_prefix}(Perl::OSType) >= 1
Requires:       %{iov_prefix}(Test::Harness)
Requires:       %{iov_prefix}(version) >= 0.87
Requires:       %{iov_prefix}

%description
Module::Build is a system for building, testing, and installing Perl
modules. It is meant to be an alternative to ExtUtils::MakeMaker.
Developers may alter the behavior of the module through subclassing in a
much more straightforward way than with MakeMaker. It also does not require
a make on your system - most of the Module::Build code is pure-perl and
written in a very cross-platform way.

%prep
%setup -q -n Module-Build-%{version}

%build
%{__perl} Build.PL --installdirs=vendor
./Build

%install
rm -rf $RPM_BUILD_ROOT

./Build install --destdir=$RPM_BUILD_ROOT create_packlist=0
find $RPM_BUILD_ROOT -depth -type d -exec rmdir {} 2>/dev/null \;

%{_fixperms} $RPM_BUILD_ROOT/*

%check
./Build test

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{perl_vendorlib}/*
%{_bindir}/*
%{_mandir}/man3/*
%{_mandir}/man1/*

%changelog
* Thu Jul 31 2014 David E. Wheeler <david.wheeler@iovation.com> 0.4206-1
- Specfile autogenerated by cpanspec 1.78.
