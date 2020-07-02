"""
copyright 2019 ijgnd

Use this at your own risk. Incomplete version.

crucial code is from /u/brunzus, https://www.reddit.com/r/Anki/comments/ayxvbw/word_wrap_for_browsertable_cells_help_needed_for/


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from anki.hooks import addHook, wrap

from aqt import mw
from aqt.browser import Browser, DataModel, StatusDelegate
from anki.hooks import wrap
from aqt.qt import *


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


#limit the lengh of what is shown in a table cell. Necessary 
#if a field is really long. 
def columnDataTruncate(self, index, _old):
    out = _old(self, index)
    if isinstance(out, str):
        out = out[:gc("max_string_length", 100)]
    return out
DataModel.columnData = wrap(DataModel.columnData, columnDataTruncate, "around")


def mypaint(self, painter, option, index):
    if table_multilines:
        self.browser.form.tableView.resizeRowToContents(index.row())
StatusDelegate.paint = wrap(StatusDelegate.paint, mypaint, "before")


def additionalInit(self, mw):
    global table_multilines
    table_multilines = False
    if gc("on by default"):
        table_multilines = True
Browser.__init__ = wrap(Browser.__init__, additionalInit)


def toggle_tablelines(browser):
    global table_multilines
    table_multilines ^= True


def onSetupMenus(self):
    try:
        m = self.menuView
    except:
        self.menuView = QMenu("&View")
        action = self.menuBar().insertMenu(
            self.mw.form.menuTools.menuAction(), self.menuView)
        m = self.menuView
    a = m.addAction('enable wordwrap in table (multi-line), close and reopen Browser to deactivate')
    a.triggered.connect(lambda _, b=self: toggle_tablelines(b))
    a.setShortcut(QKeySequence(gc("shortcut", "")))
addHook("browser.setupMenus", onSetupMenus)