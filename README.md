# sous

This is a tool that I've built to support my personal cooking workflow. It is inspired by the [cooklang](https://cooklang.org) ecosystem. 

## .sous file format

This tool is built around the `.sous` file format, which defines a lightweight markup format for writing recipes.

At present, the format is designed to serve two purposes:

- Provide a human-readable and vendor-agnostic serialization format for recipes
- Make it easy to automate the creation of a shopping list from a given list of recipes

Here's an example:

```txt
---
author: Lérè Williams
sous-version: 0
---

# Roasted broccoli

[broccoli]: 2 large crowns of broccoli, washed and trimmed {2 crowns}
[garlic]: 3 large garlic cloves, minced {3 cloves}
[olive oil]: extra virgin olive oil
[red pepper flakes]
[lemon] lemon juice {1}

Pre-heat oven to 415 F.

Place trimmed [broccoli][] in a large bowl and season with [garlic][], [red pepper flakes][], [kosher salt]{} and freshly ground [black pepper]{}. Toss with [olive oil][] and mix until ingredients are well combined.

Transfer broccoli to a parchment-lined baking sheet and roast for 20 minutes, flipping broccoli halfway through to achieve an even char.

Remove baking sheet from oven. Squeeze juice of [half a lemon][lemon] evenly over the broccoli. Serve warm.
```

The snippet above demonstrates all of the supported language features:

- YAML frontmatter which defines recipe metadata (e.g. `author: Lérè Williams`)
- Recipe title (`# Roasted broccoli`)
- Block ingredient definitions (e.g. `[garlic]: 3 large garlic cloves, minced {3 cloves}`)
- Inline ingredient definitions (e.g. `[black pepper]{}`)
- Ingredient references (e.g. `[broccoli][]`)

The format may be extended to support other uses in the future.