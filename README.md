# Config Generator

This Python module is designed to generate configuration files in Python format from YAML files. The generated files 
use dataclasses and marshmallow for structured data handling, enabling easy configuration management.

### Features

* **Dataclass Generation**: Automatically creates dataclasses for the configuration schema
* **Environment Variable Integration**: Supports default values from environment variables
* **Schema Validation**: Utilizes marshmallow for schema validation and data deserialization
* **Sample Config Generation**: Generates a sample configuration file with placeholders

### Installation

```
pip install -U git+https://github.com/iladrien-hub/genconfig
```

### Usage

```
genconfig [OPTIONS]

Options:
  --inp TEXT  Input config file
  --help      Show this message and exit.
```