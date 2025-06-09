---
url: "https://lancedb.github.io/lance/tokenizer.html"
title: "Tokenizers - Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/tokenizer.html#language-models-of-jieba)

# Tokenizers [¶](https://lancedb.github.io/lance/tokenizer.html\#tokenizers "Link to this heading")

Currently, Lance has built-in support for Jieba and Lindera. However, it doesn’t come with its own language models.
If tokenization is needed, you can download language models by yourself.
You can specify the location where the language models are stored by setting the environment variable LANCE\_LANGUAGE\_MODEL\_HOME.
If it’s not set, the default value is

```
${system data directory}/lance/language_models

```

It also supports configuring user dictionaries,
which makes it convenient for users to expand their own dictionaries without retraining the language models.

## Language Models of Jieba [¶](https://lancedb.github.io/lance/tokenizer.html\#language-models-of-jieba "Link to this heading")

### Downloading the Model [¶](https://lancedb.github.io/lance/tokenizer.html\#downloading-the-model "Link to this heading")

```
python -m lance.download jieba

```

The language model is stored by default in ${LANCE\_LANGUAGE\_MODEL\_HOME}/jieba/default.

### Using the Model [¶](https://lancedb.github.io/lance/tokenizer.html\#using-the-model "Link to this heading")

### User Dictionaries [¶](https://lancedb.github.io/lance/tokenizer.html\#user-dictionaries "Link to this heading")

Create a file named config.json in the root directory of the current model.

```
{
    "main": "dict.txt",
    "users": ["path/to/user/dict.txt"]
}

```

- The “main” field is optional. If not filled, the default is “dict.txt”.

- “users” is the path of the user dictionary. For the format of the user dictionary, please refer to [https://github.com/messense/jieba-rs/blob/main/src/data/dict.txt](https://github.com/messense/jieba-rs/blob/main/src/data/dict.txt).


## Language Models of Lindera [¶](https://lancedb.github.io/lance/tokenizer.html\#language-models-of-lindera "Link to this heading")

### Downloading the Model [¶](https://lancedb.github.io/lance/tokenizer.html\#id1 "Link to this heading")

```
python -m lance.download lindera -l [ipadic|ko-dic|unidic]

```

Note that the language models of Lindera need to be compiled. Please install lindera-cli first. For detailed steps, please refer to [https://github.com/lindera/lindera/tree/main/lindera-cli](https://github.com/lindera/lindera/tree/main/lindera-cli).

The language model is stored by default in ${LANCE\_LANGUAGE\_MODEL\_HOME}/lindera/\[ipadic\|ko-dic\|unidic\]

### Using the Model [¶](https://lancedb.github.io/lance/tokenizer.html\#id2 "Link to this heading")

```
ds.create_scalar_index("text", "INVERTED", base_tokenizer="lindera/ipadic")

```

### User Dictionaries [¶](https://lancedb.github.io/lance/tokenizer.html\#id3 "Link to this heading")

Create a file named config.json in the root directory of the current model.

- The “main” field is optional. If not filled, the default is the “main” directory.

- “user” is the path of the user dictionary. The user dictionary can be passed as a CSV file or as a binary file compiled by lindera-cli.

- The “user\_kind” field can be left blank if the user dictionary is in binary format. If it’s in CSV format, you need to specify the type of the language model.


## Create your own language model [¶](https://lancedb.github.io/lance/tokenizer.html\#create-your-own-language-model "Link to this heading")

Put your language model into LANCE\_LANGUAGE\_MODEL\_HOME.