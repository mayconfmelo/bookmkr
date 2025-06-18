# Book Maker

<center>
  Build Pandoc books based on instructions in _bookrecipe.toml_ files.
</center>


## Quick Start

```
bookmkr --init
```

Given that the command above was executed inside a `project/` directory, it
creates:

```
project/
 ├── 01.md
 ├── assets/
 │    ├── cover.png
 │    ├── filters.lua
 │    ├── styles.css
 │    └── templates/
 ├── book/
 │    └── Title.epub
 └── bookrecipe.toml
```

When executed again, `bookmkr` will search for a _bookrecipe.toml_ to identify
the book project root and colect data about the book and its content. By
default, it will search for content (markdown files) in project root and
generate a book called _Title_ in ePub format — all of this can be customized in
_bookrecipe.toml_ file.


## Description

Can generate books in various formats and manage complex generation processes
through a _bookrecipe.toml_ file. This file identifies a book project,
and must lie in its root directory; it defines all book metadata such as title,
subtitle, publisher, date, all Pandoc options used, and the specific `bookmkr`
options.

It also allows to automatically execute helper commands and scripts before and
after the book generation itself — this is useful to prepare input files before
generation or adjust the output files after the generation.

> [!NOTE]
> `bookmkr` uses Typst as PDF engine and its _[min-book](https://typst.app/universe/package/min-book)_
> package as template to generate books.


## Options

<dl>
  <dt><code><strong>-h, --help</strong></code></dt>
  <dd>Shows a help message.</dd>

  <dt><code><strong>-i, --init</strong></code></dt>
  <dd>Initialize a new book project.</dd>

  <dt><code><strong>-w, --watch</strong></code></dt>
  <dd>Enables continuous building mode.</dd>
  
  <dt><code><strong>-v, --verbose</strong></code></dt>
  <dd>Enables verbose mode.</dd>
 
  <dt><code><strong>-c, --color, --no-color</strong></code></dt>
  <dd>Set color in texs.</dd>
  
</dl>

Optionally, a positional _**`format`**_ argument can be passed to set the book output file
format — it overwrites the `bookrecipe.toml` option with the same name.


## Dependencies

To work properly, `bookmkr` needs the folowing programs installed and working:

- Pandoc 
- Python
  - tomli
  - PyYAML
  - watchdog


## Configuration File

The _bookrecipe.toml_ concentrates all options needed to manage the project.
By default, it assumes the following values:

```toml
[general]
format = "epub"
output = "book"
sources = "*.md"
cmd-before = false
cmd-after = false

[book]
title = "Title"
# subtitle = "Subtitle"
# lang = "en-US"
# date = 2024
# edition = 1
# volume = 1
# author = [ "Author" ]
# publisher = [ "Publisher" ]
# date = 2025
# cover-image = "assets/cover.png"
# titlepage = auto
# catalog = "none"
# errata = "none"
# dedication = "none"
# acknowledgements = "none"
# epigraph = "none"
# toc = true
# part = "auto"
# chapter = "auto"
# cfg = [ {name = "font-size", value = '22pt'} ]

[pandoc.flags]
split-level = 2
epub-title-page = true
pdf-engine = "typst"
template = "./assets/templates/template"
lua-filter = "./assets/filters.lua"
css = "assets/styles.css"

```

The commented `#` values are suggestions to the user, while the others are default
values. It's not necessary to set all these options; in fact, if you delete all
of them and use a blank _bookrecipe.toml_ file, they will fallback to these
defaults — after all, all options should be... optional.

<dl>

  <dt><strong>format</strong></dt>
  <dd>The book output file format (CLI option overwrites it).</dd>
  
  <dt><strong>output</strong></dt>
  <dd>The book output file directory, relative to the project root.</dd>
  
  <dt><strong>sources</strong></dt>
  <dd>A glob that colloects all input files used to generate tue book.</dd>

  <dt><strong>cmd-before</strong></dt>
  <dd>A string or arrays with a single shell command to he executed before the
  main <code>pandoc</code> parsing.</dd>

  <dt><strong>cmd-after</strong></dt>
  <dd>A string or arrays with a single shell command to he executed after the
  main <code>pandoc</code> parsing.</dd>
  
  <dt><strong>[book]</strong></dt>
  <dd>Defines book metadata such as title, author, dedication, etc.</dd>

  <dt><strong>[pandoc.args]</strong></dt>
  <dd>Set Pandoc argument/flag options and its values; flags without value are
  set with a <code>"true"</code> value. Brief one-letter arguments are not
  supported.</dd>
  
</dl>