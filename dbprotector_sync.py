#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xamai.Upload import Upload
from xamai.Login import Login
from xamai.Gui import Gui

l = Login()

if l.isActive():
    app = Upload()
    app.sync()
else:
    app = Gui()
    app.login()