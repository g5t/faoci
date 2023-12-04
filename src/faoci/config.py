import confuse
config = confuse.LazyConfig('faoci', __name__)
print(config.config_dir())
# Use environment variables `FAOCI_{XYZ}`as configuration entries 'xyz'
config.set_env()

def _get_defaults():
    import yaml
    from importlib.resources import files, as_file
    
    file = files(__name__).joinpath('defaults.yaml')
    if not file.is_file():
        raise RuntimeError(f'Can not locate {file}')
        
    with as_file(file) as f:
        with open(f, 'r') as data:
            default_configs = yaml.safe_load(data)
    
    return default_configs
    
# Adding defaults by 'add' method sets them to the lowest priority, so users can provide overrides
config.add(_get_defaults())
