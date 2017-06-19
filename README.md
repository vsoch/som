# SOM

Stanford Open Modules for Python

[Documentation](https://vsoch.github.io/som)

These are basic Python based tools for working with data (likely images and text) on Google Cloud. 
The [base](som/api/base) API module implements a basic token/refresh authentication, and the 
[identifiers](som/api/identifiers) module is an extension of that for the Stanford School of Medicine. 
For complete docs, please see our [documentation](https://vsoch.github.io/som) base and [examples](examples) that coincide with each.


## Installation
For the stable release, install via pip:

```
pip install som
```

For the development version, install from Github:

```
pip install git+git://github.com/vsoch/som.git
```

This module is currently under development, and anything/everything can change. It's currently driving the guts of:

  - [DocFish](https://doc.fish)
  - [WordFish](https://word.fish)
  - [SendIt](https://www.github.com/pydicom/sendit)


## Issues
If you have an issue, or want to request a feature, please do so on our [issues board](https://www.github.com/vsoch/som/issues)
