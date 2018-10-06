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
import six

__all__=('config_dct')

def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property_, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property_, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return jsonschema.validators.extend(
        validator_class, {"properties": set_defaults},
    )
DefaultValidatingDraft4Validator = extend_with_default(jsonschema.Draft4Validator)

g_root_dir = os.getenv('SD2_CONFIG_DIR', os.path.join(os.getenv('HOME'), '.sd2'))

from .sd2_config_schema import sd2_config_schema

def exit_with_error(msg):
    sys.stderr.write(msg)
    sys.exit(1)

def ensure_base(hosts):
    hosts_by_base = {}
    for ii, host in enumerate(hosts):
        #if host.get('base') is None:
        #    sys.stderr.write(
        #        ("ERROR: base address for {} was not found in {}." +
        #         "Each host needs a base address in the 1-200 range.\n").format(
        #            host['name'], g_root_dir))
        #    sys.exit(1)
        base = host.get('base')
        if base is not None and hosts_by_base.get(base) is not None:
            sys.stderr.write(
                "ERROR: {} and {} have the same base {}.\n".format(
                    host['name'], hosts_by_base[base][0], base))
            sys.exit(1)
        hosts_by_base[base] = [host['name']]


def process_expansions(dct):
    def expand(val, dct):
        if isinstance(val, six.integer_types) or isinstance(val, bool):
            return val
        if isinstance(val, six.string_types):
            dct2 = copy.deepcopy(dct)
            for env_key, env_val in six.iteritems(os.environ):
                dct2[env_key] = env_val
            return  string.Template(val).safe_substitute(dct2)
        if isinstance(val, list):
            return [expand(x, dct) for x in val]
        if isinstance(val, dict):
            return {k: expand(v,val) for k,v in six.iteritems(val)}
        return val

    for key,val in six.iteritems(dct):
        nval = expand(val, dct)
        dct[key] = nval


def process_containers(dct):
    """Look for containers: at top level and add them to the appropriate host"""
    if not dct.get('containers'):
        return

    dct_cnt = dct['containers']
    for cont in dct_cnt:
        if cont.get('name') is None:
            message = "ERROR: Each container must have a name that is a string. {}\n"
            exit_with_error(message.format(cont))
        if cont.get('hostname') is None:
            exit_with_error("ERROR: Container '{}' does not have a host.\n".format(cont['name']))

        #if cont.get('enabled') == False or cont.get('disabled') == True:
        #    continue

        cont_host = None
        for host in dct.get('hosts', []):
            if host['name'] == cont['hostname']:
                cont_host = host
                break
        if not cont_host:
            exit_with_error(
                "ERROR: Container '{}'' expects non existing host '{}'.\n". format(
                cont['name'], cont['hostname']))

        if not cont_host.get('containers'):
            cont_host['containers'] = []

        for host_cnt in cont_host['containers']:
            if host_cnt['name'] == cont['name']:
                exit_with_error(
                    "ERROR: host '{}' already has a container with name '{}'.\n". format(
                        host['name'], cont['name']))

        cont_host['containers'].append(cont)


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
            nodes = [x for x in lst if x['name'] == name]
            if len(nodes) == 0:
                sys.stderr.write(
                    "ERROR: abstract ancestor called {} not found in {}\n".format(name, node))
                sys.exit(1)
            node2 = nodes[0]
            if not node2 in stack and not node2 in visited:
                stack.append(node2)
        for node in reversed(stack):
            visited.append(node)
        stack = []
    return visited


def process_inheritance(config_dct, keys):
    def get_processed_dct(tlkey, host, hostsdict):
        rr = {}
        extends = host.get('extends', [])
        if isinstance(extends, six.string_types):
            extends = [extends]
        for extend in extends + [host['name']]:
            extend_host = hostsdict[extend]
            for key in six.viewkeys(extend_host):
                if key in six.viewkeys(rr) and isinstance(rr[key], list):
                    ehlst = (extend_host[key]
                        if isinstance(extend_host[key], (list,tuple))
                        else [extend_host[key]])
                    for val in ehlst:
                        if not val in rr[key]:
                            rr[key].append(val)
                else:
                    rr[key] = copy.deepcopy(extend_host[key])
        return rr

    for tlkey in keys:  # e.g workspaces
        hostsdict = {x['name']: x for x in config_dct.get(tlkey, [])}
        dfsnodes = _dfs(config_dct.get(tlkey, []))
        #print [x['name'] for x in dfsnodes]
        rr = []
        for dct in dfsnodes:
            isabstract = dct.get('abstract')
            #disabled = dct.get('disabled')
            dct = get_processed_dct(tlkey, dct, hostsdict)
            for key in ['abstract', 'extends']:
                if dct.get(key) is not None:
                    del dct[key]
            #if not isabstract:
            #    process_expansions(dct)
            hostsdict[dct['name']] = dct
            if not isabstract:
                rr.append(dct)

        config_dct[tlkey] = rr


def get_max_timestamp():
    rr = 0
    for name in os.listdir(g_root_dir):
        if (not name.endswith('config.yaml') and
            not name.endswith('config')):
            continue
        path = os.path.join(g_root_dir, name)
        rr = max(rr, os.path.getmtime(path))
    return rr


def has_timestamp_changed(config_dct):
    current_timestamp = get_max_timestamp()
    return current_timestamp > config_dct['read_timestamp']


def validate(config):
    #schema_path = os.path.join(os.path.dirname(__file__), 'config_schema.json')
    #with open(schema_path, 'r') as ff:
    #    schemajson = ff.read()
    schema = json.loads(sd2_config_schema)
    validator = DefaultValidatingDraft4Validator(schema)
    jsonschema.validate(config, schema)
    if not validator.is_valid(config):
        sys.stderr.write("Error: configuration file is not valid\n")
        for error in validator.iter_errors(config):
            sys.stderr.write(error.message + '\n')
            sys.exit(1)

def _merge_into(config_dct, dct):
    for key,val in six.iteritems(dct):
        if isinstance(val, list):
            if not config_dct.get(key):
                config_dct[key] = []
            config_dct[key].extend(val)
        else:
            config_dct[key] = val

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

    config_dct = {}
    for name in os.listdir(g_root_dir):
        if not name.endswith('config.yaml'):
            continue
        config_file_path = os.path.join(g_root_dir, name)
        with open(config_file_path, 'r') as fd:
            first_line = fd.readline()
        first_line = first_line.strip()
        if first_line == '#!jinja2':
            template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(g_root_dir))
            templ = template_env.get_template(name)
            output = templ.render(ctx) # pylint: disable-msg=E1101
        else:
            with open(os.path.join(g_root_dir, name)) as fd:
                output = fd.read()
        try:
            dct = yaml.load(output)
        except yaml.parser.ParserError as ex:
            sys.stderr.write('{}: {}\n'.format(config_file_path, ex))
            sys.exit(1)

        _merge_into(config_dct, dct)

    process_inheritance(config_dct, ['images', 'hosts', 'workspaces'])
    process_containers(config_dct)
    process_expansions(config_dct)
    validate(config_dct)
    ensure_base(config_dct['hosts'])
    #print json.dumps(config_dct, indent=2)
    config_dct['read_timestamp'] = get_max_timestamp()
    return config_dct


