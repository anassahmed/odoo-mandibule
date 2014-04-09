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
"""Module controllers."""
import uuid

from PySide.QtCore import QThreadPool, Signal

import oerplib

from mandibule import db
from mandibule.utils.i18n import _
from mandibule.reg import Controller, UI
from mandibule.widgets.dialog import confirm
from mandibule.widgets.graph import GraphWorker


class DependencyController(Controller):
    """Module dependencies graph function controller."""
    __metadata__ = {
        'name': 'dependency',
        'function': True,
    }

    created = Signal(str, str, dict)
    updated = Signal(str, str, dict)
    deleted = Signal(str, str)
    executed = Signal(str, str, dict)
    execute_error = Signal(str, str)
    finished = Signal(str, str, tuple)

    def default_get(self, default=None):
        """Return default data values."""
        if default is None:
            default = {}
        data = {
            'name': '',
            'modules': 'base',
            'models': '*',
            'models_blacklist': '',
            'restrict': False,
        }
        data.update(default)
        return data

    def display_form(self, id_=None, data=None):
        """Display a form to create/edit an existing record. If `id_` is None,
        no data will be saved (live-edit on the view). Default values of the
        form can be set through the `data` dictionary.
        """
        if id_:
            UI['workbook'].edit_function('dependency', id_)
        else:
            UI['workbook'].new_function(
                'dependency', UI['tree'].current.get('server'))

    def create(self, data):
        """Create a new record from `data` and return its ID."""
        id_ = uuid.uuid4().hex
        db_data = db.read()
        data_copy = data.copy()
        sid = data_copy.pop('server_id')
        gid = Controller['server'].read(sid)['group_id']
        if 'dependencies' not in db_data[gid]['servers'][sid]:
            db_data[gid]['servers'][sid]['dependencies'] = {}
        db_data[gid]['servers'][sid]['dependencies'][id_] = data_copy
        db.write(db_data)
        self.created.emit('dependency', id_, data)
        return id_

    def read(self, id_):
        """Return data related to the record identified by `id_`."""
        db_data = db.read()
        for gdata in db_data.itervalues():
            for sid, sdata in gdata['servers'].iteritems():
                if id_ in sdata.get('dependencies', {}):
                    rdata = sdata['dependencies'][id_]
                    rdata['server_id'] = sid
                    return rdata
        return None

    def read_all(self):
        """Return all records data."""
        db_data = db.read()
        data = {}
        for gdata in db_data.itervalues():
            for sid, sdata in gdata['servers'].iteritems():
                for rid, rdata in sdata.get('dependencies', {}).iteritems():
                    data[rid] = rdata
                    data[rid]['server_id'] = sid
        return data

    def update(self, id_, data):
        """Update a record identified by `id_` with `data`."""
        data_copy = data.copy()
        data_copy.pop('server_id')
        db_data = db.read()
        for gdata in db_data.itervalues():
            for sdata in gdata['servers'].itervalues():
                if id_ in sdata.get('dependencies', {}):
                    sdata['dependencies'][id_].update(data_copy)
                    db.write(db_data)
                    self.updated.emit('dependency', id_, data)
                    return

    def delete(self, id_):
        """Delete a record identified by `id_`."""
        db_data = db.read()
        for gdata in db_data.itervalues():
            for sdata in gdata['servers'].itervalues():
                if id_ in sdata.get('dependencies', {}):
                    del sdata['dependencies'][id_]
                    db.write(db_data)
                    self.deleted.emit('dependency', id_)
                    return

    def delete_confirm(self, id_):
        """Display a confirmation dialog to the user before delete."""
        data = self.read(id_)
        response = confirm(
            UI['main_window'],
            _(u"Are you sure you want to delete the function "
              u"<strong>%s</strong>?") % (data['name']))
        if response:
            self.delete(id_)

    def execute(self, id_, data=None):
        """Generate the relation graph."""
        if not data:
            data = self.read(id_)
        self.executed.emit('dependency', id_, data)
        worker = GraphWorker(id_, lambda: self._execute(id_, data))
        worker.result_ready.connect(self._process_result)
        worker.exception_raised.connect(self._handle_exception)
        QThreadPool.globalInstance().start(worker)

    def _execute(self, id_, data):
        """Internal threaded method requesting the result."""
        oerp = oerplib.OERP.load(data['server_id'], rc_file=db.OERPLIB_FILE)
        graph = oerp.inspect.dependencies(
            [str(model) for model in data['modules'].split()],
            [str(model) for model in data['models'].split()],
            [str(model) for model in data['models_blacklist'].split()],
            data['restrict'])
        return graph

    def _process_result(self, id_, result):
        """Slot which emit the 'finished' signal to views."""
        self.finished.emit('dependency', id_, result)

    def _handle_exception(self, id_, message):
        """Slot performed if the threaded method has raised an exception."""
        self.execute_error.emit('dependency', id_)
        raise RuntimeError(message)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
