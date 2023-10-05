#
# Conditional build:
%bcond_with	lto	# enable link time optimisations (breaks tests)
%bcond_without	static	# static version of mksh
%bcond_without	tests	# rtchecks and test.sh checks

%define		vernr	%(echo %{version} | tr -d 'a-z')

Summary:	MirBSD Korn Shell
Summary(pl.UTF-8):	Powłoka Korna z MirBSD
Name:		mksh
Version:	59c
Release:	3
License:	BSD
Group:		Applications/Shells
Source0:	https://www.mirbsd.org/MirOS/dist/mir/mksh/%{name}-R%{version}.tgz
# Source0-md5:	99f8ac3c1d8a30b913d509f1969a4aaa
Source1:	%{name}-mkshrc
Source2:	get-source.sh
Patch0:		%{name}-mkshrc_support.patch
Patch1:		%{name}-circumflex.patch
Patch2:         drop-builtins.patch
URL:		https://www.mirbsd.org/mksh.htm
%if %{with tests}
BuildRequires:	ed
BuildRequires:	perl-base
%endif
%{?with_static:BuildRequires:   glibc-static}
BuildRequires:	rpmbuild(macros) >= 1.670
# is needed for /etc directory existence
Requires(pre):	FHS
Requires:	setup >= 2.4.6-2
Obsoletes:	pdksh
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_bindir			/bin

%description
mksh is the MirBSD enhanced version of the Public Domain Korn shell
(pdksh), a Bourne-compatible shell which is largely similar to the
original AT&T Korn shell. It includes bug fixes and feature
improvements in order to produce a modern, robust shell good for
interactive and especially script use. It has UTF-8 support in the
emacs command line editing mode; corresponds to OpenBSD 4.2-current
ksh sans GNU bash-like $PS1; the build environment requirements are
autoconfigured; throughout code simplification/bugfix/enhancement has
been done, and the shell has extended compatibility to other modern
shells.

%description -l pl.UTF-8
mksh to pochodząca z MirBSD rozszerzona wersja powłoki Public Domain
Korn Shell (pdksh) - kompatybilnej z powłoką Bourne'a, w większości
zbliżonej do oryginalnej powłoki Korna z AT&T. Zawiera poprawki błędów
i rozszerzenia mające na celu stworzenie współczesnej powłoki o
bogatych możliwościach do użytku interaktywnego i (zwłaszcza) w
skryptach. Ma obsługę UTF-8 w trybie edycji linii poleceń w stylu
emacsa; $PS1 odpowiada temu z ksh obecnym w OpenBSD 4.2-current;
środowisko budowania jest automatycznie konfigurowane; dzięki
wykonanym uproszczeniom kodu, poprawkom i rozszerzeniom powłoka ma
rozszerzoną kompatybilność z innymi współczesnymi powłokami.

%package static
Summary:	Statically linked the MirBSD enhanced version of pdksh
Summary(pl.UTF-8):	Skonsolidowana statycznie powłoka mksh
Group:		Applications/Shells
# requires base for /etc/mkshrc?
Requires:	%{name} = %{version}-%{release}

%description static
mksh is the MirBSD enhanced version of the Public Domain Korn shell
(pdksh), a Bourne-compatible shell which is largely similar to the
original AT&T Korn shell.

This packege contains statically linked version of mksh.

%description static -l pl.UTF-8
mksh to pochodząca z MirBSD rozszerzona wersja powłoki Public Domain
Korn Shell (pdksh) - kompatybilnej z powłoką Bourne'a, w większości
zbliżonej do oryginalnej powłoki Korna z AT&T.

W tym pakiecie jest mksh skonsolidowany statycznie.

