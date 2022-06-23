# Clone Github Repos

## Description
A simple utility that makes it easy to locally clone all of a Github user's repositories.

## Usage instructions
```
usage: clone-github-repos.py [-h] [-t] [-n] [-s] [-j [FILE [FILE ...]]] username

Download all Github repos for a specified user.

positional arguments:
  username              All repos published by this username will be cloned.

optional arguments:
  -h, --help            show this help message and exit
  -t, --testing         Output the git clone commands but don't execute them.
  -n, --no-metadata-save
                        Don't locally save metadata (JSON) files for Github API responses.
  -s, --skip-cwd-check  Use the current working directory for cloning directly into, even if
                        there are apparently unrelated files present.
  -j [FILE [FILE ...]], --json-files [FILE [FILE ...]]
                        Use one or more local json files instead of making API requests.
```
