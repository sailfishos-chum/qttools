%global qt_version 5.15.8

# Disable automatic .la file removal
%global __brp_remove_la_files %nil

Summary: Qt5 - QtTool components
Name: opt-qt5-qttools
Version: 5.15.8
Release: 1%{?dist}

License: LGPLv3 or LGPLv2
Url:     http://www.qt.io
Source0: %{name}-%{version}.tar.bz2

BuildRequires: make
# %%check needs cmake (and don't want to mess with cmake28)
%if 0%{?fedora} || 0%{?rhel} > 6
BuildRequires: cmake
%endif
BuildRequires: opt-qt5-rpm-macros >= %{qt_version}

BuildRequires: opt-qt5-qtbase-private-devel
BuildRequires: opt-qt5-qtbase-static >= %{qt_version}
BuildRequires: opt-qt5-qtdeclarative-static >= %{qt_version}
BuildRequires: pkgconfig(Qt5Qml)
# libQt5DBus.so.5(Qt_5_PRIVATE_API)
%{?_opt_qt5:Requires: %{_opt_qt5}%{?_isa} = %{_opt_qt5_version}}

Requires: %{name}-common = %{version}-%{release}

%description
%{summary}.

%package common
Summary: Common files for %{name}
BuildArch: noarch
%description common
%{summary}.

%package devel
Summary: Development files for %{name}
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libs-designer%{?_isa} = %{version}-%{release}
Requires: %{name}-libs-designercomponents%{?_isa} = %{version}-%{release}
Requires: %{name}-libs-help%{?_isa} = %{version}-%{release}
Requires: opt-qt5-doctools = %{version}-%{release}
Requires: opt-qt5-designer = %{version}-%{release}
Requires: opt-qt5-linguist = %{version}-%{release}
Requires: opt-qt5-qtbase-devel%{?_isa}
%description devel
%{summary}.

%package static
Summary: Static library files for %{name}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
%description static
%{summary}.

%package libs-designer
Summary: Qt5 Designer runtime library
Requires: %{name}-common = %{version}-%{release}
%description libs-designer
%{summary}.

%package libs-designercomponents
Summary: Qt5 Designer Components runtime library
Requires: %{name}-common = %{version}-%{release}
%description libs-designercomponents
%{summary}.

%package libs-help
Summary: Qt5 Help runtime library
Requires: %{name}-common = %{version}-%{release}
# when split happened
Conflicts: qt5-tools < 5.4.0-0.2
%description libs-help
%{summary}.

%package -n qt5-assistant
Summary: Documentation browser for Qt5
Requires: %{name}-common = %{version}-%{release}
%description -n qt5-assistant
%{summary}.

%package -n qt5-designer
Summary: Design GUIs for Qt5 applications
Requires: %{name}-libs-designer%{?_isa} = %{version}-%{release}
Requires: %{name}-libs-designercomponents%{?_isa} = %{version}-%{release}
%description -n qt5-designer
%{summary}.

%if 0%{?webkit}
%package -n qt5-designer-plugin-webkit
Summary: Qt5 designer plugin for WebKit
BuildRequires: pkgconfig(Qt5WebKitWidgets)
Requires: %{name}-libs-designer%{?_isa} = %{version}-%{release}
%description -n qt5-designer-plugin-webkit
%{summary}.
%endif

%package -n qt5-linguist
Summary: Qt5 Linguist Tools
Requires: %{name}-common = %{version}-%{release}
%description -n qt5-linguist
Tools to add translations to Qt5 applications.

%package -n qt5-qdbusviewer
Summary: D-Bus debugger and viewer
Requires: %{name}-common = %{version}-%{release}
%{?_opt_qt5:Requires: %{_opt_qt5}%{?_isa} >= %{_opt_qt5_version}}
%description -n qt5-qdbusviewer
QDbusviewer can be used to inspect D-Bus objects of running programs
and invoke methods on those objects.

%package -n qt5-doctools
Summary: Qt5 doc tools package
Provides: qt5-qdoc = %{version}
Obsoletes: opt-qt5-qdoc < 5.8.0
Provides: qt5-qhelpgenerator = %{version}
Obsoletes: opt-qt5-qhelpgenerator < 5.8.0
Provides: qt5-qtattributionsscanner = %{version}
Obsoletes: opt-qt5-qtattributionsscanner < 5.8.0
Requires: opt-qt5-qtattributionsscanner = %{version}

%description -n qt5-doctools
%{summary}.

%package examples
Summary: Programming examples for %{name}
Requires: %{name}-common = %{version}-%{release}
%description examples
%{summary}.


%prep
%autosetup -n %{name}-%{version}/upstream -p1


%build
export QTDIR=%{_opt_qt5_prefix}
touch .git

%{opt_qmake_qt5} \
  %{?no_examples}

%make_build


%install
make install INSTALL_ROOT=%{buildroot}

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_opt_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd

## Qt5Designer.pc references non-existent Qt5UiPlugin.pc, remove the reference for now
sed -i -e 's| Qt5UiPlugin||g' %{buildroot}%{_opt_qt5_libdir}/pkgconfig/Qt5Designer.pc


%files
%{_opt_qt5_bindir}/qtpaths
%{_opt_qt5_bindir}/qdbus

