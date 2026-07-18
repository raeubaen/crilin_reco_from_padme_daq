See wiki

Per il sottomodulo:

Per fare in modo che `git pull` aggiorni anche i submodule puoi usare:

```bash
git pull --recurse-submodules
```

oppure
```bash
git config --global submodule.recurse true
```
