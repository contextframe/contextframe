---
url: "https://docs.litellm.ai/docs/langchain/"
title: "Using ChatLiteLLM() - Langchain | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/langchain/#__docusaurus_skipToContent_fallback)

On this page

# Using ChatLiteLLM() - Langchain

## Pre-Requisites [​](https://docs.litellm.ai/docs/langchain/\#pre-requisites "Direct link to Pre-Requisites")

```codeBlockLines_e6Vv
!pip install litellm langchain

```

## Quick Start [​](https://docs.litellm.ai/docs/langchain/\#quick-start "Direct link to Quick Start")

- OpenAI
- Anthropic
- Replicate
- Cohere

```codeBlockLines_e6Vv
import os
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['OPENAI_API_KEY'] = ""
chat = ChatLiteLLM(model="gpt-3.5-turbo")
messages = [\
    HumanMessage(\
        content="what model are you"\
    )\
]
chat.invoke(messages)

```

```codeBlockLines_e6Vv
import os
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['ANTHROPIC_API_KEY'] = ""
chat = ChatLiteLLM(model="claude-2", temperature=0.3)
messages = [\
    HumanMessage(\
        content="what model are you"\
    )\
]
chat.invoke(messages)

```

```codeBlockLines_e6Vv
import os
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['REPLICATE_API_TOKEN'] = ""
chat = ChatLiteLLM(model="replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1")
messages = [\
    HumanMessage(\
        content="what model are you?"\
    )\
]
chat.invoke(messages)

```

```codeBlockLines_e6Vv
import os
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['COHERE_API_KEY'] = ""
chat = ChatLiteLLM(model="command-nightly")
messages = [\
    HumanMessage(\
        content="what model are you?"\
    )\
]
chat.invoke(messages)

```

## Use Langchain ChatLiteLLM with MLflow [​](https://docs.litellm.ai/docs/langchain/\#use-langchain-chatlitellm-with-mlflow "Direct link to Use Langchain ChatLiteLLM with MLflow")

MLflow provides open-source observability solution for ChatLiteLLM.

To enable the integration, simply call `mlflow.litellm.autolog()` before in your code. No other setup is necessary.

```codeBlockLines_e6Vv
import mlflow

mlflow.litellm.autolog()

```

Once the auto-tracing is enabled, you can invoke `ChatLiteLLM` and see recorded traces in MLflow.

```codeBlockLines_e6Vv
import os
from langchain.chat_models import ChatLiteLLM

os.environ['OPENAI_API_KEY']="sk-..."

chat = ChatLiteLLM(model="gpt-4o-mini")
chat.invoke("Hi!")

```

## Use Langchain ChatLiteLLM with Lunary [​](https://docs.litellm.ai/docs/langchain/\#use-langchain-chatlitellm-with-lunary "Direct link to Use Langchain ChatLiteLLM with Lunary")

```codeBlockLines_e6Vv
import os
from langchain.chat_models import ChatLiteLLM
from langchain.schema import HumanMessage
import litellm

os.environ["LUNARY_PUBLIC_KEY"] = "" # from https://app.lunary.ai/settings
os.environ['OPENAI_API_KEY']="sk-..."

litellm.success_callback = ["lunary"]
litellm.failure_callback = ["lunary"]

chat = ChatLiteLLM(
  model="gpt-4o"
  messages = [\
    HumanMessage(\
        content="what model are you"\
    )\
]
chat(messages)

```

Get more details [here](https://docs.litellm.ai/docs/observability/lunary_integration)

## Use LangChain ChatLiteLLM + Langfuse [​](https://docs.litellm.ai/docs/langchain/\#use-langchain-chatlitellm--langfuse "Direct link to Use LangChain ChatLiteLLM + Langfuse")

Checkout this section [here](https://docs.litellm.ai/docs/observability/langfuse_integration#use-langchain-chatlitellm--langfuse) for more details on how to integrate Langfuse with ChatLiteLLM.

- [Pre-Requisites](https://docs.litellm.ai/docs/langchain/#pre-requisites)
- [Quick Start](https://docs.litellm.ai/docs/langchain/#quick-start)
- [Use Langchain ChatLiteLLM with MLflow](https://docs.litellm.ai/docs/langchain/#use-langchain-chatlitellm-with-mlflow)
- [Use Langchain ChatLiteLLM with Lunary](https://docs.litellm.ai/docs/langchain/#use-langchain-chatlitellm-with-lunary)
- [Use LangChain ChatLiteLLM + Langfuse](https://docs.litellm.ai/docs/langchain/#use-langchain-chatlitellm--langfuse)