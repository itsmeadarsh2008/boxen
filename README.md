<div align="center">
    <h1>Boxen</h1>
    <div>
        <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dd/boxen-python">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/boxen-python">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/boxen-python">
        <img alt="GitHub Sponsors" src="https://img.shields.io/github/sponsors/itsmeadarsh2008">
        <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/itsmeadarsh2008/boxen">
    </div>
</div>

<h3 align="center">
    A simple, fast, dependencyless and intuitive library for creating boxes in console 🎁
</h3>
<h2 align="center">Installation</h2>
<p align="center">
    <code>uv pip install boxen-python</code>
</p>

<h2 align="center">Usage</h2>

```python
from boxen import boxen

print(
    boxen(
        "Hello, World!",
        options={
            "padding": 3,
            "borderStyle": "double",
            "borderColor": "red",
            "dimBorder": False,
            "textAlignment": "center",
            "float": "center",
        },
    )
)
# These are only few options, there are many more options available
```


<h2 align="center">Preview (A single image for now, there are several options for customization)</h2>
<table align="center">
    <tr>
        <td>
            <a href="https://ibb.co/GVTHY4F"><img src="https://i.ibb.co/LC5NjXv/image.png" alt="image" border="0"></a>
        </td>
    </tr>
</table>