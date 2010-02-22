Summary:	MirBSD Korn Shell
Summary(pl.UTF-8):	Powłoka Korna z MirBSD
Name:		mksh
Version:	36
Release:	0.1
License:	BSD
Group:		Applications/Shells
Source0:	http://www.mirbsd.org/MirOS/dist/mir/mksh/%{name}-R%{version}.cpio.gz
# Source0-md5:	9962d052a1571ba843965c6253819ac4
Source1:	http://www.mirbsd.org/MirOS/dist/hosted/other/arc4random.c
URL:		http://mirbsd.de/mksh
BuildRequires:	rpmbuild(macros) >= 1.462
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

%prep
%setup -qcT
gzip -dc %{SOURCE0} | cpio -mid
mv mksh/* .; rmdir mksh
cp -a %{SOURCE1} .

%build
CC="%{__cc}" CFLAGS="%{rpmcflags}" sh ./Build.sh -Q -r -j
./test.sh -v

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1}
install -p mksh	$RPM_BUILD_ROOT%{_bindir}/mksh
cp -a mksh.1 $RPM_BUILD_ROOT%{_mandir}/man1/mksh.1

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p <lua>
%lua_add_etc_shells %{_bindir}/mksh

%preun	-p <lua>
if arg[2] == 0 then
	%lua_remove_etc_shells  %{_bindir}/mksh
end

%files
%defattr(644,root,root,755)
%doc dot.mkshrc
%attr(755,root,root) %{_bindir}/mksh
%{_mandir}/man1/mksh.1*
