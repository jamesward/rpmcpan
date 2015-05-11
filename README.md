Modern Perl RPM Packager
========================

This project manages the creation and maintenance of modern Perl 5 RPMs, and
selected CPAN distributions. It's designed to be run directly from a Git
clone. To build it, just run:

    ./bin/rpmcpan --version 5.20.1

This will build Perl and all of the modules. If it has been built previously
from the same Git branch, then only updated CPAN modules or modules for which
no RPM exists in the `repo` directory will be built. This is to keep the
number of things that get built on each run to a minimum.

The RPMs built by `rpmcpan` will have names like `perl520` and
`perl520-Try-Tiny` and will all be installed in `/usr/local/perl520`. You can
modify the version of Perl to build with the `--version` option, and the
prefix with the `--prefix` options, e.g.:

    ./bin/rpmcpan --version 5.18.2 --prefix /opt/local/iovperl

But you probably won't want to mess with the prefix.

If you want to rebuild *all* of the RPMs, not just those that have been
updated since the last run, pass `--all`.

    ./bin/rpmcpan --version 5.20.1 --all

Options
-------

* `--version`: The version of Perl to build. Defaults to the version used to
  run `rpmcpan`.
* `--epoch`: The epoch to use. Defaults to minor version when using the system
  Perl; otherwise not set.
* `-f` `--prefix`: The path prefix. Defaults to `$Config{prefix}` for the
   system Perl; `/usr/local/perl5xx` otherwise.
* `-c` `--config`: Distribution configuration JSON file.
* `--all`: Delete the local repo and build all new RPMs.
* `-v` `--verbose`: Incremental verbosity.
* `-r` `--repo`: Directory to use for local repo. Defaults to `./repo`.
* `--admin`: Email address to use for the Perl admin contact info.
* `-p` `--packager`: Name and email address of the packager.
* `-d` `--dist`: Distribution to build. May be specified multiple times.
* `--die`: Die on first error.
* `--no-perl`: Don't check or build Perl itself. Used internally.

Adding CPAN Distributions
-------------------------

To add a CPAN distribution, simply add it to the `etc/dists.json` file, like
so:

    "App-Sqitch": {},

The JSON object after the distribution name supports a number of keys:

* `rpm_name`: The name to use for the RPM, after the prefixed "perl-".
  Defaults to the distribution name.

* `no_system_prefix`: Set to true to suppress the `perl-` prefix in the name
  of the RPM when building against the systerm Perl. Builds against other
  versions will still get the `perl5xx-` prefix.
* `provides`: A list of additional features provided by the RPM, in case the
  list fetched from MetaCPAN is incomplete. Mostly used to name programs,
  since MetaCPAN is aware only of modules.
* `requires`: A list of non-CPAN-derived RPMs required for the resulting RPM
  to be used. Normally needed only for third-party RPMS, such as `libxml2` or
  `httpd`.
* `conflicts`: A list of non-CPAN-derived RPMs with which thge resulting RPM
  conflicts.
* `exclude_requires`: A list of CPAN modules to exclude from the list of
  runtime prereqs returned by the MetaCPAN API. Useful for excluding
  incompatible or circular dependencies.
* `build_requires`: A list of non-CPAN-derived RPMs required to build the RPM.
  Normally needed only for third-party RPMS, such as `httpd-devel` or
  `postgresql`.
* `exclude_build_requires`: A list of CPAN modules to exclude from the list of
  non-runtime prereqs returned by the MetaCPAN API. Useful for excluding
  incompatible or circular dependencies.
* `cpan_conflicts`: An array of CPAN distributions with which the resulting
   RPM for the distribution will conflict.
* `envrionment`: An object defining environment variables required to build
   the RPM. Keys should be environment variable names, and values their
   values.
* `patch`: A list of patches to be applied to the source before buildling.
  Each will be applied with `patch -p1`, so make sure your prefixes are
  correct.
* `download_url`: The URL from which to download the source code. Probably need
  to also set `archive` if you set this key.
