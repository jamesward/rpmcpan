iovation Perl RPM Packager
==========================

This project manages the creation and maintenance of iovation's Perl 5 RPMs,
including all modules required for iovation Perl applications. It's designed
to be run directly from a Git clone. To build it, just run:

    ./bin/rpmcpan --version 5.20.0

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

If you want to rebuild *all* of the RPMs, not just those that have had their
spec files changed, pass `--all`.

    ./bin/rpmcpan --version 5.20.1 --all

Adding CPAN Distributions
-------------------------

To add a CPAN distribution, simply add it to the `etc/dists.json` file, like
so:

    "App-Sqitch": {},

The JSON object after the distribution name suppors a number of keys:

* `provides`: A list of additional features provided by the RPM, in case the
  list fetched from MetaCPAN is incomplete. Mostly used to name programs,
  since MetaCPAN is aware only of modules.
* `requires`: A list of non-CPAN-derived RPMs required for the resulting RPM
  to be used. Normally needed only for third-party RPMS, such as `libxml2` or
  `httpd`.
* `build_requires`: A list of non-CPAN-derived RPMs required to build the RPM.
  Normally needed only for third-party RPMS, such as `httpd-devel` or
  `postgresql`.
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
* `%dist`: The Unix epoch time in seconds since 1970.
* `%__perl`: The path to the perl against which the RPM will be built.
* `%plv`: A simple Perl version prefix, such as "520" for 5.20.x or
  "518" for 5.18.x.
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

The build should gnerally use the vendor installation directories. An
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

Author
------
* [David E. Wheeler](mailto:david.wheeler@iovation.com)
