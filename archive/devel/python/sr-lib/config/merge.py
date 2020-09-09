#!/usr/bin/env python
# -*- coding: utf-8 -*-


def merge( default_config=None, parser_options=None, cfg_file=None):
    """
    Invocation:
    Provide a default_config (ConfigObj) object, an OptionParser opts object
    and an optional config file name. The config and option data are merged 
    as follows:

    default options < config file < command line options
    means: command line options overwrite config file options
    which beat default options. In case config file does not exist but is not
    None it is created .

    Returns a ConfigObj object.
    """

    if default_config is None or parser_config is None:
        raise ConfigError(
            "Make sure default_config or parser_config is provided to "
            "merge_configs(), cfg_file is optional"
        )

    if cfg_file is not None:
        # config file specified, load or create it
        if os.path.exists( cfg_file ):
            # ignore default options, merge config file and cli options
            cfg = ConfigFile( cfg_file, create_empty=False )
            cfg.merge(parser_config)
        else:
            # write default options to config file, merge with cli options
            cfg = ConfigFile( cfg_file, create_empty=True )
            cfg.merge(default_config)
            cfg.write()
            cfg.merge(parser_config)
    else:
        # no config file defined, just load defaults and merge with cli opts
        cfg = default_config.merge(parser_config)

    return cfg
