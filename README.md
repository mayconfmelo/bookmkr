# To-Do

<center>
  Recursively shows codetags in current directory.
</center>


## Usage

Given `src/file.py`, which contains:

```python
#/usr/local/env python

# TODO: Rename life_unoverse_everything() as ultimate_answer()
def life_universe_everything():
    # TODO: Raise an exception if answer != 42
    answer = calculate_answer()
    
    print("The ultimate answer is: ", answer)

```

Run `todo` inside `src/` will return:

![output](assets/output-example.jpeg)

The number in green is the line which the codetag is located inside the file.

## Description

The [PEP 350](https://peps.python.org/pep-0350/) proposed the 
standardization of source file comments with special meaning, called _codetags_.
These cidetags are used mainly as semantic remainders for developers that
differentiate themselves from other comments and helps to draw attention to
important parts of the code. They can be used in any language that supports
comments, like Python:

```python
# TODO: This is a to-do codetag
```

This CLI program allows to retrieve codetags scattered throughout all text files
inside a directory and shows them neatly formatted in the terminal. By default,
`todo` shows only _TODO_ codetags, as its name suggest; but it support other
codetags, such as _FIXME_ or _BUG_.

For the sake of readability and to avoid mistakes, `todo` only recognizes as
codetags names preceded by at least one space and followed by a colon; in regular
expressions, a codetag must match a `\s+[A+Z]+:.*$` pattern.


## Options

<dl>
  <dt><code><strong>-h, --help</strong></code></dt>
  <dd>Shows a help message.</dd>

  <dt><code><strong>-r, --root</strong></code></dt>
  <dd>Search from the Git project root, if any.</dd>
 
  <dt><code><strong>-q, --quiet</strong></code></dt>
  <dd>Disable verbose outout.</dd>
  
  <dt><code><strong>-p, --path</strong> <em>PATHS</em></code></dt>
  <dd>Search in custom <em>PATHS</em> (absolute, relative, file, folder).</dd>
  
  <dt><code><strong>-e, --exclude</strong> <em>PATHS</em></code></dt>
  <dd>Exclude <em>PATHS</em> from search (absolute, relative, files, folders, globs).</dd>
  
  <dt><code><strong>-c, --codetag</strong> <em>CODETAGS</em></code></dt>
  <dd>Search for custom <em>CODETAGS</em>, each <code>+</code> separated; if no <em>CODETAG</em>, shows a list of common codetags.</dd>
  
  <dt><code><strong>--color, --no-color</strong></code></dt>
  <dd>Toggle terminal colors.</dd>
</dl>


## Configuration File

A `.todo` TOML file which allows to run `todo` with pre-determined options in a
specific project. For example, given a following `src/.todo` file:

```toml
[config]
codetag = "FIXME+TODO"
root = true
```

Then when run `todo` inside `src/` the result will be equivalent to:

```
todo --codetag FIXME+TODO --root
```

## Common Codetags

&nbsp;       | Description
:-----------:|:-------------------------------------------------
**ALL**      | Special: show all codetags.
**TODO**     | Future tasks or planned features.
**FIXME**    | Problematic or ugly code to refactor or cleanup.
**BUG**      | Defective code that needs to be fixed.
**NOBUG**    | Defective code that can't or won't be fixed.
**NOFIX**    | Code problems that can't or won't be fixed.
**REQ**      | Specific, formal requirements.
**RFE**      | Request For Enhancement (in the roadmad)
**IDEA**     | RFE candidate ideas (not in roadmap yet)
**???**      | Unclear or misunderstood details
**!!!**      | Alert that needs imediate attention
**HACK**     | Some alternative course or workaround was used.
**PORT**     | Workarounds specific to OS, language, version.
**CAVEAT**   | Non-intuitive details that needs caution.
**NOTE**     | Needs discussion or further investigation.
**FAQ**      | Popular areas that requires explanation.
**GLOSS**    | Term and concept defintions
**SEE**      | Point to anything external or in the file.
**TODOC**    | Needs documentation.
**CRED**     | Accreditation for third-party contributions.
**STAT**     | Status maturity indicatitor
**RVD**      | Indicatites that review was conducted.
**XXX**      | Something wrong or not accepted.
**INFO**     | Any type of information.
**OPTIMIZE** | Something that needs improvement.
**DESC**     | Short description.
**USAGE**    | Assist in the des in the correct way of use

The `todo` is not limited by only those codetags above, it recognizes any custom
codetag with any name — although is recomended to use names between 3 to 7
characters. The special _ALL_ "codetag" is not a codetag itself, but an umbrella
option to enable searching for all and any codetags with names at least 3
characters long.


## Codetag Search

The `todo` searches for codetags inside all UTF-8 encoded files in a directory
and its subdirectories; by default, the directory searched is the terminal
working directory.

```
src/
├── .git/
├── dev/
│   └── manual.pdf
├── modules/
│   ├── init.py
│   └── utils.py
└── assets/
    ├── cover.png
    └── data.toml
```

If `todo` is run in the `src/` directory above, it could find codetags inside
`init.py`, `utils.py`, and `data.toml`.

The `todo --root` option works by searching for a `.git/` directory inside the
actual directory, if not found it just `cd ..` and continues searching in the
parent directory recursively. For example, `todo --root` from inside `src/assets/`
will actually run from `src/` — the project root where `.git/` is located.