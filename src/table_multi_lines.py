"""
copyright: 2019- ijgnd
           2020- Lovac42 (toolbar.py)

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


from anki.hooks import wrap

from aqt.gui_hooks import (
    browser_menus_did_init,
    browser_will_show,
)
from aqt import mw
from aqt.browser import (
    Browser,
    DataModel,
    StatusDelegate,
)
from aqt.qt import (
    QKeySequence
)


from .toolbar import getMenu


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


#limit the lengh of what is shown in a table cell. Necessary
#if a field is really long.
def columnDataTruncate(self, index, _old):
    out = _old(self, index)
    if isinstance(out, str):
        out = out[:gc("max_string_length", 100)]
    return out
DataModel.columnData = wrap(DataModel.columnData, columnDataTruncate, "around")


height_was_adjusted_once = False
old_row_height = None
def mypaint(self, painter, option, index):
    global height_was_adjusted_once
    global old_row_height
    if not height_was_adjusted_once:
        old_row_height = self.browser.form.tableView.rowHeight(0)
    if table_multilines:
        self.browser.form.tableView.resizeRowToContents(index.row())
        height_was_adjusted_once = True
    else:
        if height_was_adjusted_once and old_row_height:
            self.browser.form.tableView.setRowHeight(index.row(), old_row_height)
StatusDelegate.paint = wrap(StatusDelegate.paint, mypaint, "before")


def additionalInit(self):
    global table_multilines
    table_multilines = False
    if gc("on by default"):
        table_multilines = True
    # revert https://github.com/ankitects/anki/commit/9ee82d55b11168b24f8c6b78efed735e2523bc66
    # from 2020-03-20
    self.form.tableView.setWordWrap(True)
browser_will_show.append(additionalInit)


def toggle_tablelines(self):
    # self is browser
    global table_multilines
    if table_multilines:
        self.form.tableView.setWordWrap(False)
    else:
        self.form.tableView.setWordWrap(True)
    self.onSearchActivated()
    table_multilines ^= True



def setupBrowserMenu(self):
    # self is browser
    m = getMenu(self, "&View")
    l = "enable wordwrap in table (multi-line)"
    toggle_action = m.addAction(l)
    toggle_action.setCheckable(True)
    toggle_action.setChecked(gc("enable by default"))
    toggle_action.toggled.connect(lambda _, b=self: toggle_tablelines(b))
    cut = gc("shortcut")
    if cut:
        toggle_action.setShortcut(QKeySequence(cut))
browser_menus_did_init.append(setupBrowserMenu)
