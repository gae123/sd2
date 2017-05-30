#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import subprocess
import copy
import os
import jinja2
import json
import yaml
import string
import sys
import jsonschema

__all__=('config_dct')

g_root_dir = os.getenv('SD2_CONFIG_DIR', os.path.join(os.getenv('HOME'), '.sd2'))

def ensure_base(hosts):
    hosts_by_base = {}
    for ii, host in enumerate(hosts):
        if host.get('base') is None:
            sys.stderr.write(
                "ERROR: base address for {} was not found.\n".format(
                    host['name']))
            sys.exit(1)
        base = host.get('base')
        if hosts_by_base.get(base) is not None:
            sys.stderr.write(
                "ERROR: {} and {} have the same base {}.\n".format(
                    host['name'], hosts_by_base[base][0], base))
            sys.exit(1)
        hosts_by_base[base] = [host['name']]


def process_expansions(dct):
    def expand(val, dct):
        if isinstance(val, (long,int,bool)):
            return val
        if isinstance(val, basestring):
            dct2 = copy.deepcopy(dct)
            for env_key, env_val in os.environ.iteritems():
                dct2[env_key] = env_val
            return  string.Template(val).safe_substitute(dct2)
        if isinstance(val, list):
            return [expand(x, dct) for x in val]
        if isinstance(val, dict):
            return {k: expand(v,dct) for k,v in val.iteritems()}
        return val

    for key,val in dct.iteritems():
        nval = expand(val, dct)
        dct[key] = nval


def _dfs(lst):
    stack = []
    visited = []
    for node in lst:
        if node in visited:
            continue
        stack.append(node)
        extends = node.get('extends', [])
        if not isinstance(extends, (list, tuple)):
            extends = [extends]
        for name in extends:
            node2 = [x for x in lst if x['name'] == name][0]
            if not node2 in stack and not node2 in visited:
                stack.append(node2)
        for node in reversed(stack):
            visited.append(node)
        stack = []
    return visited


def process_inheritance(config_dct, keys):
    def get_processed_dct(host, hostsdict):
        rr = {}
        extends = host.get('extends', [])
        if isinstance(extends, basestring):
            extends = [extends]
        for extend in extends + [host['name']]:
            extend_host = hostsdict[extend]
            for key in extend_host.keys():
                if key in rr.keys() and isinstance(rr[key], list):
                    ehlst = (extend_host[key]
                        if isinstance(extend_host[key], (list,tuple))
                        else [extend_host[key]])
                    for val in ehlst:
                        if not val in rr[key]:
                            rr[key].append(val)
                else:
                    rr[key] = copy.deepcopy(extend_host[key])
        return rr

    for tlkey in keys:
        hostsdict = {x['name']: x for x in config_dct.get(tlkey, [])}
        dfsnodes = _dfs(config_dct.get(tlkey, []))
        #print [x['name'] for x in dfsnodes]
        rr = []
        for dct in dfsnodes:
            isabstract = dct.get('abstract')
            disabled = dct.get('disabled')
            dct = get_processed_dct(dct, hostsdict)
            for key in ['abstract', 'extends']:
                if dct.get(key) is not None:
                    del dct[key]
            if not isabstract:
                process_expansions(dct)
            hostsdict[dct['name']] = dct
            if not disabled and not isabstract:
                rr.append(dct)

        config_dct[tlkey] = rr


def get_max_timestamp():
    rr = 0
    for name in os.listdir(g_root_dir):
        path = os.path.join(g_root_dir, name)
        rr = max(rr, os.path.getmtime(path))
    return rr


def has_timestamp_changed(config_dct):
    current_timestamp = get_max_timestamp()
    return current_timestamp > config_dct['read_timestamp']


def validate(config):
    schema_path = os.path.join(os.path.dirname(__file__), 'config_schema.json')
    with open(schema_path, 'r') as ff:
        schemajson = ff.read()
    schema = json.loads(schemajson)
    validator = jsonschema.Draft4Validator(schema)
    jsonschema.validate(config, schema)
    if not validator.is_valid(config):
        sys.stderr.write("Error: configuration file is not valid\n")
        for error in validator.iter_errors(config):
            sys.stderr.write(error.message + '\n')
            sys.exit(1)
    
    

def read_config():
    global g_root_dir, initial_timestamp

    if not os.path.exists(g_root_dir):
        sys.stderr.write('ERROR: Configuration directory {} does not exist.\n'.format(
            g_root_dir))
        sys.exit(1)

    configpy_path = os.path.join(g_root_dir, 'config')
    if os.path.exists(configpy_path):
        json_text = subprocess.check_output(configpy_path)
        ctx = json.loads(json_text)
    else:
        ctx = os.environ

    if os.path.exists(os.path.join(g_root_dir, 'config.yaml')):
        with open(os.path.join(g_root_dir, 'config.yaml'), 'r') as fd:
            first_line = fd.readline()
        first_line = first_line.strip()
        if first_line == '#!jinja2':
            template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(g_root_dir))
            templ = template_env.get_template('config.yaml')
            output = templ.render(ctx) # pylint: disable-msg=E1101
        else:
            with open(os.path.join(g_root_dir, 'config.yaml')) as fd:
                output = fd.read()
    else:
        output = ''
    try:
        config_dct = yaml.load(output)
    except yaml.parser.ParserError as ex:
        sys.stderr.write('{}\n'.format(ex))
        sys.exit(1)
    process_inheritance(config_dct, ['hosts', 'workspaces'])
    process_expansions(config_dct)
    validate(config_dct)
    ensure_base(config_dct['hosts'])
    #print json.dumps(config_dct, indent=2)
    config_dct['read_timestamp'] = get_max_timestamp()
    return config_dct


