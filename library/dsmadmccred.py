#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import datetime
import glob
import os
import shlex

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.common.collections import is_iterable

def main():

    module = AnsibleModule(
        argument_spec=dict(
            command=dict(),
            serveraddress=dict(),
            se=dict(),
            dataonly=dict(type='bool', default=False),
            commadelimited=dict(type='bool'),
            comma=dict(type='bool'),
            tabdelimited=dict(type='bool'),
            tab=dict(type='bool'),
            credentialsfile=dict(type='str', no_log=True),
            cred=dict(type='str', no_log=True),
            displaymode=dict(),
            displ=dict(),
            dateformat=dict(type='int'),
            date=dict(type='int'),
            dsmdir=dict(type='path'),
            sim_mode=dict(type='bool', default=False),
            sim_out=dict(type='str'),
            sim_rc=dict(type='int')
        ),
        supports_check_mode=True
    )

    command = module.params['command']
    serveraddress = module.params['serveraddress']
    se = module.params['se']
    dataonly = module.params['dataonly']
    commadelimited = module.params['commadelimited']
    comma = module.params['comma']
    tabdelimited = module.params['tabdelimited']
    tab = module.params['tab']
    credentialsfile = module.params['credentialsfile']
    cred = module.params['cred']
    displaymode = module.params['displaymode']
    displ = module.params['displ']
    dsmdir = module.params['dsmdir']
    dateformat = module.params['dateformat']
    date = module.params['date']
    sim_mode = module.params['sim_mode']
    sim_out = module.params['sim_out']
    sim_rc = module.params['sim_rc']

    if not command or command.strip() == '':
        module.fail_json(rc=256, msg="no command given")

    if (not serveraddress or serveraddress.strip() == '') and (not se or se.strip() == ''):
        module.fail_json(rc=256, msg="no serveraddress given")
    elif serveraddress and se:
        module.fail_json(rc=256, msg="only serveraddress or se can be given, not both")
    else:
        serveraddress = serveraddress or se

    if (not credentialsfile or credentialsfile.strip() == '') and (not cred or cred.strip() == ''):
        module.fail_json(rc=256, msg="no credentialsfile given")
    elif credentialsfile and cred:
        module.fail_json(rc=256, msg="only credentialsfile or cred can be given, not both")
    else:
        credentialsfile = credentialsfile or cred

    if commadelimited and comma:
        module.fail_json(rc=256, msg="only commadelimited or comma can be given, not both")
    elif commadelimited or comma:
        commadelimited = commadelimited or comma

    if tabdelimited and tab:
        module.fail_json(rc=256, msg="only tabdelimited or tab can be given, not both")
    elif tabdelimited or tab:
        tabdelimited = tabdelimited or tab

    if displaymode and displ:
        module.fail_json(rc=256, msg="only displaymode or displ can be given, not both")
    elif displaymode or displ:
        displaymode = displaymode or displ

    if dateformat and date:
        module.fail_json(rc=256, msg="only dateformat or date can be given, not both")
    elif dateformat or date:
        dateformat = dateformat or date


    # All args must be strings
    if is_iterable(command, include_strings=False):
        command = [to_native(arg, errors='surrogate_or_strict', nonstring='simplerepr') for arg in command]

    compiled_command = ""

    if dsmdir:
        if dsmdir.endswith("/"):
            compiled_command = dsmdir + "dsmadmc "
        else:
            compiled_command = dsmdir + "/" + "dsmadmc "
    else:
        compiled_command = "dsmadmc "
    if (dataonly and (str(dataonly).lower() == "yes" or str(dataonly).lower() == "true")):
        compiled_command += "-DATAONLY=YES "
    compiled_command += "-SE=" + serveraddress + " "
    compiled_command += "-CRED=" + credentialsfile + " "
    if commadelimited:
        compiled_command += "-COMMA "
    if tabdelimited:
        compiled_command += "-TAB "
    if displaymode:
        compiled_command += "-DISPL=" + displaymode + " "
    if dateformat:
        compiled_command += "-DATE=" + str(dateformat) + " "
    compiled_command += "\"" + command +"\""



    startd = datetime.datetime.now()

    if not module.check_mode and not sim_mode:
        rc, out, err = module.run_command(compiled_command, encoding=None)
    elif (module.check_mode and sim_out) or sim_mode:
        if sim_out:
            out = sim_out
        else:
            out = ""
        if sim_rc:
            rc = sim_rc
        else:
            rc = 0
        err = ""
    else:
        module.exit_json(msg="skipped, running in check mode", skipped=True)

    endd = datetime.datetime.now()
    delta = endd - startd

    result = dict(
        cmd=compiled_command,
        stdout=out,
        stderr=err,
        rc=rc,
        sim_rc=sim_rc,
        sim_out=sim_out,
        start=str(startd),
        end=str(endd),
        delta=str(delta),
        changed=True,
    )

    if rc != 0:
        module.fail_json(msg='non-zero return code', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
