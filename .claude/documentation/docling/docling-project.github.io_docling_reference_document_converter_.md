---
url: "https://docling-project.github.io/docling/reference/document_converter/"
title: "Document Converter - Docling"
---

[Skip to content](https://docling-project.github.io/docling/reference/document_converter/#document-converter)

# Document converter

This is an automatic generated API reference of the main components of Docling.

## `` document\_converter

Classes:

- **`DocumentConverter`**
–


- **`ConversionResult`**
–


- **`ConversionStatus`**
–


- **`FormatOption`**
–


- **`InputFormat`**
–



A document format supported by document backend parsers.

- **`PdfFormatOption`**
–


- **`ImageFormatOption`**
–


- **`StandardPdfPipeline`**
–


- **`WordFormatOption`**
–


- **`PowerpointFormatOption`**
–


- **`MarkdownFormatOption`**
–


- **`AsciiDocFormatOption`**
–


- **`HTMLFormatOption`**
–


- **`SimplePipeline`**
–



SimpleModelPipeline.


### `` DocumentConverter

```
DocumentConverter(allowed_formats: Optional[List[InputFormat]] = None, format_options: Optional[Dict[InputFormat, FormatOption]] = None)

```

Methods:

- **`convert`**
–


- **`convert_all`**
–


- **`initialize_pipeline`**
–



Initialize the conversion pipeline for the selected format.


Attributes:

- **`allowed_formats`**
–


- **`format_to_options`**
–


- **`initialized_pipelines`**
( `Dict[Tuple[Type[BasePipeline], str], BasePipeline]`)
–



#### `` allowed\_formats`instance-attribute`

```
allowed_formats = allowed_formats if allowed_formats is not None else list(InputFormat)

```

#### `` format\_to\_options`instance-attribute`

```
format_to_options = {format: _get_default_option(format=format) if (custom_option := get(format)) is None else _lG7dekt9j1xmfor format in allowed_formats}

```

#### `` initialized\_pipelines`instance-attribute`

```
initialized_pipelines: Dict[Tuple[Type[BasePipeline], str], BasePipeline] = {}

```

#### `` convert

```
convert(source: Union[Path, str, DocumentStream], headers: Optional[Dict[str, str]] = None, raises_on_error: bool = True, max_num_pages: int = maxsize, max_file_size: int = maxsize, page_range: PageRange = DEFAULT_PAGE_RANGE) -> ConversionResult

```

#### `` convert\_all

```
convert_all(source: Iterable[Union[Path, str, DocumentStream]], headers: Optional[Dict[str, str]] = None, raises_on_error: bool = True, max_num_pages: int = maxsize, max_file_size: int = maxsize, page_range: PageRange = DEFAULT_PAGE_RANGE) -> Iterator[ConversionResult]

```

#### `` initialize\_pipeline

```
initialize_pipeline(format: InputFormat)

```

Initialize the conversion pipeline for the selected format.

### `` ConversionResult

Bases: `BaseModel`

Attributes:

- **`assembled`**
( `AssembledUnit`)
–


- **`confidence`**
( `ConfidenceReport`)
–


- **`document`**
( `DoclingDocument`)
–


- **`errors`**
( `List[ErrorItem]`)
–


- **`input`**
( `InputDocument`)
–


- **`legacy_document`**
–


- **`pages`**
( `List[Page]`)
–


- **`status`**
( `ConversionStatus`)
–


- **`timings`**
( `Dict[str, ProfilingItem]`)
–



#### `` assembled`class-attribute``instance-attribute`

```
assembled: AssembledUnit = AssembledUnit()

```

#### `` confidence`class-attribute``instance-attribute`

```
confidence: ConfidenceReport = Field(default_factory=ConfidenceReport)

```

#### `` document`class-attribute``instance-attribute`

```
document: DoclingDocument = _EMPTY_DOCLING_DOC

```

#### `` errors`class-attribute``instance-attribute`

```
errors: List[ErrorItem] = []

```

#### `` input`instance-attribute`

```
input: InputDocument

```

#### `` legacy\_document`property`

```
legacy_document

```

#### `` pages`class-attribute``instance-attribute`

```
pages: List[Page] = []

```

#### `` status`class-attribute``instance-attribute`

```
status: ConversionStatus = PENDING

```

#### `` timings`class-attribute``instance-attribute`

```
timings: Dict[str, ProfilingItem] = {}

```

### `` ConversionStatus

Bases: `str`, `Enum`

Attributes:

- **`FAILURE`**
–


- **`PARTIAL_SUCCESS`**
–


- **`PENDING`**
–


- **`SKIPPED`**
–


- **`STARTED`**
–


- **`SUCCESS`**
–



#### `` FAILURE`class-attribute``instance-attribute`

```
FAILURE = 'failure'

```

#### `` PARTIAL\_SUCCESS`class-attribute``instance-attribute`

```
PARTIAL_SUCCESS = 'partial_success'

```

#### `` PENDING`class-attribute``instance-attribute`

```
PENDING = 'pending'

```

#### `` SKIPPED`class-attribute``instance-attribute`

```
SKIPPED = 'skipped'

```

#### `` STARTED`class-attribute``instance-attribute`

```
STARTED = 'started'

```

#### `` SUCCESS`class-attribute``instance-attribute`

```
SUCCESS = 'success'

```

### `` FormatOption

Bases: `BaseModel`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type[BasePipeline]`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`instance-attribute`

```
backend: Type[AbstractDocumentBackend]

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`instance-attribute`

```
pipeline_cls: Type[BasePipeline]

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` InputFormat

Bases: `str`, `Enum`

A document format supported by document backend parsers.

Attributes:

- **`ASCIIDOC`**
–


- **`CSV`**
–


- **`DOCX`**
–


- **`HTML`**
–


- **`IMAGE`**
–


- **`JSON_DOCLING`**
–


- **`MD`**
–


- **`PDF`**
–


- **`PPTX`**
–


- **`XLSX`**
–


- **`XML_JATS`**
–


- **`XML_USPTO`**
–



#### `` ASCIIDOC`class-attribute``instance-attribute`

```
ASCIIDOC = 'asciidoc'

```

#### `` CSV`class-attribute``instance-attribute`

```
CSV = 'csv'

```

#### `` DOCX`class-attribute``instance-attribute`

```
DOCX = 'docx'

```

#### `` HTML`class-attribute``instance-attribute`

```
HTML = 'html'

```

#### `` IMAGE`class-attribute``instance-attribute`

```
IMAGE = 'image'

```

#### `` JSON\_DOCLING`class-attribute``instance-attribute`

```
JSON_DOCLING = 'json_docling'

```

#### `` MD`class-attribute``instance-attribute`

```
MD = 'md'

```

#### `` PDF`class-attribute``instance-attribute`

```
PDF = 'pdf'

```

#### `` PPTX`class-attribute``instance-attribute`

```
PPTX = 'pptx'

```

#### `` XLSX`class-attribute``instance-attribute`

```
XLSX = 'xlsx'

```

#### `` XML\_JATS`class-attribute``instance-attribute`

```
XML_JATS = 'xml_jats'

```

#### `` XML\_USPTO`class-attribute``instance-attribute`

```
XML_USPTO = 'xml_uspto'

```

### `` PdfFormatOption

Bases: `FormatOption`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`class-attribute``instance-attribute`

```
backend: Type[AbstractDocumentBackend] = DoclingParseV4DocumentBackend

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`class-attribute``instance-attribute`

```
pipeline_cls: Type = StandardPdfPipeline

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` ImageFormatOption

Bases: `FormatOption`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`class-attribute``instance-attribute`

```
backend: Type[AbstractDocumentBackend] = DoclingParseV4DocumentBackend

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`class-attribute``instance-attribute`

```
pipeline_cls: Type = StandardPdfPipeline

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` StandardPdfPipeline

```
StandardPdfPipeline(pipeline_options: PdfPipelineOptions)

```

Bases: `PaginatedPipeline`

Methods:

- **`download_models_hf`**
–


- **`execute`**
–


- **`get_default_options`**
–


- **`get_ocr_model`**
–


- **`get_picture_description_model`**
–


- **`initialize_page`**
–


- **`is_backend_supported`**
–



Attributes:

- **`build_pipe`**
–


- **`enrichment_pipe`**
–


- **`keep_backend`**
–


- **`keep_images`**
–


- **`pipeline_options`**
( `PdfPipelineOptions`)
–


- **`reading_order_model`**
–



#### `` build\_pipe`instance-attribute`

```
build_pipe = [PagePreprocessingModel(options=PagePreprocessingOptions(images_scale=images_scale, create_parsed_page=generate_parsed_pages)), ocr_model, LayoutModel(artifacts_path=artifacts_path, accelerator_options=accelerator_options), TableStructureModel(enabled=do_table_structure, artifacts_path=artifacts_path, options=table_structure_options, accelerator_options=accelerator_options), PageAssembleModel(options=PageAssembleOptions())]

```

#### `` enrichment\_pipe`instance-attribute`

```
enrichment_pipe = [CodeFormulaModel(enabled=do_code_enrichment or do_formula_enrichment, artifacts_path=artifacts_path, options=CodeFormulaModelOptions(do_code_enrichment=do_code_enrichment, do_formula_enrichment=do_formula_enrichment), accelerator_options=accelerator_options), DocumentPictureClassifier(enabled=do_picture_classification, artifacts_path=artifacts_path, options=DocumentPictureClassifierOptions(), accelerator_options=accelerator_options), picture_description_model]

```

#### `` keep\_backend`instance-attribute`

```
keep_backend = True

```

#### `` keep\_images`instance-attribute`

```
keep_images = generate_page_images or generate_picture_images or generate_table_images

```

#### `` pipeline\_options`instance-attribute`

```
pipeline_options: PdfPipelineOptions

```

#### `` reading\_order\_model`instance-attribute`

```
reading_order_model = ReadingOrderModel(options=ReadingOrderOptions())

```

#### `` download\_models\_hf`staticmethod`

```
download_models_hf(local_dir: Optional[Path] = None, force: bool = False) -> Path

```

#### `` execute

```
execute(in_doc: InputDocument, raises_on_error: bool) -> ConversionResult

```

#### `` get\_default\_options`classmethod`

```
get_default_options() -> PdfPipelineOptions

```

#### `` get\_ocr\_model

```
get_ocr_model(artifacts_path: Optional[Path] = None) -> BaseOcrModel

```

#### `` get\_picture\_description\_model

```
get_picture_description_model(artifacts_path: Optional[Path] = None) -> Optional[PictureDescriptionBaseModel]

```

#### `` initialize\_page

```
initialize_page(conv_res: ConversionResult, page: Page) -> Page

```

#### `` is\_backend\_supported`classmethod`

```
is_backend_supported(backend: AbstractDocumentBackend)

```

### `` WordFormatOption

Bases: `FormatOption`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`class-attribute``instance-attribute`

```
backend: Type[AbstractDocumentBackend] = MsWordDocumentBackend

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`class-attribute``instance-attribute`

```
pipeline_cls: Type = SimplePipeline

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` PowerpointFormatOption

Bases: `FormatOption`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`class-attribute``instance-attribute`

```
backend: Type[AbstractDocumentBackend] = MsPowerpointDocumentBackend

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`class-attribute``instance-attribute`

```
pipeline_cls: Type = SimplePipeline

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` MarkdownFormatOption

Bases: `FormatOption`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`class-attribute``instance-attribute`

```
backend: Type[AbstractDocumentBackend] = MarkdownDocumentBackend

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`class-attribute``instance-attribute`

```
pipeline_cls: Type = SimplePipeline

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` AsciiDocFormatOption

Bases: `FormatOption`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`class-attribute``instance-attribute`

```
backend: Type[AbstractDocumentBackend] = AsciiDocBackend

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`class-attribute``instance-attribute`

```
pipeline_cls: Type = SimplePipeline

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` HTMLFormatOption

Bases: `FormatOption`

Methods:

- **`set_optional_field_default`**
–



Attributes:

- **`backend`**
( `Type[AbstractDocumentBackend]`)
–


- **`model_config`**
–


- **`pipeline_cls`**
( `Type`)
–


- **`pipeline_options`**
( `Optional[PipelineOptions]`)
–



#### `` backend`class-attribute``instance-attribute`

```
backend: Type[AbstractDocumentBackend] = HTMLDocumentBackend

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(arbitrary_types_allowed=True)

```

#### `` pipeline\_cls`class-attribute``instance-attribute`

```
pipeline_cls: Type = SimplePipeline

```

#### `` pipeline\_options`class-attribute``instance-attribute`

```
pipeline_options: Optional[PipelineOptions] = None

```

#### `` set\_optional\_field\_default

```
set_optional_field_default() -> FormatOption

```

### `` SimplePipeline

```
SimplePipeline(pipeline_options: PipelineOptions)

```

Bases: `BasePipeline`

SimpleModelPipeline.

This class is used at the moment for formats / backends
which produce straight DoclingDocument output.

Methods:

- **`execute`**
–


- **`get_default_options`**
–


- **`is_backend_supported`**
–



Attributes:

- **`build_pipe`**
( `List[Callable]`)
–


- **`enrichment_pipe`**
( `List[GenericEnrichmentModel[Any]]`)
–


- **`keep_images`**
–


- **`pipeline_options`**
–



#### `` build\_pipe`instance-attribute`

```
build_pipe: List[Callable] = []

```

#### `` enrichment\_pipe`instance-attribute`

```
enrichment_pipe: List[GenericEnrichmentModel[Any]] = []

```

#### `` keep\_images`instance-attribute`

```
keep_images = False

```

#### `` pipeline\_options`instance-attribute`

```
pipeline_options = pipeline_options

```

#### `` execute

```
execute(in_doc: InputDocument, raises_on_error: bool) -> ConversionResult

```

#### `` get\_default\_options`classmethod`

```
get_default_options() -> PipelineOptions

```

#### `` is\_backend\_supported`classmethod`

```
is_backend_supported(backend: AbstractDocumentBackend)

```

Back to top