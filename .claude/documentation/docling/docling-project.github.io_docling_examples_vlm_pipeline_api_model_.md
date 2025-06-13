---
url: "https://docling-project.github.io/docling/examples/vlm_pipeline_api_model/"
title: "VLM pipeline with remote model - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/vlm_pipeline_api_model/#example-of-apivlmoptions-definitions)

# VLM pipeline with remote model

In \[ \]:

Copied!

```
import logging
import os
from pathlib import Path

```

import logging
import os
from pathlib import Path

In \[ \]:

Copied!

```
import requests
from dotenv import load_dotenv

```

import requests
from dotenv import load\_dotenv

In \[ \]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
VlmPipelineOptions,
)
from docling.datamodel.pipeline\_options\_vlm\_model import ApiVlmOptions, ResponseFormat
from docling.document\_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm\_pipeline import VlmPipeline

## Example of ApiVlmOptions definitions [¶](https://docling-project.github.io/docling/examples/vlm_pipeline_api_model/\#example-of-apivlmoptions-definitions)

### Using LM Studio [¶](https://docling-project.github.io/docling/examples/vlm_pipeline_api_model/\#using-lm-studio)

In \[ \]:

Copied!

```
def lms_vlm_options(model: str, prompt: str, format: ResponseFormat):
    options = ApiVlmOptions(
        url="http://localhost:1234/v1/chat/completions",  # the default LM Studio
        params=dict(
            model=model,
        ),
        prompt=prompt,
        timeout=90,
        scale=1.0,
        response_format=format,
    )
    return options

```

def lms\_vlm\_options(model: str, prompt: str, format: ResponseFormat):
options = ApiVlmOptions(
url="http://localhost:1234/v1/chat/completions", # the default LM Studio
params=dict(
model=model,
),
prompt=prompt,
timeout=90,
scale=1.0,
response\_format=format,
)
return options

### Using Ollama [¶](https://docling-project.github.io/docling/examples/vlm_pipeline_api_model/\#using-ollama)

In \[ \]:

Copied!

```
def ollama_vlm_options(model: str, prompt: str):
    options = ApiVlmOptions(
        url="http://localhost:11434/v1/chat/completions",  # the default Ollama endpoint
        params=dict(
            model=model,
        ),
        prompt=prompt,
        timeout=90,
        scale=1.0,
        response_format=ResponseFormat.MARKDOWN,
    )
    return options

```

def ollama\_vlm\_options(model: str, prompt: str):
options = ApiVlmOptions(
url="http://localhost:11434/v1/chat/completions", # the default Ollama endpoint
params=dict(
model=model,
),
prompt=prompt,
timeout=90,
scale=1.0,
response\_format=ResponseFormat.MARKDOWN,
)
return options

### Using a cloud service like IBM watsonx.ai [¶](https://docling-project.github.io/docling/examples/vlm_pipeline_api_model/\#using-a-cloud-service-like-ibm-watsonxai)

In \[ \]:

Copied!

```
def watsonx_vlm_options(model: str, prompt: str):
    load_dotenv()
    api_key = os.environ.get("WX_API_KEY")
    project_id = os.environ.get("WX_PROJECT_ID")

    def _get_iam_access_token(api_key: str) -> str:
        res = requests.post(
            url="https://iam.cloud.ibm.com/identity/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}",
        )
        res.raise_for_status()
        api_out = res.json()
        print(f"{api_out=}")
        return api_out["access_token"]

    options = ApiVlmOptions(
        url="https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29",
        params=dict(
            model_id=model,
            project_id=project_id,
            parameters=dict(
                max_new_tokens=400,
            ),
        ),
        headers={
            "Authorization": "Bearer " + _get_iam_access_token(api_key=api_key),
        },
        prompt=prompt,
        timeout=60,
        response_format=ResponseFormat.MARKDOWN,
    )
    return options

```

def watsonx\_vlm\_options(model: str, prompt: str):
load\_dotenv()
api\_key = os.environ.get("WX\_API\_KEY")
project\_id = os.environ.get("WX\_PROJECT\_ID")

def \_get\_iam\_access\_token(api\_key: str) -> str:
res = requests.post(
url="https://iam.cloud.ibm.com/identity/token",
headers={
"Content-Type": "application/x-www-form-urlencoded",
},
data=f"grant\_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api\_key}",
)
res.raise\_for\_status()
api\_out = res.json()
print(f"{api\_out=}")
return api\_out\["access\_token"\]

