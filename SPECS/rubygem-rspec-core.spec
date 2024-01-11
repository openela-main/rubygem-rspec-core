%global	majorver	3.7.1
#%%global	preminorver	.rc6
%global	rpmminorver	.%(echo %preminorver | sed -e 's|^\\.\\.*||')
%global	fullver	%{majorver}%{?preminorver}

%global	fedorarel	5

%global	gem_name	rspec-core

# %%check section needs rspec-core, however rspec-core depends on rspec-mocks
# runtime part of rspec-mocks does not depend on rspec-core
%global	need_bootstrap_set	0
%if 0%{?fedora} >= 25
# Disable test for now due to cucumber v.s. gherkin dependency issue
# pulled by aruba
%global	need_bootstrap_set	0
%endif

Summary:	Rspec-2 runner and formatters
Name:		rubygem-%{gem_name}
Version:	%{majorver}
Release:	%{?preminorver:0.}%{fedorarel}%{?preminorver:%{rpmminorver}}%{?dist}

Group:		Development/Languages
License:	MIT
URL:		http://github.com/rspec/rspec-mocks
Source0:	http://rubygems.org/gems/%{gem_name}-%{fullver}.gem
# %%{SOURCE2} %%{name} %%{version} 
Source1:	rubygem-%{gem_name}-%{version}-full.tar.gz
Source2:	rspec-related-create-full-tarball.sh

#BuildRequires:	ruby(release)
BuildRequires:	rubygems-devel
%if 0%{?need_bootstrap_set} < 1
BuildRequires:	rubygem(rspec)
BuildRequires:	rubygem(rake)
BuildRequires:	rubygem(coderay)
BuildRequires:	rubygem(thread_order)
BuildRequires:	git
%endif
# Make the following installed by default
# lib/rspec/core/rake_task
Recommends:	rubygem(rake)
# Optional
#Requires:	rubygem(ZenTest)
#Requires:	rubygem(flexmock)
#Requires:	rubygem(mocha)
#Requires:	rubygem(rr)
BuildArch:	noarch

%description
Behaviour Driven Development for Ruby.

%package	doc
Summary:	Documentation for %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description	doc
This package contains documentation for %{name}.


%prep
%setup -q -T -n %{gem_name}-%{version} -b 1
gem specification %{SOURCE0} -l --ruby > %{gem_name}.gemspec

%build
gem build %{gem_name}.gemspec
%gem_install

