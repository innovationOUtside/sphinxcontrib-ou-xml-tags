# sphinxcontrib-ou-xml-tags

*Needs repo name change*

Simple Sphinx extension to create Sphinx parseable markdown admonitions that can be used to render HTML components and Sphinx XML elements that render nicely to OU-XML:

- `ou-audio`: simple tag for embedding audio
- `ou-video`: simple tag for embedding video [TO DO]
- `ou-html5`: simple tag for embedding html [TO DO]
- `ou-activity`: simple [?]

## BUILD and INSTALL

`python3 -m build`

Install as:

`python3 -m pip install .`

## HTML packages

```bash
cd sphinxcontrib_ou_media/packages/shinylite-py
zip -r -X "../../../dist/shinylite-py-01.zip" .
cd ../..
```