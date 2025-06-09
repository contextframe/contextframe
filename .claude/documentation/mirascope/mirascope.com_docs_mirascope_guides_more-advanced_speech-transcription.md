---
url: "https://mirascope.com/docs/mirascope/guides/more-advanced/speech-transcription"
title: "Transcribing Speech | Mirascope"
---

# Transcribing Speech [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/speech-transcription\#transcribing-speech)

In this recipe, we go over how to transcribe the speech from an audio file using Gemini 1.5 Flash’s audio capabilities.

Mirascope Concepts Used

Background

LLMs have significantly advanced speech transcription beyond traditional machine learning techniques, by improved handling of diverse accents and languages, and the ability to incorporate context for more precise transcriptions. Additionally, LLMs can leverage feedback loops to continuously improve their performance and correct errors through simple prompting.

## Setup [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/speech-transcription\#setup)

Let's start by installing Mirascope and its dependencies:

```
!pip install "mirascope[gemini]"
```

```
import os

os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Transcribing Speech using Gemini [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/speech-transcription\#transcribing-speech-using-gemini)

With Gemini’s multimodal capabilities, audio input is treated just like text input, which means we can use it as context to ask questions. We will use an audio clip provided by Google of [a countdown of the Apollo Launch](https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3). Note that if you use your own URL, Gemini currently has a byte limit of `20971520` when not using their file system.

Since we can treat the audio like any other text context, we can create a transcription simply by inserting the audio into the prompt and asking for a transcription:

```
import os

from google.generativeai import configure
from mirascope.core import gemini, prompt_template

configure(api_key=os.environ["GOOGLE_API_KEY"])

apollo_url = "https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3"

@gemini.call(model="gemini-1.5-flash")
@prompt_template(
    """
    Transcribe the content of this speech:
    {url:audio}
    """
)
def transcribe_speech_from_url(url: str): ...

response = transcribe_speech_from_url(apollo_url)

print(response)
```

10 9 8 We have a goal for main engine start. We have a main engine start.

## Tagging audio [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/speech-transcription\#tagging-audio)

We can start by creating a Pydantic Model with the content we want to analyze:

```
from typing import Literal

from pydantic import BaseModel, Field

class AudioTag(BaseModel):
    audio_quality: Literal["Low", "Medium", "High"] = Field(
        ...,
        description="""The quality of the audio file.
        Low - unlistenable due to severe static, distortion, or other imperfections
        Medium - Audible but noticeable imperfections
        High - crystal clear sound""",
    )
    imperfections: list[str] = Field(
        ...,
        description="""A list of the imperfections affecting audio quality, if any.
        Common imperfections are static, distortion, background noise, echo, but include
        all that apply, even if not listed here""",
    )
    description: str = Field(
        ..., description="A one sentence description of the audio content"
    )
    primary_sound: str = Field(
        ...,
        description="""A quick description of the main sound in the audio,
        e.g. `Male Voice`, `Cymbals`, `Rainfall`""",
    )
```

Now we make our call passing in our `AudioTag` into the `response_model` field:

```
@gemini.call(model="gemini-1.5-flash", response_model=AudioTag, json_mode=True)
@prompt_template(
    """
    Analyze this audio file
    {url:audio}

    Give me its audio quality (low, medium, high), a list of its audio flaws (if any),
    a quick description of the content of the audio, and the primary sound in the audio.
    Use the tool call passed into the API call to fill it out.
    """
)
def analyze_audio(url: str): ...

response = analyze_audio(apollo_url)
print(response)
```

audio\_quality='Medium' imperfections=\['Background noise'\] description='A countdown from ten with a male voice announcing "We have a go for main engine start"' primary\_sound='Male Voice'

## Speaker Diarization [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/speech-transcription\#speaker-diarization)

Now let's look at an audio file with multiple people talking. For the purposes of this recipe, I grabbed a snippet from Creative Commons\[ [https://www.youtube.com/watch?v=v0l-u0ZUOSI](https://www.youtube.com/watch?v=v0l-u0ZUOSI)\], around 1:15 in the video and giving Gemini the audio file.

```
with open("YOUR_MP3_HERE", "rb") as file:
    data = file.read()

    @gemini.call(model="gemini-1.5-flash")
    @prompt_template(
        """
        Transcribe the content of this speech adding speaker tags
        for example:
            Person 1: hello
            Person 2: good morning


        {data:audio}
        """
    )
    def transcribe_speech_from_file(data: bytes): ...

    response = transcribe_speech_from_file(data)
    print(response)
```

Additional Real-World Examples

- **Subtitles and Closed Captions**: Automatically generate subtitles for same and different languages for accessibility.
- **Meetings**: Transcribe meetings for future reference or summarization.
- **Voice Assistant**: Transcription is the first step to answering voice requests.

When adapting this recipe to your specific use-case, consider the following:

- Split your audio file into multiple chunks and run the transcription in parallel.
- Compare results with traditional machine learning techniques.
- Experiment with the prompt by giving it some context before asking to transcribe the audio.

Copy as Markdown

#### Provider

OpenAI

#### On this page

Copy as Markdown

#### Provider

OpenAI

#### On this page

## Cookie Consent

We use cookies to track usage and improve the site.

RejectAccept