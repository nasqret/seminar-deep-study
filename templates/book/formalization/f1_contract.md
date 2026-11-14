# The contract: what exactly is proved

Everything on this page is read from `formal/` while the book is built; nothing is retyped.

## The comparator configuration

```{literalinclude} ../../formal/comparator.json
:language: json
```

## The statement surface

````{dropdown} formal/Challenge.lean
```{literalinclude} ../../formal/Challenge.lean
:language: lean4
```
````

## A proof, as it stands in the library

```{literalinclude} ../../formal/{{LEAN_NAME}}/Main.lean
:language: lean4
:start-at: theorem R_simple
:end-at: norm_num at key
```

## Divergences from the paper

```{literalinclude} ../../formal/formalization.yaml
:language: yaml
:start-at: "fidelity:"
:end-before: "review:"
```
