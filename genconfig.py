import ast
import itertools
import os
import re

import astor
import click
import yaml

__version__ = '0.2.3'

from astor.source_repr import split_lines

__debug = False


def write_file(text, fp, end="\n"):
    fp.write(text + end)


def name_generator():
    yield "_Config"

    for i in itertools.count():
        yield f"_Nested{i + 1}"


def gen_dataclass_ann():
    # return ast.Attribute(
    #     value=ast.Name(id='dataclasses', ctx=ast.Load()),
    #     attr='dataclass',
    #     ctx=ast.Load()
    # )
    return ast.Name(id='dataclass', ctx=ast.Load())


def gen_ann_assign(name, kind, envvar=None):
    value = None
    if envvar:
        value = ast.Call(
            func=ast.Name(id='field', ctx=ast.Load()),
            args=[],
            keywords=[
                ast.keyword(
                    arg='default_factory',
                    # value=ast.Call(
                    #     func=ast.Name(id='partial', ctx=ast.Load()),
                    #     args=[
                    #         ast.Attribute(
                    #             value=ast.Name(id='os', ctx=ast.Load()),
                    #             attr='getenv',
                    #             ctx=ast.Load()
                    #         ),
                    #         ast.Constant(envvar)
                    #     ],
                    #     keywords=[]
                    # )
                    # value=ast.Lambda(
                    #     args=ast.arguments(
                    #         args=[],
                    #         defaults=[]
                    #     ),
                    #     body=ast.Call(
                    #         func=ast.Name(id=kind, ctx=ast.Load()),
                    #         args=[
                    #             ast.Subscript(
                    #                 value=ast.Attribute(
                    #                     value=ast.Name(id='os', ctx=ast.Load()),
                    #                     attr='environ',
                    #                     ctx=ast.Load()
                    #                 ),
                    #                 slice=ast.Index(value=ast.Constant(value=envvar)),
                    #                 ctx=ast.Load()
                    #             )
                    #         ],
                    #         keywords=[]
                    #     )
                    # )
                    value=ast.Call(
                        func=ast.Name(id='_environ', ctx=ast.Load()),
                        args=[
                            ast.Constant(envvar),
                            ast.Name(id=kind, ctx=ast.Load())
                        ],
                        keywords=[]
                    )
                )
            ]
        )

    return ast.AnnAssign(
        target=ast.Name(id=name, ctx=ast.Store()),
        annotation=ast.Name(id=kind, ctx=ast.Load()),
        simple=True,
        value=value
    )


def gen_assign(name, kind, args=None):
    if args is None:
        args = []

    return ast.Assign(
        targets=[
            ast.Name(id=name, ctx=ast.Store())
        ],
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='fields', ctx=ast.Load()),
                attr=kind,
                ctx=ast.Load()
            ),
            args=args,
            keywords=[]
        )
    )


