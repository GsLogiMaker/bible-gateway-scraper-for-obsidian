# bible-gateway-scraper-for-obsidian

Uses https://github.com/jgclark/BibleGateway-to-Markdown to download bibles from Bible Gatway and adds obsidian links.

## Installation
After cloning  the repository, install Ruby:
```
sudo apt install ruby
```
Then install the following required Ruby modules:
```
sudo gem install colorize
sudo gem install optparse
sudo gem install clipboard
```

## Usage
After installation, open a terminal in `bible-gateway-scraper-for-obsidian/`. Then run:
```
python3 main.py --version kjv
```
Doing this will download the King James bible into `bible-gateway-scraper-for-obsidian/bin/`. Now your bible is ready for Obsidian!

> Note:
> When downloading other versions, make sure it contains the full list of old and new testament books.
