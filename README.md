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

## Shopping list configuration

You can control how items in a shopping list are grouped and sorted by providing a TOML configuration file. Each table in the file defines a category, and items within each category are sorted alphabetically. Categories appear in the order they are defined in the file, and any items not listed in the config are grouped under "other" at the end.

Here's an example:

```toml
[dairy]
items = ["milk", "butter", "eggs"]

[produce]
items = [
  "garlic",
  "onion",
  "broccoli crowns",
  "cilantro",
]

[canned]
items = ["olive oil", "beans", "chickpeas"]
```

### CLI

Pass the config file to the `shop` command with the `--config` flag:

```sh
sous shop --cookbook ~/recipes --config ~/recipes/store-layout.toml
```

Any selected ingredients that don't appear in the config file will be reported as warnings on stderr.

### iOS

On the shopping list screen, tap the menu (ellipsis button) and select **Organize By** to choose from any `.toml` files found in the current cookbook directory. Sections are collapsible — tap a section header to collapse or expand it, or use **Collapse All** / **Expand All** from the menu.
