# Book Maker

<center>
  Build Pandoc books based on instructions in bookrecipe.toml files.
</center>


## Quick Start

```
bookmkr --init
```

Given that the command above was executed in a `project/` directory, it creates:

```
project/
├── 01.md
├── assets/
│   ├── cover.png
│   ├── filters.lua
│   ├── styles.css
│   └── templates/
├── book/
│   └── Title.FORMAT
└── bookrecipe.toml

```

When executed again, `bookmkr` search for `bookrecipe.toml` to colect data about
the book and and where is the content (Markdown files, by default) to generate a book
in _FORMAT_ inside `book/`


## Description

Allows to generate books in various formats and to manage complex generation
processes through a `bookrecipe.toml` file. This file identifies a book project,
and must lie in its root directory; it defines all book metadata such as title,
subtitle, publisher, or date, and all Pandoc options used — as well as specific
_bookmkr_ options.

Besides facilitate Pandoc management, _bookmkr_ also allows to
automatically execute helper commands and scripts before and after the book
generation itself — this is useful to prepare input files before generation or
adjust the output files after the generation.

> [!NOTE]
> _bookmkr_ uses Typst as PDF engine and its _[min-book](https://typst.app/universe/package/min-book)_
> package as template to generate books.


## Options

<dl>
  <dt><code><strong>-h, --help</strong></code></dt>
  <dd>Shows a help message.</dd>

  <dt><code><strong>-v, --verbose</strong></code></dt>
  <dd>Enables verbose mode.</dd>
 
  <dt><code><strong>-l, --loop</strong></code></dt>
  <dd>Enables continuous building mode.</dd>
  
  <dt><code><strong>-s, --sleep-time</strong> <em>SLEEP_TIME</em></code></dt>
  <dd>Set the <code><em>SLEEP_TIME</em></code> between each build in continuous building mode.</dd>
  
  <dt><code><strong>-i, --init</strong></code></dt>
  <dd>Initialize a new book project.</dd>
</dl>

Optionally, a sole _**`format`**_ argument can be passed to set the book output file
format — it overwrites the `bookrecipe.toml` option with the same name.


## Configuration File

The `bookrecipe.toml` concentrates all options needed to manage the project.
By default, it assumes the following values:

```toml
[general]
format = "pdf"
output = "book"
sources = "*.md"
cmd-before = false
cmd-after = false

[pandoc.flags]
split-level = 2
epub-title-page = true
epub-cover-image = "assets/cover.png"
pdf-engine = "typst"
template = "./assets/templates/template"
lua-filter = "./assets/filters.lua"
css = "assets/styles.css"

[book]
title = "Title"
subtitle = "Subtitle"
lang = "en-US"
date = 2024
author = "Author"
```

<dl>
  <dt><strong>format</strong></dt>
  <dd>The book output file format (CLI option overwrites it).</dd>
  
  <dt><strong>output</strong></dt>
  <dd>The book output file directory, relative to the project root.</dd>
  
  <dt><strong>sources</strong></dt>
  <dd>A glob that colloects all input files used to generate tue book.</dd>
  
  <dt><strong>[pandoc.flags]</strong></dt>
  <dd>Set Pandoc option flags and its values; each <code>pandoc --flag=value</code>
  becomes a <code>flag = value</code> TOML pair. Brief <code>-f</code> flags are not supported.</dd>
  
  <dt><strong>[book]</strong></dt>
  <dd>Defines the book metadata such as title, author, dedication, etc.</dd>
  
</dl>