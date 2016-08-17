#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xamai.Scanda import Scanda
from xamai.Login import Login
from xamai.Gui import Gui

l = Login()

if l.isActive():
    app = Scanda()
    app.main()
else:
    app = Gui()
    app.login()