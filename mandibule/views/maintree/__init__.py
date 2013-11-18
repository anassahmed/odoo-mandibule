# -*- coding: UTF-8 -*-
##############################################################################
#
#    Mandibule, an explorer for OpenERP servers
#    Copyright (C) 2013 Sébastien Alix
#                       Frédéric Fidon
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

__all__ = ['GroupItem', 'ServerItem']

from PySide import QtGui, QtCore

from mandibule.views.maintree.group import GroupItem
from mandibule.views.maintree.server import ServerItem
from mandibule.utils.i18n import _


class MainTree(QtGui.QTreeWidget):
    """Main tree to manage group, servers and functions."""
    def __init__(self, app):
        QtGui.QTreeWidget.__init__(self)
        self.app = app
        self.app.group_ctl.created.connect(self.add_group)
        self.app.group_ctl.deleted.connect(self.remove_group)
        self.setHeaderHidden(True)
        for id_ in self.app.group_ctl.read_all():
            self.add_group(id_)

    def add_group(self, id_):
        """Add the group identified by `id_`."""
        group = GroupItem(self.app, id_)
        self.addTopLevelItem(group)
        group.setExpanded(True)

    def remove_group(self, id_):
        """Remove the group identified by `id_`."""
        for index in range(self.topLevelItemCount()):
            group = self.topLevelItem(index)
            if group.id == id_:
                group = self.takeTopLevelItem(index)
                group.deleteLater()

    def contextMenuEvent(self, event):
        """Overridden to show a contextual menu according to the
        selected item.
        """
        if self.currentItem():
            menu = self.currentItem().get_menu()
            menu.popup(event.globalPos())
        else:
            menu = QtGui.QMenu(self)
            icon_add = QtGui.QIcon.fromTheme('list-add')
            menu.addAction(
                icon_add,
                _("New group"),
                self.app.group_ctl.display_form)
            menu.popup(event.globalPos())

    def mousePressEvent(self, event):
        """Overloaded to unset the current selection when clicking
        in the blanc area.
        """
        if self.itemAt(event.pos()) is None:
            self.setCurrentItem(None)
        QtGui.QTreeWidget.mousePressEvent(self, event)

    def keyPressEvent(self, event):
        """Overloaded to unset the current selection when pressing the
        Escape key.
        """
        if (event.key() == QtCore.Qt.Key_Escape and
            event.modifiers() == QtCore.Qt.NoModifier):
            self.setCurrentItem(None)
        else:
            QtGui.QTreeWidget.keyPressEvent(self, event)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
