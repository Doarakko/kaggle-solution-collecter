# Kaggle Solution Collecter
## Requirements
- pipenv
- Kaggle account
- Google Chrome

## Usage
- Download [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver)
Check your chrome version.
```
$ unzip chromedriver_mac64.zip
```

- hoge
```
$ pipenv shell
```
- Download Meta Kaggle
```
$ mkdir input
$ kaggle datasets download -d kaggle/meta-kaggle -p input/
```
Or download from [here](https://www.kaggle.com/kaggle/meta-kaggle).

- Unzip the zip file
```
$ unzip input/meta-kaggle.zip -d input/
```

## Credits
I refer to [this](https://www.kaggle.com/sudalairajkumar/winning-solutions-of-kaggle-competitions) kernel and appreciate [@sudalairajkumar](https://www.kaggle.com/sudalairajkumar).