%files common
%license LICENSE.LGPL*

%post libs-designer -p /sbin/ldconfig
%postun libs-designer -p /sbin/ldconfig

%files  libs-designer
%{_opt_qt5_libdir}/libQt5Designer.so.5*
%dir %{_opt_qt5_libdir}/cmake/Qt5Designer/
%{_opt_qt5_plugindir}/designer

%post libs-designercomponents -p /sbin/ldconfig
%postun libs-designercomponents -p /sbin/ldconfig

%files  libs-designercomponents
%{_opt_qt5_libdir}/libQt5DesignerComponents.so.5*

%post libs-help -p /sbin/ldconfig
%postun libs-help -p /sbin/ldconfig

%files  libs-help
%{_opt_qt5_libdir}/libQt5Help.so.5*

%files -n qt5-assistant
%{_opt_qt5_bindir}/assistant*
#{_datadir}/applications/*assistant.desktop
#{_datadir}/icons/hicolor/*/apps/assistant*.*

%files -n qt5-doctools
#{_opt_qt5_bindir}/qdoc*
%{_opt_qt5_bindir}/qdistancefieldgenerator*
%{_opt_qt5_bindir}/qhelpgenerator*
%{_opt_qt5_bindir}/qtattributionsscanner*

%files -n qt5-designer
%{_opt_qt5_bindir}/designer*
#{_datadir}/applications/*designer.desktop
#{_datadir}/icons/hicolor/*/apps/designer*.*
%{_opt_qt5_libdir}/cmake/Qt5DesignerComponents/Qt5DesignerComponentsConfig*.cmake

%if 0%{?webkit}
%files -n qt5-designer-plugin-webkit
%{_opt_qt5_plugindir}/designer/libqwebview.so
%{_opt_qt5_libdir}/cmake/Qt5Designer/Qt5Designer_QWebViewPlugin.cmake
%endif

%files -n qt5-linguist
%{_opt_qt5_bindir}/linguist*
# phrasebooks used by linguist
%{_opt_qt5_datadir}/phrasebooks/
#{_datadir}/applications/*linguist.desktop
#{_datadir}/icons/hicolor/*/apps/linguist*.*
# linguist friends
%{_opt_qt5_bindir}/lconvert*
%{_opt_qt5_bindir}/lrelease*
%{_opt_qt5_bindir}/lupdate*
%{_opt_qt5_bindir}/lprodump*
# cmake config
%dir %{_opt_qt5_libdir}/cmake/Qt5LinguistTools/
%{_opt_qt5_libdir}/cmake/Qt5LinguistTools/Qt5LinguistToolsConfig*.cmake
%{_opt_qt5_libdir}/cmake/Qt5LinguistTools/Qt5LinguistToolsMacros.cmake

%files -n qt5-qdbusviewer
%{_opt_qt5_bindir}/qdbusviewer*
#{_datadir}/applications/*qdbusviewer.desktop
#{_datadir}/icons/hicolor/*/apps/qdbusviewer*.*

%files devel
%{_opt_qt5_bindir}/pixeltool*
%{_opt_qt5_bindir}/qcollectiongenerator*
#{_bindir}/qhelpconverter*
%{_opt_qt5_bindir}/qtdiag*
%{_opt_qt5_bindir}/qtplugininfo*
%{_opt_qt5_headerdir}/QtDesigner/
%{_opt_qt5_headerdir}/QtDesignerComponents/
%{_opt_qt5_headerdir}/QtHelp/
%{_opt_qt5_headerdir}/QtUiPlugin
%{_opt_qt5_libdir}/libQt5Designer*.prl
%{_opt_qt5_libdir}/libQt5Designer*.so
%{_opt_qt5_libdir}/libQt5Help.prl
%{_opt_qt5_libdir}/libQt5Help.so
%{_opt_qt5_libdir}/Qt5UiPlugin.la
%{_opt_qt5_libdir}/libQt5UiPlugin.prl
%{_opt_qt5_libdir}/cmake/Qt5Designer/Qt5DesignerConfig*.cmake
%dir %{_opt_qt5_libdir}/cmake/Qt5Help/
%{_opt_qt5_libdir}/cmake/Qt5Help/Qt5HelpConfig*.cmake
%{_opt_qt5_libdir}/cmake/Qt5UiPlugin/
%{_opt_qt5_libdir}/pkgconfig/Qt5Designer.pc
%{_opt_qt5_libdir}/pkgconfig/Qt5Help.pc
%{_opt_qt5_libdir}/pkgconfig/Qt5UiPlugin.pc
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_designer.pri
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_designer_private.pri
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_designercomponents_private.pri
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_help.pri
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_help_private.pri
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_uiplugin.pri
# putting these here for now, new stuff in 5.14, review for accuracy -- rdieter
%{_opt_qt5_libdir}/cmake

%files static
%{_opt_qt5_headerdir}/QtUiTools/
%{_opt_qt5_libdir}/libQt5UiTools.*a
%{_opt_qt5_libdir}/libQt5UiTools.prl
%{_opt_qt5_libdir}/cmake/Qt5UiTools/
%{_opt_qt5_libdir}/pkgconfig/Qt5UiTools.pc
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_uitools.pri
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_uitools_private.pri