def gen_with_node(module, basename, schema_name, model_name):
    filename = ast.Name(id="__config_fn", ctx=ast.Load())
    default_fn = ast.Call(
        func=ast.Attribute(
            value=ast.Attribute(
                value=ast.Name(id='os', ctx=ast.Load()),
                attr='path',
                ctx=ast.Load()
            ),
            attr='join',
            ctx=ast.Load()
        ),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id='os', ctx=ast.Load()),
                        attr='path',
                        ctx=ast.Load()
                    ),
                    attr='dirname',
                    ctx=ast.Load()
                ),
                args=[ast.Name(id='__file__', ctx=ast.Load())],
                keywords=[]
            ),
            ast.Str(s=basename + '.yml')
        ],
        keywords=[]
    )
    environ_fn = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id='os', ctx=ast.Load()),
            attr='getenv',
            ctx=ast.Load()
        ),
        args=[
            ast.Str(s='CONFIG_FN'),
            default_fn
        ],
        keywords=[]
    )

    filename_assign = ast.Assign(
        targets=[
            filename,
        ],
        value=environ_fn
    )

    cond = ast.If(
        test=ast.Call(
            func=ast.Name(id='os.path.isfile', ctx=ast.Load()),
            args=[filename],
            keywords=[]
        ),
        body=[
            ast.With(
                items=[
                    ast.withitem(
                        context_expr=ast.Call(
                            func=ast.Name(id='open', ctx=ast.Load()),
                            args=[
                                filename
                            ],
                            keywords=[]
                        ),
                        optional_vars=ast.Name(id='f', ctx=ast.Store())
                    )
                ],
                body=[
                    ast.AnnAssign(
                        target=ast.Name(id='config', ctx=ast.Store()),
                        annotation=ast.Name(id=model_name, ctx=ast.Load()),
                        simple=True,
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Call(
                                    func=ast.Name(id=schema_name, ctx=ast.Load()),
                                    args=[],
                                    keywords=[]
                                ),
                                attr='load',
                                ctx=ast.Load()
                            ),
                            args=[
                                ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id='yaml', ctx=ast.Load()),
                                        attr='load',
                                        ctx=ast.Load()
                                    ),
                                    args=[ast.Name(id='f', ctx=ast.Load())],
                                    keywords=[ast.keyword(arg='Loader', value=ast.Attribute(
                                        value=ast.Name(id='yaml', ctx=ast.Load()),
                                        attr='Loader',
                                        ctx=ast.Load()
                                    ))]
                                )
                            ],
                            keywords=[]
                        )
                    ),

                ]
            ),
        ],
        orelse=[
            ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='warnings', ctx=ast.Load()),
                    attr='warn',
                    ctx=ast.Load()
                ),
                args=[
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Constant(value='{} was not found!'),
                            attr='format',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Name(id='__config_fn', ctx=ast.Load())
                        ],
                        keywords=[]
                    ),
                    ast.Name(id='RuntimeWarning', ctx=ast.Load())
                ],
                keywords=[]
            )),
            ast.AnnAssign(
                target=ast.Name(id='config', ctx=ast.Store()),
                annotation=ast.Name(id=model_name, ctx=ast.Load()),
                simple=True,
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(id=schema_name, ctx=ast.Load()),
                            args=[],
                            keywords=[]
                        ),
                        attr='load',
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Dict(keys=[], values=[])
                    ],
                    keywords=[]
                )
            )
        ]
    )

    module.body.extend([
        filename_assign,
        cond,
        ast.If(
            test=ast.Compare(
                left=ast.Name(id='__name__', ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value='__main__')]
            ),
            body=[
                ast.Expr(
                    value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()),
                                   args=[ast.Name(id='config', ctx=ast.Load())],
                                   keywords=[]))
            ],
            orelse=[]
        )
    ])


def gen_post_load(model_name):
    method_def = ast.FunctionDef(
        name='make_dataclass',
        args=ast.arguments(
            args=[
                ast.arg(arg='self', annotation=None),
                ast.arg(arg='data', annotation=None),
                ast.arg(arg='many', annotation=None),
                ast.arg(arg='**__ignored', annotation=None)
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[]
        ),
        body=[],
        decorator_list=[
            ast.Name(id='post_load', ctx=ast.Load())
        ],
        returns=None
    )

    # Create the if statement inside the method
    if_statement = ast.If(
        test=ast.Name(id='many', ctx=ast.Load()),
        body=[
            ast.Return(
                value=ast.ListComp(
                    elt=ast.Call(
                        func=ast.Name(id=model_name, ctx=ast.Load()),
                        args=[ast.Name(id="**item", ctx=ast.Load())],
                        keywords=[]
                    ),
                    generators=[
                        ast.comprehension(
                            target=ast.Name(id='item', ctx=ast.Store()),
                            iter=ast.Name(id='data', ctx=ast.Load()),
                            ifs=[],
                            is_async=0
                        )
                    ]
                )
            )
        ],
        orelse=[
            ast.Return(
                value=ast.Call(
                    func=ast.Name(id=model_name, ctx=ast.Load()),
                    args=[ast.Name(id="**data", ctx=ast.Load())],
                    keywords=[]
                )
            )
        ]
    )

    # Add the if statement to the body of the method
    method_def.body.append(if_statement)
    return method_def


def gen_classes(config, gen_name, module):
    name = next(gen_name)

    schema_name = name + "Schema"
    model_name = name + "Model"

    schema_node = ast.ClassDef(
        name=schema_name,
        bases=[
            ast.Name(id="Schema", ctx=ast.Load())
        ],
        keywords=[],
        body=[],
        decorator_list=[]
    )

    model_node = ast.ClassDef(
        name=model_name,
        bases=[],
        keywords=[],
        body=[],
        decorator_list=[
            gen_dataclass_ann()
        ]
    )

    for k, v in config.items():
        if isinstance(v, dict):
            n_schema_name, n_model_name = gen_classes(v, gen_name, module)
            model_node.body.append(gen_ann_assign(k, n_model_name))

            schema_node.body.append(gen_assign(k, 'Nested', [
                ast.Call(
                    func=ast.Name(id=n_schema_name, ctx=ast.Load()),
                    args=[],
                    keywords=[]
                )
            ]))

        elif isinstance(v, list):
            model_node.body.append(gen_ann_assign(k, 'list'))

            types = list({type(i).__name__.capitalize() for i in v})

            schema_item_type = str(types[0]).capitalize() if len(types) == 1 else "Raw"
            schema_node.body.append(gen_assign(k, 'List', [
                ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='fields', ctx=ast.Load()),
                        attr=schema_item_type,
                        ctx=ast.Load()
                    ),
                    args=[],
                    keywords=[]
                )
            ]))

        else:
            type_name = type(v).__name__
            envvar = k.upper() if name == '_Config' else None

            model_node.body.append(gen_ann_assign(k, type_name, envvar))
            schema_node.body.append(gen_assign(k, type_name.capitalize()))

    model_node.body.sort(key=lambda x: x.value is not None)

    schema_node.body.append(gen_post_load(model_name))

    module.body.append(model_node)
    module.body.append(schema_node)

    return schema_name, model_name