%prep
%setup -qc
%{__mv} mksh/* .; rmdir mksh

%patch0 -p1
%patch1 -p1
%patch2 -p1

sed -i -e 's|fgrep|grep -F|g' check.t

# sed rules instead of patch (needed update for every release)
sed -i -e 's|\(#define.*MKSH_VERSION.*\)"|\1 @DISTRO@"|g' sh.h
sed -i -e 's|\(KSH R%{vernr}.*\)|\1 @DISTRO@|g' check.t

# fill distro
sed -i -e 's#@DISTRO@#PLD/Linux 3.0#g' check.t sh.h
# sanity checks
grep PLD/Linux check.t || exit 1
grep PLD/Linux sh.h || exit 1

# we'll need this later due to -DMKSH_GCC55009
cat >rtchecks <<'EOF'
typeset -i sari=0
typeset -Ui uari=0
typeset -i x=0
print -r -- $((x++)):$sari=$uari.
let --sari --uari
print -r -- $((x++)):$sari=$uari.
sari=2147483647 uari=2147483647
print -r -- $((x++)):$sari=$uari.
let ++sari ++uari
print -r -- $((x++)):$sari=$uari.
let --sari --uari
let 'sari *= 2' 'uari *= 2'
let ++sari ++uari
print -r -- $((x++)):$sari=$uari.
let ++sari ++uari
print -r -- $((x++)):$sari=$uari.
sari=-2147483648 uari=-2147483648
print -r -- $((x++)):$sari=$uari.
let --sari --uari
print -r -- $((x++)):$sari=$uari.
EOF

cat >rtchecks.expected <<'EOF'
0:0=0.
1:-1=4294967295.
2:2147483647=2147483647.
3:-2147483648=2147483648.
4:-1=4294967295.
5:0=0.
6:-2147483648=2147483648.
7:2147483647=2147483647.
EOF

%build
install -d out

CC="%{__cc}" \
CFLAGS="%{rpmcflags} -DMKSH_GCC55009" \
LDFLAGS="%{rpmldflags}" \
CPPFLAGS="%{rpmcppflags}" \
sh ./Build.sh -Q -r -j %{?with_lto:-c lto}

# skip some tests if not on terminal
if ! tty -s; then
	skip_tests="-C regress:no-ctty"
fi

%if %{with tests}
./mksh rtchecks >rtchecks.got 2>&1
if ! cmp --quiet rtchecks.got rtchecks.expected ; then
	echo "rtchecks failed"
	diff -Naurp rtchecks.expected rtchecks.got
	exit 1
fi
./test.sh -v $skip_tests
%endif
mv mksh out/mksh.dynamic

%if %{with static}
CC="%{__cc}" \
CFLAGS="%{rpmcflags} -DMKSH_GCC55009" \
LDFLAGS="%{rpmldflags} -static" \
CPPFLAGS="%{rpmcppflags}" \
sh ./Build.sh -Q -r -j %{?with_lto:-c lto}

%if %{with tests}
./test.sh -v $skip_tests
./mksh rtchecks >rtchecks.got 2>&1
if ! cmp --quiet rtchecks.got rtchecks.expected ; then
	echo "rtchecks failed"
	diff -Naurp %{SOURCE3} rtchecks.got
	exit 1
fi
%endif
mv mksh out/mksh.static
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1}
install -p out/mksh.dynamic $RPM_BUILD_ROOT%{_bindir}/mksh
%{?with_static:install -p out/mksh.static $RPM_BUILD_ROOT%{_bindir}/mksh.static}

cp -a mksh.1 $RPM_BUILD_ROOT%{_mandir}/man1/mksh.1
echo ".so mksh.1" > $RPM_BUILD_ROOT%{_mandir}/man1/sh.1

install -D %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/mkshrc
ln -sf mksh $RPM_BUILD_ROOT%{_bindir}/sh

# some pdksh scripts used that
ln -sf mksh $RPM_BUILD_ROOT%{_bindir}/ksh

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p %add_etc_shells -p /bin/sh /bin/ksh /bin/mksh
%preun  -p %remove_etc_shells -p /bin/sh /bin/ksh /bin/mksh

%post	static -p %add_etc_shells -p /bin/mksh.static
%preun	static -p %remove_etc_shells -p /bin/mksh.static

%triggerpostun -p <lua> -- pdksh
if arg[2] ~= 0 then
%lua_add_etc_shells /bin/sh /bin/ksh /bin/mksh
end

%files
%defattr(644,root,root,755)
%doc dot.mkshrc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mkshrc
%attr(755,root,root) %{_bindir}/mksh
%attr(755,root,root) %{_bindir}/ksh
%attr(755,root,root) %{_bindir}/sh
%{_mandir}/man1/mksh.1*
%{_mandir}/man1/sh.1*

%if %{with static}
%files static
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/mksh.static
%endif