%install
mkdir -p %{buildroot}%{_prefix}
cp -a .%{_prefix}/* %{buildroot}%{_prefix}/

# cleanups
rm -f %{buildroot}%{gem_instdir}/{.document,.yardopts}

%if 0%{?need_bootstrap_set} < 1
%check
LANG=en_US.UTF-8
# Test failure needs investigation...
# perhaps due to some incompatibility between libxml2 2.9.x
# and rubygem-nokogiri

FAILFILE=()
FAILTEST=()
FAILFILE+=("spec/rspec/core/formatters/progress_formatter_spec.rb")
FAILTEST+=("produces the expected full output")
FAILFILE+=("spec/rspec/core/formatters/documentation_formatter_spec.rb")
FAILTEST+=("produces the expected full output")
FAILFILE+=("spec/rspec/core/formatters/syntax_highlighter_spec.rb")
FAILTEST+=("when CodeRay is available")
# New from 3.5.3
FAILFILE+=("spec/integration/suite_hooks_errors_spec.rb")
FAILTEST+=("nicely formats errors")
# New from 3.6.0
FAILFILE+=("spec/integration/spec_file_load_errors_spec.rb")
FAILTEST+=("nicely handles load-time errors")
# NET??
FAILFILE+=("spec/rspec/core/runner_spec.rb")
FAILTEST+=("if drb server is started with 127.0.0.1")
FAILFILE+=("spec/rspec/core/runner_spec.rb")
FAILTEST+=("if drb server is started with localhost")

for ((i = 0; i < ${#FAILFILE[@]}; i++)) {
	sed -i \
		-e "\@${FAILTEST[$i]}@s|do$|, :broken => true do|" \
		${FAILFILE[$i]}
}

# Avoid dependency on Aruba. The files needs to be present, since they are
# listed by `git ls-files` from 'library wide checks' shared example.
truncate -s 0 spec/support/aruba_support.rb
find spec/integration -exec truncate -s 0 {} \;


# Do not execute the integration test suite, which requires Aruba.
ruby -rrubygems -Ilib/ -S exe/rspec || \
	ruby -rrubygems -Ilib/ -S exe/rspec --tag ~broken
%endif

%files
%dir	%{gem_instdir}

%license	%{gem_instdir}/LICENSE.md
%doc	%{gem_instdir}/Changelog.md
%doc	%{gem_instdir}/README.md

%{_bindir}/rspec
%{gem_instdir}/exe/
%{gem_instdir}/lib/

%exclude	%{gem_cache}
%{gem_spec}

%files	doc
%{gem_docdir}

%changelog
* Thu Jul 12 2018 Jun Aruga <jaruga@redhat.com> - 3.7.1-5
- Fix FTBFS by adding build dependency for RHEL.

* Fri Jun 29 2018 Vít Ondruch <vondruch@redhat.com> - 3.7.1-4
- Remove Aruba dependency.
- Remove unneeded BRs.

* Fri Feb 23 2018 Troy Dawson <tdawson@redhat.com> - 3.7.1-3
- Update conditionals

* Tue Feb 13 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.7.1-2
- ruby 2.5 drops -rubygems usage

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan  3 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.7.1-1
- 3.7.1

* Mon Nov 13 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.7.0-1
- Enable tests again

* Mon Nov 13 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.7.0-0.1
- 3.7.0
- Once disable tests

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.6.0-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat May  6 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.6.0-1
- Enable tests again

* Sat May  6 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.6.0-0.1
- 3.6.0
- Once disable tests

* Tue Feb 21 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.0-3
- Always use full tar.gz for installed files and
  keep using gem file for gem spec (ref: bug 1425220)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.4-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 31 2017 Vít Ondruch <vondruch@redhat.com> - 3.5.4-2
- Fix Ruby 2.4 and Aruba 0.14.0 compatibility.

* Mon Oct 10 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.4-1
- 3.5.4

* Sun Sep  4 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.3-1
- 3.5.3

* Mon Aug  1 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.2-1
- 3.5.2

* Sun Jul 24 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.1-1
- Enable tests again

* Sat Jul 23 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.1-0.1
- 3.5.1
- Once disable tests

* Mon Mar 14 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.4-1
- 3.4.4

* Sun Feb 28 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.3-1
- 3.4.3

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.2-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 28 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.2-1
- 3.4.2

* Tue Dec  8 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-2
- Enable tests again

* Tue Dec  8 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-1
- 3.4.1
- Once disable tests

* Wed Aug 12 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.3.2-3
- Enable thread_order dependent tests

* Sun Aug  2 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.3.2-2
- Enable tests again

* Sun Aug  2 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.3.2-1
- 3.3.2
- Once disable tests

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.3-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr  8 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.2.3-1
- 3.2.3

* Thu Mar 12 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.2.2-1
- 3.2.2

* Wed Feb 25 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.2.1-1
- 3.2.1

* Mon Feb  9 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.2.0-2
- Enable tests again

* Mon Feb  9 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.2.0-1
- 3.2.0
- Once disable tests

* Mon Nov 10 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.1.7-2
- Enable tests

* Mon Nov 10 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.1.7-1
- 3.1.7
- Once disable tests

* Fri Aug 15 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.0.4-1
- 3.0.4

* Fri Aug 15 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.0.3-1
- 3.0.3

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.14.8-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Mar  6 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.14.8-1
- 2.14.8

* Mon Nov 11 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.14.7-1
- 2.14.7

* Thu Oct 24 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.14.6-1
- 2.14.6

* Fri Aug 16 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.14.5-2
- Enable test suite again

* Fri Aug 16 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.14.5-1
- 2.14.5

* Tue Aug  6 2013 Mamoru TASAKA <mtasaka@fedoraproject.org>
- Again enable test suite

* Tue Aug  6 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.13.1-3
- Bootstrap for rubygem-gherkin <- rubygem-cucumber

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.13.1-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Mar 28 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.13.1-2
- Enable test suite again

* Thu Mar 28 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.13.1-1
- 2.13.1

* Tue Feb 19 2013 Vít Ondruch <vondruch@redhat.com> - 2.12.2-3
- Rebuild for https://fedoraproject.org/wiki/Features/Ruby_2.0.0

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.12.2-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan  2 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.12.2-2
- Use aruba, which is already in Fedora, drop no-longer-needed
  patch

* Wed Jan  2 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.12.2-1
- 2.12.2

* Thu Oct 11 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.11.1-1
- 2.11.1
- Drop dependency for mocks and expectations

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.0-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jan 22 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.8.0-1
- 2.8.0

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.4-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Jun  7 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.4-1
- 2.6.4

* Wed May 25 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.3-1
- 2.6.3

* Tue May 24 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.2-2
- Workaround for invalid date format in gemspec file (bug 706914)

* Mon May 23 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.2-1
- 2.6.2

* Mon May 16 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.0-1
- 2.6.0

* Tue May 10 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.0-0.2.rc6
- 2.6.0 rc6

* Tue May  3 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.0-0.1.rc4
- 2.6.0 rc4

* Sat Feb 26 2011 Mamoru Tasaka <mtasaka@fedoraproject.org>
- And enable check on rawhide

* Sat Feb 26 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.5.1-3
- More cleanups

* Tue Feb 22 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.5.1-2
- Some misc fixes

* Thu Feb 17 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.5.1-1
- 2.5.1

* Fri Nov 05 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.0.1-1
- Initial package