* `archive`: The name of the downloadaed archive. Probably needs to be
  set to the base name of the `download_url` if `download_url` is set.
* `missing_prereqs`: A list of JSON objects describing required modules
   missing from the metadata downloaded from MetaCPAN. Requires these keys:
    * `module`: Name of the required module.
    * `version`: Minimum required version of the module.
    * `phase`: The phase during which the module will be used. Must be one of
      "configure", "build", "test", "runtime", or "develop".
    * `relationship`: The dependency relationship for the module. Must be one
       of "requires", "recommends", "suggests", or "conflicts".

`rpmcpan` will use this information to download the required distributions,
determine their dependencies, create RPM spec files in the `SPECS` directory,
and build RPMs for all the distributions and their CPAN dependencies. Most of
the time none of the object keys will be required.

Customizing Builds
------------------

In some cases, the installation will be more complicated than the generated
RPM spec file can handle. In those cases, you can create a custom spec file
named for the distribiution in the `etc` directory. `rpmcpan` will use such
included spec files in preference to generating one of its own. You can use any
of the following macros in the spec file to customize the build:

* `%version`: The version of the distribution.
* `%etime`: The Unix epoch time in seconds since 1970.
* `%__perl`: The path to the perl against which the RPM will be built.
* `%plv`: A simple Perl version prefix, such as "520" for 5.20.x or
  "518" for 5.18.x. Not set when building against the system Perl.
* `%plfullv`: The full version of Perl, including major, minor, and patch
   version, e.g., "5.18.3".
* `%epoch`: The value do to use for the Epoch label. Set to the Perl minor
  version when building aginst the system Perl, and undefined otherwise.
* `%_prefix`: Path to the directory into which the distrbiution should be
  installed.
* `%sitemandir`: Directory into which site builds of modules should install
  their man pages.
* `%vendormandir`: Directory into which vendor builds of modules should
  install their man pages.

When creating the spec file header section, these three values are
recommended, assuming a spec file named `My-Distribution.spec`:

    Name:           perl%{plv}-My-Distribution
    Version:        %(echo %{version})
    Release:        1.%{?dist}

Dependencies on other CPAN modules should use a `perl%{plv}` prefix, like so:

    Requires:       perl%{plv}(App::Info)

CPAN Build depenencies should require RPMs rather than provided modules,
again with the `perl%{plv}` prefix:

    BuildRequires   perl%{plv}-DBD-Pg

Auto-generation of required and provided details should be fitered through the
included `bin/filter-requires` and `bin/filter-provides` scripts, to ensure
that all are properly prefixed, like so:

    %define _use_internal_dependency_generator 0
    %define __find_provides bin/filter-provides perl%{plv}
    %define __find_requires bin/filter-requires perl%{plv}

Note that `__find_requires` can take an additional argument, a regular
expression to be passed to `grep` to filter out any bogusly-detected prerequisites.

The build should gnerally use the vendor installation directories. A
`Makefile.PL`-based build does it like this:

    %{__perl} Makefile.PL INSTALLDIRS=vendor OPTIMIZE="$RPM_OPT_FLAGS"

While a `Build.PL`-based build does this:

    %{__perl} Build.PL --installdirs=vendor --optimize="$RPM_OPT_FLAGS"

The simplest way to set up the `%files` section is to just require the whole
prefix:

    %files
    %defattr(-,root,root,-)
    %{_prefix}/*

But you can also use the `%_bindir`, `%perl_vendorlib`, `%perl_vendorarch`,
and `%vendormandir` macros. If you did not do a vendor build (shame on you!),
you can use the `site` versions of those macros, instead.

Copyright & License
-------------------
Copyright 2014 [iovation, Inc.](http://iovation.com/) Some Rights Reserved.

This program is free software; you can redistribute it and/or modify it under
the same terms as Perl itself.

Author
------
* [David E. Wheeler](mailto:david.wheeler@iovation.com)
