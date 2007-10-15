Summary:	MirBSD Korn Shell
Name:		mksh
Version:	31d
Release:	0.1
License:	BSD
Group:		Applications/Shells
Source0:	http://www.mirbsd.org/MirOS/dist/mir/mksh/%{name}-R%{version}.cpio.gz
# Source0-md5:	a7c77428bd2b887c1583095a00c84aac
Source1:	http://www.mirbsd.org/MirOS/dist/hosted/other/arc4random.c
URL:		http://mirbsd.de/mksh
Requires(pre):	FHS
Requires:	setup >= 2.4.6-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_bindir			/bin

%description
mksh is the MirBSD enhanced version of the Public Domain Korn shell
(pdksh), a bourne-compatible shell which is largely si- milar to the
original AT&T Korn shell. It includes bug fixes and feature
improvements in order to produce a modern, robust shell good for
interactive and especially script use. It has UTF-8 support in the
emacs command line editing mode; corres- ponds to OpenBSD 4.2-current
ksh sans GNU bash-like $PS1; the build environment requirements are
autoconfigured; throughout code simplification/bugfix/enhancement has
been done, and the shell has extended compatibility to other modern
shells.


%prep
%setup -q -T
gzip -dc %{SOURCE0} | cpio -mid
mv mksh/* ./ ; rm -fr mksh
cp "%{SOURCE1}" ./

%build
CC="%__cc" CFLAGS="%{optflags}" sh ./Build.sh -Q -r -j
./test.sh -v

%install
rm -rf $RPM_BUILD_ROOT

install -D mksh   $RPM_BUILD_ROOT%{_bindir}/mksh
install -D mksh.1 $RPM_BUILD_ROOT%{_mandir}/man1/mksh.1

%clean
rm -rf $RPM_BUILD_ROOT

%post -p <lua>
t = {}
f = io.open("/etc/shells", "r")
if f then
   for l in f:lines() do t[l]=l; end
   f:close()
end
for _, s in ipairs({"/bin/mksh", "/bin/sh"}) do
   if not t[s] then
      f = io.open("/etc/shells", "a"); f:write(s.."\n"); f:close()
   end
end

%preun -p <lua>
if arg[2] == "0" then
   f = io.open("/etc/shells", "r")
   if f then
      s=""
      for l in f:lines() do
        if not string.match(l,"^/bin/mksh$") then
           s=s..l.."\n"
        end
      end
      f:close()
      io.open("/etc/shells", "w"):write(s)
   end
end

%files
%defattr(644,root,root,755)
%doc dot.mkshrc
%attr(755,root,root) %{_bindir}/mksh
%{_mandir}/man1/*
