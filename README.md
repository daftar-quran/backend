# backend


## layer management


```

cd layers

### Creates a 'python' folder that contains the content of the layer
sh build_layer.sh

### Publishes a new version of the layer
sh publish_layer.sh

```

## How to install on VS Code

- Create a .vscode folder and create inside a `settings.json` file

```

{
    "python.analysis.extraPaths": ["/{path_to_the_folder}/daftar_backend/layers/python"]
}
```