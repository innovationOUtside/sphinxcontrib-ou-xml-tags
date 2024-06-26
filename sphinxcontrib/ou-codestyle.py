"""codestyle extension to embed codestyle in html sphinx output.

Originally based on https://github.com/sphinx-contrib/video/
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from sphinxcontrib_ou_media.utils import resources_path, fetch_template

import json
import os
import uuid
import zipfile

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective, SphinxTranslator
from sphinx.util.osutil import copyfile

from sphinxcontrib_ou_media.utils import handle_css_js_assets

__author__ = "Raphael Massabot & Tony Hirst"
__version__ = "0.0.2"

logger = logging.getLogger(__name__)

SUPPORTED_OPTIONS: List[str] = [
    "height",
    "width",
    "src",
    "caption",
    "type",
    "viewer",
    "theme",
    "keep",
]
"List of the supported options attributes"

CODE_TEMPLATE = fetch_template(
    "assets", "html-zip-resources", "templates", "ou-code-index.html"
)

# Example: https://executablebooks.github.io/thebe/
# Cribbed from: https://github.com/stevejpurves/lite-quickstart-example/tree/gh-pages
THEBE_LITE_TEMPLATE = fetch_template(
    "assets", "html-zip-resources", "templates", "ou-thebe-lite-index.html"
)


# Via Chatgpt:
# function to mimic: zip -j MYZIP.zip MYDIR
# zip files to root of zipfile, ignoring path
def zip_directory(source_folder, output_zipfile):
    source_path = Path(source_folder)
    with zipfile.ZipFile(output_zipfile, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_path.glob("**/*"):
            if file_path.is_file():
                arcname = file_path.relative_to(source_path)
                print(arcname)
                zipf.write(file_path, arcname)


class ou_codestyle(nodes.General, nodes.Element):
    """codestyle node."""

    pass


class codestyle(SphinxDirective):
    """codestyle directive.

    Wrapper for the html <codestyle> tag embedding all the supported options
    """

    has_content: bool = True
    required_arguments: int = 1
    optional_arguments: int = 1
    option_spec: Dict[str, Any] = {
        "src": directives.unchanged,
        "width": directives.unchanged,
        "height": directives.unchanged,
        "caption": directives.unchanged,
        "type": directives.unchanged,
        "viewer": directives.unchanged,
        "theme": directives.unchanged,
        "keep": directives.unchanged,
    }

    def run(self) -> List[ou_codestyle]:
        """Return the codestyle node based on the set options."""
        env: BuildEnvironment = self.env

        # check options that need to be specific values
        # TO DO?

        # Get the asset location
        _lang = self.arguments[0]
        # Copy the media asset over to the build directory
        _src = self.options.get("src", "")
        _width = self.options.get("width", "")
        _height = self.options.get("height", "")
        _type = self.options.get("type", "code").lower()
        os.makedirs(env.app.builder.outdir, exist_ok=True)
        if _src and not bool(urlparse(_src).netloc):
            # TO DO - should we use the codesnippet,
            # and assume file is a code file to pass?
            outpath = os.path.join(env.app.builder.outdir, _src)
            copyfile(_src, outpath)
            # TO DO what if it is a url?
        elif self.content:
            _src_root = f"{uuid.uuid4().hex}"
            os.makedirs("_tmp", exist_ok=True)
            if _type == "thebelite":
                html = THEBE_LITE_TEMPLATE.format(
                    lang=_lang, code="\n".join(self.content)
                )
                _src_zip = f"JL-{_src_root}.zip"
                tmp_path = os.path.join("_tmp", _src_zip)
                jl_dir_path = resources_path().joinpath(
                    "assets", "html-zip-resources", "thebelite"
                )
                zip_directory(jl_dir_path, tmp_path)
                # outpath = os.path.join(env.app.builder.outdir, _src_zip)
                with zipfile.ZipFile(tmp_path, "a", zipfile.ZIP_DEFLATED) as zipf:
                    # Create a new file named 'index.html' and write the text to it
                    zipf.writestr("index.html", html)
                # copyfile(tmp_path, outpath)
                # if not _height:
                #    # TO DO - have an optional line height param?
                #    _line_height = 15
                #    _height = _line_height * len(self.content) + 200
                _ou_codestyle = ou_codestyle(
                    src=tmp_path,
                    height=_height,
                    width=_width,
                    interactivetype="thebelite",
                    keep=self.options.get("keep", "never"),
                )
            elif _type == "shinylite-py":
                shiny_app = [
                    {
                        "name": "app.py",
                        "type": "text",
                        "content": "\n".join(self.content),
                    }
                ]
                _src_zip = f"SH-py-{_src_root}.zip"
                tmp_path = os.path.join("_tmp", _src_zip)
                shl_dir_path = resources_path().joinpath(
                    "assets", "html-zip-resources", "shinylite-py"
                )
                zip_directory(shl_dir_path, tmp_path)
                # outpath = os.path.join(env.app.builder.outdir, _src_zip)
                with zipfile.ZipFile(tmp_path, "a", zipfile.ZIP_DEFLATED) as zipf:
                    # Create a new file named 'index.html' and write the text to it
                    zipf.writestr("app.json", json.dumps(shiny_app))
                # copyfile(tmp_path, outpath)
                # if not _height:
                #    # TO DO - have an optional line height param?
                #    _line_height = 15
                #    _height = _line_height * len(self.content) + 200
                _ou_codestyle = ou_codestyle(
                    src=tmp_path,
                    height=_height,
                    width=_width,
                    interactivetype="shinylite-py",
                    keep=self.options.get("keep", "never"),
                )
            elif _type == "Xshinylite-py":
                shiny_app = [
                    {
                        "name": "app.py",
                        "type": "text",
                        "content": "\n".join(self.content),
                    }
                ]
                txt = json.dumps(shiny_app)
                _src = f"XShPy-{_src_root}.py"
                tmp_path = os.path.join("_tmp", _src)
                outpath = os.path.join(env.app.builder.outdir, _src)
                with open(tmp_path, "w") as f:
                    f.write(txt)
                # copyfile(tmp_path, outpath)
                # if not _height:
                #    # TO DO - have an optional line height param?
                #    _line_height = 15
                #    _height = _line_height * len(self.content) + 200
                _ou_codestyle = ou_codestyle(
                    src=tmp_path,
                    height=_height,
                    width=_width,
                    keep=self.options.get("keep", "never"),
                    interactivetype="Xshinylite-py",
                )
            else:
                _codesnippet = (
                    self.options.get("viewer", "th_hack").lower() == "codesnippet"
                )
                # Currently, theme and code only apply to codesnippet
                _theme = self.options.get("theme", "light").lower()
                if _codesnippet:
                    content = "\n".join(self.content)
                    _src = f"{_src_root}.txt"
                else:
                    content = CODE_TEMPLATE.format(
                        lang=_lang, code="\n".join(self.content)
                    )
                    # This uses my crude take on codesnippet
                    # May have a parameter to use codesnippet or this?
                    _src = f"{_src_root}.html"
                tmp_path = os.path.join("_tmp", _src)
                # Copy the media asset over to the build directory
                outpath = os.path.join(env.app.builder.outdir, _src)
                with open(tmp_path, "w") as f:
                    f.write(content)
                copyfile(tmp_path, outpath)
                # if not _height:
                #    # TO DO - have an optional line height param?
                #    _line_height = 15
                #    _height = _line_height * len(self.content)
                _ou_codestyle = ou_codestyle(
                    src=tmp_path,
                    height=_height,
                    width=_width,
                    theme=_theme,
                    codetype=_lang,
                    codesnippet=_codesnippet,
                    keep=self.options.get("keep", "never"),
                )

        # ?Crib Jupyter Book and adds a caption etc
        # https://github.com/executablebooks/MyST-NB/blob/9ddc821933826a7fd2ea9bbda1741f4f3977eb7e/myst_nb/ext/eval/__init__.py#L193C9-L201C39
        """ TO DO
        _caption = self.options.get("caption", "")
        if _caption:
            node = nodes.Element()  # anonymous container for parsing
            self.state.nested_parse(self.content, self.content_offset, node)
            caption = #how do we create a node we can add?
            # set its text to _caption
            _ou_codestyle += caption
        """

        return [_ou_codestyle]


def visit_ou_codestyle_html(translator: SphinxTranslator, node: ou_codestyle) -> None:
    """Entry point of the html iframe node."""
    # start the codestyle block
    # TO DO - if we just have a single html file,
    # or HTML text in the admonition, we could just srcdoc it?
    attr: List[str] = [
        f'{k}="{node[k]}"' for k in SUPPORTED_OPTIONS if k in node and node[k]
    ]
    attr.append('name="expandable-code-iframe"')
    html: str = f"<iframe {' '.join(attr)}>"
    # TO DO - this is currently a hack
    html = html.replace("_tmp/", "./")
    translator.body.append(html)


def depart_ou_codestyle_html(translator: SphinxTranslator, node: ou_codestyle) -> None:
    """Exit of the html iframe node."""
    translator.body.append("</iframe>")


def visit_ou_codestyle_unsupported(
    translator: SphinxTranslator, node: ou_codestyle
) -> None:
    """Entry point of the ignored codestyle node."""
    logger.warning(f"codestyle {node['src']}: unsupported output format (node skipped)")
    raise nodes.SkipNode


def setup(app: Sphinx) -> Dict[str, bool]:
    """Add codestyle node and parameters to the Sphinx builder."""
    # app.add_config_value("codestyle_enforce_extra_source", False, "html")
    app.add_node(
        ou_codestyle,
        html=(visit_ou_codestyle_html, depart_ou_codestyle_html),
        epub=(visit_ou_codestyle_unsupported, None),
        latex=(visit_ou_codestyle_unsupported, None),
        man=(visit_ou_codestyle_unsupported, None),
        texinfo=(visit_ou_codestyle_unsupported, None),
        text=(visit_ou_codestyle_unsupported, None),
    )
    app.add_directive("ou-codestyle", codestyle)

    # Pass in the stub filename used in static/js/STUB.js etc
    handle_css_js_assets(app, "ou_codestyle")

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
