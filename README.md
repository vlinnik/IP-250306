# Проект АСУ БСУ IP-250306 (ДЛЯ РАДИСА)

Проект автоматизации линии приготовления бетона 

- Логика управления написана для контроллера KRAX PLC-932
- Визуализация написана на python+PyQt5, использует библиотеку concrete6 (C++, Qt5) в виде бинарника

# Запуск

## Зависимости

AnyQt, PyQt5, pyplc, pysca, pygui, concreteui. Также для запуска необходима скомпилированная библиотека libconcrete6, которая должна быть в
каталоге plugins/SCADA/modules используемой Qt5 

# Установка

Если есть сборка pyinstaller то ее необходимо 

- скопировать в /usr/local/ и выполнить 
- скопировать .desktop в /usr/share/applications/ и выполнить

```
xdg-desktop-menu install --novendor --mode user /usr/share/applications/ip-250306.desktop
```

Если запускаем из исходников, то

```
python3 <SOURCE_DIR_LOCATION>/__main__.py -w <SOURCE_DIR_LOCATION>
```

# Сборка pyinstaller

## Создание spec файла

```
$ pyi-makespec  --windowed --icon=resources/power.png --name=etalon-241218 --exclude PyQt6 --exclude PySide2 __main__.py
        --hidden-import=qwt
        --hidden-import=AnyQt.QtSql
        --hidden-import=SCADA_qrc
        --hidden-import=pygui.animation
        --hidden-import=pygui.runtimetrend
        --hidden-import=concreteui.dosatorpanel
        --hidden-import=concreteui.doserpanel
        --hidden-import=concreteui.elevatorpanel
        --hidden-import=concreteui.mixerpanel
```
### Дополнительно в spec

АСУ БСУ зависит от необходимых файлов и бинарников, которые надо добавить вручную

```
import os
from AnyQt.QtCore import QLibraryInfo

datas = [ ('default.scada','.'),('ui','./ui'),('resources','./resources'),('SCADA.rcc','.'),('concrete6.dat','.') ]
binaries = [
    (os.path.join(QLibraryInfo.location(QLibraryInfo.LibraryLocation.PluginsPath), 'SCADA/modules', 'libconcrete6.so'), 'PyQt5/Qt5/plugins/SCADA/modules'),
    (os.path.join(QLibraryInfo.location(QLibraryInfo.LibraryLocation.PluginsPath), 'sqldrivers', 'libqsqlmysql.so'), 'PyQt5/Qt5/plugins/sqldrivers'),
    (os.path.join(QLibraryInfo.location(QLibraryInfo.LibraryLocation.LibraryExecutablesPath), 'QtWebEngineProcess'), 'PyQt5/Qt5/libexec'),
]
```

в секции 

```
a = Analysis(...)
```

изменить параметры binaries и datas

# Кастомные Widget на python

Home.ui использует Widgets, которые сделаны на python-е. Чтобы стали доступны в панели нужно

Из каталога проекта (где файлы *plugin.py)

```
PYQTDESIGNERPATH=. designer
```

в designer должен быть установлен libpyqt5/libpyqt5 