options = ApiVlmOptions(
url="https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29",
params=dict(
model\_id=model,
project\_id=project\_id,
parameters=dict(
max\_new\_tokens=400,
),
),
headers={
"Authorization": "Bearer " + \_get\_iam\_access\_token(api\_key=api\_key),
},
prompt=prompt,
timeout=60,
response\_format=ResponseFormat.MARKDOWN,
)
return options

## Usage and conversion [¶](https://docling-project.github.io/docling/examples/vlm_pipeline_api_model/\#usage-and-conversion)

In \[ \]:

Copied!

```
def main():
    logging.basicConfig(level=logging.INFO)

    # input_doc_path = Path("./tests/data/pdf/2206.01062.pdf")
    input_doc_path = Path("./tests/data/pdf/2305.03393v1-pg9.pdf")

    pipeline_options = VlmPipelineOptions(
        enable_remote_services=True  # <-- this is required!
    )

    # The ApiVlmOptions() allows to interface with APIs supporting
    # the multi-modal chat interface. Here follow a few example on how to configure those.

    # One possibility is self-hosting model, e.g. via LM Studio, Ollama or others.

    # Example using the SmolDocling model with LM Studio:
    # (uncomment the following lines)
    pipeline_options.vlm_options = lms_vlm_options(
        model="smoldocling-256m-preview-mlx-docling-snap",
        prompt="Convert this page to docling.",
        format=ResponseFormat.DOCTAGS,
    )

    # Example using the Granite Vision model with LM Studio:
    # (uncomment the following lines)
    # pipeline_options.vlm_options = lms_vlm_options(
    #     model="granite-vision-3.2-2b",
    #     prompt="OCR the full page to markdown.",
    #     format=ResponseFormat.MARKDOWN,
    # )

    # Example using the Granite Vision model with Ollama:
    # (uncomment the following lines)
    # pipeline_options.vlm_options = ollama_vlm_options(
    #     model="granite3.2-vision:2b",
    #     prompt="OCR the full page to markdown.",
    # )

    # Another possibility is using online services, e.g. watsonx.ai.
    # Using requires setting the env variables WX_API_KEY and WX_PROJECT_ID.
    # (uncomment the following lines)
    # pipeline_options.vlm_options = watsonx_vlm_options(
    #     model="ibm/granite-vision-3-2-2b", prompt="OCR the full page to markdown."
    # )

    # Create the DocumentConverter and launch the conversion.
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                pipeline_cls=VlmPipeline,
            )
        }
    )
    result = doc_converter.convert(input_doc_path)
    print(result.document.export_to_markdown())

```

def main():
logging.basicConfig(level=logging.INFO)

# input\_doc\_path = Path("./tests/data/pdf/2206.01062.pdf")
input\_doc\_path = Path("./tests/data/pdf/2305.03393v1-pg9.pdf")

pipeline\_options = VlmPipelineOptions(
enable\_remote\_services=True # <-- this is required!
)

# The ApiVlmOptions() allows to interface with APIs supporting
# the multi-modal chat interface. Here follow a few example on how to configure those.

# One possibility is self-hosting model, e.g. via LM Studio, Ollama or others.

# Example using the SmolDocling model with LM Studio:
# (uncomment the following lines)
pipeline\_options.vlm\_options = lms\_vlm\_options(
model="smoldocling-256m-preview-mlx-docling-snap",
prompt="Convert this page to docling.",
format=ResponseFormat.DOCTAGS,
)

# Example using the Granite Vision model with LM Studio:
# (uncomment the following lines)
# pipeline\_options.vlm\_options = lms\_vlm\_options(
# model="granite-vision-3.2-2b",
# prompt="OCR the full page to markdown.",
# format=ResponseFormat.MARKDOWN,
# )

# Example using the Granite Vision model with Ollama:
# (uncomment the following lines)
# pipeline\_options.vlm\_options = ollama\_vlm\_options(
# model="granite3.2-vision:2b",
# prompt="OCR the full page to markdown.",
# )

# Another possibility is using online services, e.g. watsonx.ai.
# Using requires setting the env variables WX\_API\_KEY and WX\_PROJECT\_ID.
# (uncomment the following lines)
# pipeline\_options.vlm\_options = watsonx\_vlm\_options(
# model="ibm/granite-vision-3-2-2b", prompt="OCR the full page to markdown."
# )

# Create the DocumentConverter and launch the conversion.
doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
pipeline\_cls=VlmPipeline,
)
}
)
result = doc\_converter.convert(input\_doc\_path)
print(result.document.export\_to\_markdown())

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top