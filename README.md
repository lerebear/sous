# sous

This is a tool that I've built to support my personal cooking workflow. It is inspired by the [cooklang](https://cooklang.org) ecosystem.

## .sous file format

This tool is built around the `.sous` file format, which defines a lightweight markup format for writing recipes.

At present, the format is designed to serve two purposes:

- Provide a human-readable and vendor-agnostic serialization format for recipes
- Make it easy to automate the creation of a shopping list from a given list of recipes

Here's an example:

```txt
# Roasted broccoli

@author Lérè Williams
@syntax 1

{2} large [broccoli crowns], washed and trimmed
{3 cloves} [garlic], minced
{} extra virgin [olive oil | avocado oil]
{}[red pepper flakes]
{1/2}[lemon], for juicing
% Syntax for optional ingredients coming soon!

Pre-heat oven to 415 F.

Place trimmed [broccoli crowns] in a large bowl and season with [garlic], [red pepper flakes], {}[Kosher salt] and freshly ground {}[black pepper]. Toss with [olive oil] and mix until ingredients are well combined.

Transfer broccoli to a parchment-lined baking sheet and roast for 20 minutes, flipping broccoli halfway through to achieve an even char.

Remove baking sheet from oven. Squeeze [lemon] juice evenly over the broccoli. Serve warm.
```

The snippet above demonstrates all of the supported language features:

- Recipe title (`# Roasted broccoli`)
- Metadata attributes (e.g. `@author Lérè Williams`)
- Block ingredient definitions (e.g. `{2} large [broccoli crowns], washed and trimmed`)
  - Alternative ingredients (e.g. `{} extra virgin [olive oil | avocado oil]`)
- Inline ingredient definitions (e.g. `{}[black pepper]`)
- Inline ingredient references (e.g. `[broccoli crowns]`)
- Comments (e.g. `% Syntax for optional ingredients coming soon!`)

The format may be extended to support other uses in the future.
