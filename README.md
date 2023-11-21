# Marc XML to table converter

## Description

Librarians may want to list and explore Marc 21 fields in a tabular format. `marcxml2table.py` converts Marc XML data into a tab separated values table where every subfield is a separate column and every record a row of data.

## Usage

There is a `-h` switch to print a how-to-use message:

`python marcxml2table.py -h`

### Execution
`python marcxml2table.py marc.xml marc.tsv "001 035 85640"`

### Positional arguments

#### marc.xml

A Marc XML file for input. It holds bibliographic, authorities or holdings records in `<record/>` elements. Often, Marc XML is created thru an Export job, which has no namespaces in it. *Currently, this script only looks for elements without any namespace.*

#### marc.tsv

A tab separated values file to write the output to.

#### List of fields to extract: "001 035 85640"

A blank seperated list of fields to be converted. The LDR/Leader field should be written as `leader`.

To convert only Marc fields with specific indicators, use the five character notation.

E.g., `85640` only outputs Marc 856 fields with first indicator = 4 and second indicator = 0.

For any indicator, use an asterisk sign `*` as wildcard. For the blank indicator, use the hash sign `#`.

## Acknowledgement

Kudos to [gabriele-h](https://github.com/gabriele-h) - the general idea is taken from her [alma_export_extractor](https://github.com/gabriele-h/alma_export_extractor) project. Also, some code snippets were copy-pasted 🍝