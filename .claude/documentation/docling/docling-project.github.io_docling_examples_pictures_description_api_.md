---
url: "https://docling-project.github.io/docling/examples/pictures_description_api/"
title: "Annotate picture with remote VLM - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/pictures_description_api/#example-of-picturedescriptionapioptions-definitions)

# Annotate picture with remote VLM

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
from docling_core.types.doc import PictureItem
from dotenv import load_dotenv

```

import requests
from docling\_core.types.doc import PictureItem
from dotenv import load\_dotenv

In \[ \]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
PdfPipelineOptions,
PictureDescriptionApiOptions,
)
from docling.document\_converter import DocumentConverter, PdfFormatOption

## Example of PictureDescriptionApiOptions definitions [¶](https://docling-project.github.io/docling/examples/pictures_description_api/\#example-of-picturedescriptionapioptions-definitions)

### Using vLLM [¶](https://docling-project.github.io/docling/examples/pictures_description_api/\#using-vllm)

Models can be launched via:
$ vllm serve MODEL\_NAME

In \[ \]:

Copied!

```
def vllm_local_options(model: str):
    options = PictureDescriptionApiOptions(
        url="http://localhost:8000/v1/chat/completions",
        params=dict(
            model=model,
            seed=42,
            max_completion_tokens=200,
        ),
        prompt="Describe the image in three sentences. Be consise and accurate.",
        timeout=90,
    )
    return options

```

def vllm\_local\_options(model: str):
options = PictureDescriptionApiOptions(
url="http://localhost:8000/v1/chat/completions",
params=dict(
model=model,
seed=42,
max\_completion\_tokens=200,
),
prompt="Describe the image in three sentences. Be consise and accurate.",
timeout=90,
)
return options

### Using LM Studio [¶](https://docling-project.github.io/docling/examples/pictures_description_api/\#using-lm-studio)

In \[ \]:

Copied!

```
def lms_local_options(model: str):
    options = PictureDescriptionApiOptions(
        url="http://localhost:1234/v1/chat/completions",
        params=dict(
            model=model,
            seed=42,
            max_completion_tokens=200,
        ),
        prompt="Describe the image in three sentences. Be consise and accurate.",
        timeout=90,
    )
    return options

```

def lms\_local\_options(model: str):
options = PictureDescriptionApiOptions(
url="http://localhost:1234/v1/chat/completions",
params=dict(
model=model,
seed=42,
max\_completion\_tokens=200,
),
prompt="Describe the image in three sentences. Be consise and accurate.",
timeout=90,
)
return options

### Using a cloud service like IBM watsonx.ai [¶](https://docling-project.github.io/docling/examples/pictures_description_api/\#using-a-cloud-service-like-ibm-watsonxai)

In \[ \]:

Copied!

```
def watsonx_vlm_options():
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

    options = PictureDescriptionApiOptions(
        url="https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29",
        params=dict(
            model_id="ibm/granite-vision-3-2-2b",
            project_id=project_id,
            parameters=dict(
                max_new_tokens=400,
            ),
        ),
        headers={
            "Authorization": "Bearer " + _get_iam_access_token(api_key=api_key),
        },
        prompt="Describe the image in three sentences. Be consise and accurate.",
        timeout=60,
    )
    return options

```

def watsonx\_vlm\_options():
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

options = PictureDescriptionApiOptions(
url="https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29",
params=dict(
model\_id="ibm/granite-vision-3-2-2b",
project\_id=project\_id,
parameters=dict(
max\_new\_tokens=400,
),
),
headers={
"Authorization": "Bearer " + \_get\_iam\_access\_token(api\_key=api\_key),
},
prompt="Describe the image in three sentences. Be consise and accurate.",
timeout=60,
)
return options

## Usage and conversion [¶](https://docling-project.github.io/docling/examples/pictures_description_api/\#usage-and-conversion)

In \[ \]:

Copied!

```
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/pdf/2206.01062.pdf")

    pipeline_options = PdfPipelineOptions(
        enable_remote_services=True  # <-- this is required!
    )
    pipeline_options.do_picture_description = True

    # The PictureDescriptionApiOptions() allows to interface with APIs supporting
    # the multi-modal chat interface. Here follow a few example on how to configure those.
    #
    # One possibility is self-hosting model, e.g. via VLLM.
    # $ vllm serve MODEL_NAME
    # Then PictureDescriptionApiOptions can point to the localhost endpoint.

    # Example for the Granite Vision model:
    # (uncomment the following lines)
    # pipeline_options.picture_description_options = vllm_local_options(
    #     model="ibm-granite/granite-vision-3.1-2b-preview"
    # )

    # Example for the SmolVLM model:
    # (uncomment the following lines)
    # pipeline_options.picture_description_options = vllm_local_options(
    #     model="HuggingFaceTB/SmolVLM-256M-Instruct"
    # )

    # For using models on LM Studio using the built-in GGUF or MLX runtimes, e.g. the SmolVLM model:
    # (uncomment the following lines)
    pipeline_options.picture_description_options = lms_local_options(
        model="smolvlm-256m-instruct"
    )

    # Another possibility is using online services, e.g. watsonx.ai.
    # Using requires setting the env variables WX_API_KEY and WX_PROJECT_ID.
    # (uncomment the following lines)
    # pipeline_options.picture_description_options = watsonx_vlm_options()

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )
    result = doc_converter.convert(input_doc_path)

    for element, _level in result.document.iterate_items():
        if isinstance(element, PictureItem):
            print(
                f"Picture {element.self_ref}\n"
                f"Caption: {element.caption_text(doc=result.document)}\n"
                f"Annotations: {element.annotations}"
            )

```

def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_path = Path("./tests/data/pdf/2206.01062.pdf")

pipeline\_options = PdfPipelineOptions(
enable\_remote\_services=True # <-- this is required!
)
pipeline\_options.do\_picture\_description = True

# The PictureDescriptionApiOptions() allows to interface with APIs supporting
# the multi-modal chat interface. Here follow a few example on how to configure those.
#
# One possibility is self-hosting model, e.g. via VLLM.
# $ vllm serve MODEL\_NAME
# Then PictureDescriptionApiOptions can point to the localhost endpoint.

# Example for the Granite Vision model:
# (uncomment the following lines)
# pipeline\_options.picture\_description\_options = vllm\_local\_options(
# model="ibm-granite/granite-vision-3.1-2b-preview"
# )

# Example for the SmolVLM model:
# (uncomment the following lines)
# pipeline\_options.picture\_description\_options = vllm\_local\_options(
# model="HuggingFaceTB/SmolVLM-256M-Instruct"
# )

# For using models on LM Studio using the built-in GGUF or MLX runtimes, e.g. the SmolVLM model:
# (uncomment the following lines)
pipeline\_options.picture\_description\_options = lms\_local\_options(
model="smolvlm-256m-instruct"
)

# Another possibility is using online services, e.g. watsonx.ai.
# Using requires setting the env variables WX\_API\_KEY and WX\_PROJECT\_ID.
# (uncomment the following lines)
# pipeline\_options.picture\_description\_options = watsonx\_vlm\_options()

doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
)
}
)
result = doc\_converter.convert(input\_doc\_path)

for element, \_level in result.document.iterate\_items():
if isinstance(element, PictureItem):
print(
f"Picture {element.self\_ref}\\n"
f"Caption: {element.caption\_text(doc=result.document)}\\n"
f"Annotations: {element.annotations}"
)

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top