def gen_environ_func(module):
    lambda_expr = ast.Lambda(
        args=ast.arguments(args=[], defaults=[]),
        body=ast.Call(
            func=ast.Name(id='cast', ctx=ast.Load()),
            args=[ast.Subscript(
                value=ast.Attribute(
                    value=ast.Name(id='os', ctx=ast.Load()),
                    attr='environ',
                    ctx=ast.Load()
                ),
                slice=ast.Index(value=ast.Name(id='key', ctx=ast.Load())),
                ctx=ast.Load()
            )],
            keywords=[]
        )
    )

    function_def = ast.FunctionDef(
        name='_environ',
        args=ast.arguments(
            args=[
                ast.arg(arg='key'),
                ast.arg(arg='cast')
            ],
            defaults=[]
        ),
        body=[
            ast.Return(value=lambda_expr)
        ],
        decorator_list=[]
    )

    module.body.append(function_def)


def generate_config_py(fn, basename, config):
    # creating module
    module = ast.Module(body=[
        ast.Expr(value=ast.Str(s=f"\n"
                                 f"This file is generated by genconfig v{__version__} by Iladrien\n"
                                 f"\n"
                                 f"This file uses:\n"
                                 f"    - PyYAML from https://pypi.org/project/PyYAML/\n"
                                 f"    - marshmallow from https://marshmallow.readthedocs.io/en/stable/\n")),
        ast.Import(names=[ast.alias(name='os', asname=None)]),
        ast.Import(names=[ast.alias(name='yaml', asname=None)]),
        ast.Import(names=[ast.alias(name='warnings', asname=None)]),
        # ast.Import(names=[ast.alias(name='dataclasses', asname=None)]),
        ast.ImportFrom(
            module='dataclasses',
            names=[
                ast.alias(name='field', asname=None),
                ast.alias(name='dataclass', asname=None),
            ],
            level=0
        ),
        ast.ImportFrom(
            module='marshmallow',
            names=[
                ast.alias(name='fields', asname=None),
                ast.alias(name='Schema', asname=None),
                ast.alias(name='post_load', asname=None),
            ],
            level=0
        ),
        ast.Assign(
            targets=[ast.Name(id='__all__', ctx=ast.Store())],
            value=ast.List(elts=[ast.Constant(value='config')], ctx=ast.Load())
        ),
    ], type_ignores=[])

    gen_environ_func(module)

    # generating classes
    schema_name, model_name = gen_classes(config, name_generator(), module)

    # Create the With node
    gen_with_node(module, basename, schema_name, model_name)

    # printing result
    source = astor.to_source(module, pretty_source=lambda x: ''.join(split_lines(x, maxline=130)))
    print(source)

    with open(fn, "w", encoding="utf-8") as f:
        f.write(source)


def config_sample(match: re.Match):
    text = match.group(0)
    repl = match.group(1)

    target = ""
    if "mongodb+srv://" in repl:
        target = '"mongodb+srv://"'
    elif re.match(r"[\"\'].*?[\"\']", repl):
        target = '""'
    elif re.match(r"\d+", repl):
        target = "0"

    return text.replace(repl, target)


def generate_config_sample(fn_in, fn_out):
    with open(fn_in) as f, open(fn_out, "w") as fo:
        fo.write(re.sub(r"\w+:\s([\"\'].*?[\"\']|\d+)", config_sample, f.read()))


@click.command()
@click.option("--inp", "inp", default="config.yml", help="Input config file")
def main(inp):
    realpath = os.path.realpath(inp)

    working_dir = os.path.dirname(realpath)
    basename, ext = os.path.splitext(os.path.basename(realpath))

    o_python = os.path.join(working_dir, f"{basename}.py")
    o_sample = os.path.join(working_dir, f"{basename}.sample{ext}")

    with open(realpath, encoding="utf-8") as f:
        config = yaml.load(f, yaml.Loader)

    generate_config_py(o_python, basename, config)
    generate_config_sample(realpath, o_sample)


if __name__ == '__main__':
    main()
