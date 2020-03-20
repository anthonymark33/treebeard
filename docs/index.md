```eval_rst
.. toctree::
   :caption: Documentation
   :maxdepth: 2
   :hidden:

   Home <https://treebeard.readthedocs.io/>
   project_config
   running
   outputs
   external_integrations
   integrate_your_infra
   cli
   on_prem
   faq

.. toctree::
  :caption: Support
  :maxdepth: 2
  :hidden:

  GitHub <https://github.com/treebeardtech/treebeard>

```

# 🌲 Welcome to Treebeard

Treebeard is an open source library which reproduces Python data science work in the cloud, natively supporting Jupyter Notebooks.

The goal is to allow data scientists to set up continuous integration with minimal changes to their project.

Treebeard works by adding the `treebeard` pip package to your `requirements.txt`, `Pipfile`, or `environment.yml`.

Then placing a `treebeard.yaml` file in the same directory like so:

```yaml
# treebeard.yaml
notebook: run.ipynb
ignore:
  - venv
```

then running `treebeard run`.

We host back-end infrastructure for running your notebook in the cloud, and serving output data.

![](https://treebeard.io/static/slack_integration-ba8ff89332c2e14c928973a841842e5b.png)

## Install Treebeard

Treebeard is available via pip. Please note only Python 3 is supported.

```bash
➜ pip --version
pip 20.0.2 from /Users/.../python3.7/site-packages/pip (python 3.7)
```

```bash
➜ pip install treebeard
```

## Get started

Authenticate your CLI with our backend infrastructure using your email address.

```bash
➜ treebeard configure --email test@example.com
🔑  Config saved in /Users/project_user/.treebeard
```

You will then need to verify your email address.

Clone our git repo to try the examples

```bash
➜ git clone https://github.com/treebeardtech/treebeard.git
TODO cd examples, run, admin page, pull down file
```

### Running your first example

The entry example shows the basic capabilities of the cloud build service.  
The notebook uses some cloud credentials to call an API, saves an image to an output directory, and calls a separate python script.
`cd examples/hello_treebeard`

We recommend working in a python virtual environment. Ensure your python 3 environment has jupyter and treebeard installed, and then start jupyter in the project directory.
`jupyter notebook`

Open `main.ipynb` and check out the examples. When you're ready, return to the command line and instruct treebeard to build the project on the cloud with:
`treebeard run`

### Examples

There are several example projects in the `examples` folder.

The `reddit_tracker` example shows a notebook that calls the Reddit API using saved credentials, extracts the most commonly mentioned names from recent submissions and saves charts showing those common names. This is then run daily, and the images can then be served through a browser extension. [This blog]("https://towardsdatascience.com/how-to-track-sentiment-on-reddit-with-python-and-a-chrome-extension-a623d63e3a1d?gi=90de4fb3934a") goes into more detail.

## Join the community

Stay in touch with us via [Github](https://github.com/treebeardtech/treebeard) and our [email newsletter](https://treebeard.io/contact)
