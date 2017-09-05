# industrial-innovation-crawler

## Getting Started

Make sure that [conda](https://github.com/conda/conda) is installed for managing Python dependencies.

```
brew cask install anaconda  # MacOS
```

Then add the following line to `~/.zshrc`

```
export PATH=/usr/local/anaconda3/bin:$PATH
```

Install all dependencies:
```
conda create -n py3 python=3 anaconda
source activate py3
conda install --yes --file requirements.txt
```

Export the environment:
```
conda env export > requirements.txt
```
