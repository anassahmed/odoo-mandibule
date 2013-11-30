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

from PySide import QtGui

from mandibule.utils.i18n import _
from mandibule.views.maintree.relation import RelationDrawer
from mandibule.views.maintree.dependency import DependencyDrawer
from mandibule.views import icons


class ServerItem(QtGui.QTreeWidgetItem):
    """A server item inside a GroupItem."""
    def __init__(self, app, id_, parent):
        QtGui.QTreeWidgetItem.__init__(self)
        parent.addChild(self)
        self.app = app
        self.app.server_ctl.updated.connect(self.update_server)
        self.id = id_
        data = self.app.server_ctl.read(id_)
        self.setText(0, data['name'])
        icon = QtGui.QIcon.fromTheme('network-server')
        self.setIcon(0, icon)
        # Add the drawers
        self.addChild(RelationDrawer(self.app, self.id, self))
        self.addChild(DependencyDrawer(self.app, self.id, self))

    def update_server(self, id_):
        """Update the server identified by `ìd_`."""
        if self.id == id_:
            data = self.app.server_ctl.read(id_)
            self.setText(0, data['name'])

    def get_menu(self):
        """Return a QMenu corresponding to the current ServerItem."""
        menu = QtGui.QMenu(self.treeWidget())
        # Add relational graph
        menu.addAction(
            icons.icon_add,
            _("Add relational graph"),
            lambda: self.app.relation_ctl.display_form(None, self.id))
        # Add module dependencies graph
        menu.addAction(
            icons.icon_add,
            _("Add dependencies graph"),
            lambda: self.app.dependency_ctl.display_form(None, self.id))
        # Remove current server
        menu.addAction(
            icons.icon_remove,
            _("Remove"),
            lambda: self.app.server_ctl.delete(self.id))
        # Properties
        menu.addSeparator()
        menu.addAction(
            icons.icon_edit,
            _("Properties"),
            lambda: self.app.server_ctl.display_form(self.id))
        return menu

    def set_icon_expanded(self, expanded=True):
        """Update the icon."""
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: