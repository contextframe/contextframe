---
url: "https://docling-project.github.io/docling/reference/pipeline_options/"
title: "Pipeline options - Docling"
---

[Skip to content](https://docling-project.github.io/docling/reference/pipeline_options/#pipeline-options)

# Pipeline options

Pipeline options allow to customize the execution of the models during the conversion pipeline.
This includes options for the OCR engines, the table model as well as enrichment options which
can be enabled with `do_xyz = True`.

This is an automatic generated API reference of the all the pipeline options available in Docling.

## `` pipeline\_options

Classes:

- **`BaseOptions`**
–



Base class for options.

- **`EasyOcrOptions`**
–



Options for the EasyOCR engine.

- **`OcrEngine`**
–



Enum of valid OCR engines.

- **`OcrMacOptions`**
–



Options for the Mac OCR engine.

- **`OcrOptions`**
–



OCR options.

- **`PaginatedPipelineOptions`**
–


- **`PdfBackend`**
–



Enum of valid PDF backends.

- **`PdfPipeline`**
–


- **`PdfPipelineOptions`**
–



Options for the PDF pipeline.

- **`PictureDescriptionApiOptions`**
–


- **`PictureDescriptionBaseOptions`**
–


- **`PictureDescriptionVlmOptions`**
–


- **`PipelineOptions`**
–



Base pipeline options.

- **`RapidOcrOptions`**
–



Options for the RapidOCR engine.

- **`TableFormerMode`**
–



Modes for the TableFormer model.

- **`TableStructureOptions`**
–



Options for the table structure.

- **`TesseractCliOcrOptions`**
–



Options for the TesseractCli engine.

- **`TesseractOcrOptions`**
–



Options for the Tesseract engine.

- **`VlmPipelineOptions`**
–



Attributes:

- **`granite_picture_description`**
–


- **`smolvlm_picture_description`**
–



### `` granite\_picture\_description`module-attribute`

```
granite_picture_description = PictureDescriptionVlmOptions(repo_id='ibm-granite/granite-vision-3.1-2b-preview', prompt='What is shown in this image?')

```

### `` smolvlm\_picture\_description`module-attribute`

```
smolvlm_picture_description = PictureDescriptionVlmOptions(repo_id='HuggingFaceTB/SmolVLM-256M-Instruct')

```

### `` BaseOptions

Bases: `BaseModel`

Base class for options.

Attributes:

- **`kind`**
( `str`)
–



#### `` kind`class-attribute`

```
kind: str

```

### `` EasyOcrOptions

Bases: `OcrOptions`

Options for the EasyOCR engine.

Attributes:

- **`bitmap_area_threshold`**
( `float`)
–


- **`confidence_threshold`**
( `float`)
–


- **`download_enabled`**
( `bool`)
–


- **`force_full_page_ocr`**
( `bool`)
–


- **`kind`**
( `Literal['easyocr']`)
–


- **`lang`**
( `List[str]`)
–


- **`model_config`**
–


- **`model_storage_directory`**
( `Optional[str]`)
–


- **`recog_network`**
( `Optional[str]`)
–


- **`use_gpu`**
( `Optional[bool]`)
–



#### `` bitmap\_area\_threshold`class-attribute``instance-attribute`

```
bitmap_area_threshold: float = 0.05

```

#### `` confidence\_threshold`class-attribute``instance-attribute`

```
confidence_threshold: float = 0.5

```

#### `` download\_enabled`class-attribute``instance-attribute`

```
download_enabled: bool = True

```

#### `` force\_full\_page\_ocr`class-attribute``instance-attribute`

```
force_full_page_ocr: bool = False

```

#### `` kind`class-attribute`

```
kind: Literal['easyocr'] = 'easyocr'

```

#### `` lang`class-attribute``instance-attribute`

```
lang: List[str] = ['fr', 'de', 'es', 'en']

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(extra='forbid', protected_namespaces=())

```

#### `` model\_storage\_directory`class-attribute``instance-attribute`

```
model_storage_directory: Optional[str] = None

```

#### `` recog\_network`class-attribute``instance-attribute`

```
recog_network: Optional[str] = 'standard'

```

#### `` use\_gpu`class-attribute``instance-attribute`

```
use_gpu: Optional[bool] = None

```

### `` OcrEngine

Bases: `str`, `Enum`

Enum of valid OCR engines.

Attributes:

- **`EASYOCR`**
–


- **`OCRMAC`**
–


- **`RAPIDOCR`**
–


- **`TESSERACT`**
–


- **`TESSERACT_CLI`**
–



#### `` EASYOCR`class-attribute``instance-attribute`

```
EASYOCR = 'easyocr'

```

#### `` OCRMAC`class-attribute``instance-attribute`

```
OCRMAC = 'ocrmac'

```

#### `` RAPIDOCR`class-attribute``instance-attribute`

```
RAPIDOCR = 'rapidocr'

```

#### `` TESSERACT`class-attribute``instance-attribute`

```
TESSERACT = 'tesseract'

```

#### `` TESSERACT\_CLI`class-attribute``instance-attribute`

```
TESSERACT_CLI = 'tesseract_cli'

```

### `` OcrMacOptions

Bases: `OcrOptions`

Options for the Mac OCR engine.

Attributes:

- **`bitmap_area_threshold`**
( `float`)
–


- **`force_full_page_ocr`**
( `bool`)
–


- **`framework`**
( `str`)
–


- **`kind`**
( `Literal['ocrmac']`)
–


- **`lang`**
( `List[str]`)
–


- **`model_config`**
–


- **`recognition`**
( `str`)
–



#### `` bitmap\_area\_threshold`class-attribute``instance-attribute`

```
bitmap_area_threshold: float = 0.05

```

#### `` force\_full\_page\_ocr`class-attribute``instance-attribute`

```
force_full_page_ocr: bool = False

```

#### `` framework`class-attribute``instance-attribute`

```
framework: str = 'vision'

```

#### `` kind`class-attribute`

```
kind: Literal['ocrmac'] = 'ocrmac'

```

#### `` lang`class-attribute``instance-attribute`

```
lang: List[str] = ['fr-FR', 'de-DE', 'es-ES', 'en-US']

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(extra='forbid')

```

#### `` recognition`class-attribute``instance-attribute`

```
recognition: str = 'accurate'

```

### `` OcrOptions

Bases: `BaseOptions`

OCR options.

Attributes:

- **`bitmap_area_threshold`**
( `float`)
–


- **`force_full_page_ocr`**
( `bool`)
–


- **`kind`**
( `str`)
–


- **`lang`**
( `List[str]`)
–



#### `` bitmap\_area\_threshold`class-attribute``instance-attribute`

```
bitmap_area_threshold: float = 0.05

```

#### `` force\_full\_page\_ocr`class-attribute``instance-attribute`

```
force_full_page_ocr: bool = False

```

#### `` kind`class-attribute`

```
kind: str

```

#### `` lang`instance-attribute`

```
lang: List[str]

```

### `` PaginatedPipelineOptions

Bases: `PipelineOptions`

Attributes:

- **`accelerator_options`**
( `AcceleratorOptions`)
–


- **`allow_external_plugins`**
( `bool`)
–


- **`artifacts_path`**
( `Optional[Union[Path, str]]`)
–


- **`create_legacy_output`**
( `bool`)
–


- **`document_timeout`**
( `Optional[float]`)
–


- **`enable_remote_services`**
( `bool`)
–


- **`generate_page_images`**
( `bool`)
–


- **`generate_picture_images`**
( `bool`)
–


- **`images_scale`**
( `float`)
–



#### `` accelerator\_options`class-attribute``instance-attribute`

```
accelerator_options: AcceleratorOptions = AcceleratorOptions()

```

#### `` allow\_external\_plugins`class-attribute``instance-attribute`

```
allow_external_plugins: bool = False

```

#### `` artifacts\_path`class-attribute``instance-attribute`

```
artifacts_path: Optional[Union[Path, str]] = None

```

#### `` create\_legacy\_output`class-attribute``instance-attribute`

```
create_legacy_output: bool = True

```

#### `` document\_timeout`class-attribute``instance-attribute`

```
document_timeout: Optional[float] = None

```

#### `` enable\_remote\_services`class-attribute``instance-attribute`

```
enable_remote_services: bool = False

```

#### `` generate\_page\_images`class-attribute``instance-attribute`

```
generate_page_images: bool = False

```

#### `` generate\_picture\_images`class-attribute``instance-attribute`

```
generate_picture_images: bool = False

```

#### `` images\_scale`class-attribute``instance-attribute`

```
images_scale: float = 1.0

```

### `` PdfBackend

Bases: `str`, `Enum`

Enum of valid PDF backends.

Attributes:

- **`DLPARSE_V1`**
–


- **`DLPARSE_V2`**
–


- **`DLPARSE_V4`**
–


- **`PYPDFIUM2`**
–



#### `` DLPARSE\_V1`class-attribute``instance-attribute`

```
DLPARSE_V1 = 'dlparse_v1'

```

#### `` DLPARSE\_V2`class-attribute``instance-attribute`

```
DLPARSE_V2 = 'dlparse_v2'

```

#### `` DLPARSE\_V4`class-attribute``instance-attribute`

```
DLPARSE_V4 = 'dlparse_v4'

```

#### `` PYPDFIUM2`class-attribute``instance-attribute`

```
PYPDFIUM2 = 'pypdfium2'

```

### `` PdfPipeline

Bases: `str`, `Enum`

Attributes:

- **`STANDARD`**
–


- **`VLM`**
–



#### `` STANDARD`class-attribute``instance-attribute`

```
STANDARD = 'standard'

```

#### `` VLM`class-attribute``instance-attribute`

```
VLM = 'vlm'

```

### `` PdfPipelineOptions

Bases: `PaginatedPipelineOptions`

Options for the PDF pipeline.

Attributes:

- **`accelerator_options`**
( `AcceleratorOptions`)
–


- **`allow_external_plugins`**
( `bool`)
–


- **`artifacts_path`**
( `Optional[Union[Path, str]]`)
–


- **`create_legacy_output`**
( `bool`)
–


- **`do_code_enrichment`**
( `bool`)
–


- **`do_formula_enrichment`**
( `bool`)
–


- **`do_ocr`**
( `bool`)
–


- **`do_picture_classification`**
( `bool`)
–


- **`do_picture_description`**
( `bool`)
–


- **`do_table_structure`**
( `bool`)
–


- **`document_timeout`**
( `Optional[float]`)
–


- **`enable_remote_services`**
( `bool`)
–


- **`force_backend_text`**
( `bool`)
–


- **`generate_page_images`**
( `bool`)
–


- **`generate_parsed_pages`**
( `bool`)
–


- **`generate_picture_images`**
( `bool`)
–


- **`generate_table_images`**
( `bool`)
–


- **`images_scale`**
( `float`)
–


- **`ocr_options`**
( `OcrOptions`)
–


- **`picture_description_options`**
( `PictureDescriptionBaseOptions`)
–


- **`table_structure_options`**
( `TableStructureOptions`)
–



#### `` accelerator\_options`class-attribute``instance-attribute`

```
accelerator_options: AcceleratorOptions = AcceleratorOptions()

```

#### `` allow\_external\_plugins`class-attribute``instance-attribute`

```
allow_external_plugins: bool = False

```

#### `` artifacts\_path`class-attribute``instance-attribute`

```
artifacts_path: Optional[Union[Path, str]] = None

```

#### `` create\_legacy\_output`class-attribute``instance-attribute`

```
create_legacy_output: bool = True

```

#### `` do\_code\_enrichment`class-attribute``instance-attribute`

```
do_code_enrichment: bool = False

```

#### `` do\_formula\_enrichment`class-attribute``instance-attribute`

```
do_formula_enrichment: bool = False

```

#### `` do\_ocr`class-attribute``instance-attribute`

```
do_ocr: bool = True

```

#### `` do\_picture\_classification`class-attribute``instance-attribute`

```
do_picture_classification: bool = False

```

#### `` do\_picture\_description`class-attribute``instance-attribute`

```
do_picture_description: bool = False

```

#### `` do\_table\_structure`class-attribute``instance-attribute`

```
do_table_structure: bool = True

```

#### `` document\_timeout`class-attribute``instance-attribute`

```
document_timeout: Optional[float] = None

```

#### `` enable\_remote\_services`class-attribute``instance-attribute`

```
enable_remote_services: bool = False

```

#### `` force\_backend\_text`class-attribute``instance-attribute`

```
force_backend_text: bool = False

```

#### `` generate\_page\_images`class-attribute``instance-attribute`

```
generate_page_images: bool = False

```

#### `` generate\_parsed\_pages`class-attribute``instance-attribute`

```
generate_parsed_pages: bool = False

```

#### `` generate\_picture\_images`class-attribute``instance-attribute`

```
generate_picture_images: bool = False

```

#### `` generate\_table\_images`class-attribute``instance-attribute`

```
generate_table_images: bool = Field(default=False, deprecated='Field `generate_table_images` is deprecated. To obtain table images, set `PdfPipelineOptions.generate_page_images = True` before conversion and then use the `TableItem.get_image` function.')

```

#### `` images\_scale`class-attribute``instance-attribute`

```
images_scale: float = 1.0

```

#### `` ocr\_options`class-attribute``instance-attribute`

```
ocr_options: OcrOptions = EasyOcrOptions()

```

#### `` picture\_description\_options`class-attribute``instance-attribute`

```
picture_description_options: PictureDescriptionBaseOptions = smolvlm_picture_description

```

#### `` table\_structure\_options`class-attribute``instance-attribute`

```
table_structure_options: TableStructureOptions = TableStructureOptions()

```

### `` PictureDescriptionApiOptions

Bases: `PictureDescriptionBaseOptions`

Attributes:

- **`batch_size`**
( `int`)
–


- **`concurrency`**
( `int`)
–


- **`headers`**
( `Dict[str, str]`)
–


- **`kind`**
( `Literal['api']`)
–


- **`params`**
( `Dict[str, Any]`)
–


- **`picture_area_threshold`**
( `float`)
–


- **`prompt`**
( `str`)
–


- **`provenance`**
( `str`)
–


- **`scale`**
( `float`)
–


- **`timeout`**
( `float`)
–


- **`url`**
( `AnyUrl`)
–



#### `` batch\_size`class-attribute``instance-attribute`

```
batch_size: int = 8

```

#### `` concurrency`class-attribute``instance-attribute`

```
concurrency: int = 1

```

#### `` headers`class-attribute``instance-attribute`

```
headers: Dict[str, str] = {}

```

#### `` kind`class-attribute`

```
kind: Literal['api'] = 'api'

```

#### `` params`class-attribute``instance-attribute`

```
params: Dict[str, Any] = {}

```

#### `` picture\_area\_threshold`class-attribute``instance-attribute`

```
picture_area_threshold: float = 0.05

```

#### `` prompt`class-attribute``instance-attribute`

```
prompt: str = 'Describe this image in a few sentences.'

```

#### `` provenance`class-attribute``instance-attribute`

```
provenance: str = ''

```

#### `` scale`class-attribute``instance-attribute`

```
scale: float = 2

```

#### `` timeout`class-attribute``instance-attribute`

```
timeout: float = 20

```

#### `` url`class-attribute``instance-attribute`

```
url: AnyUrl = AnyUrl('http://localhost:8000/v1/chat/completions')

```

### `` PictureDescriptionBaseOptions

Bases: `BaseOptions`

Attributes:

- **`batch_size`**
( `int`)
–


- **`kind`**
( `str`)
–


- **`picture_area_threshold`**
( `float`)
–


- **`scale`**
( `float`)
–



#### `` batch\_size`class-attribute``instance-attribute`

```
batch_size: int = 8

```

#### `` kind`class-attribute`

```
kind: str

```

#### `` picture\_area\_threshold`class-attribute``instance-attribute`

```
picture_area_threshold: float = 0.05

```

#### `` scale`class-attribute``instance-attribute`

```
scale: float = 2

```

### `` PictureDescriptionVlmOptions

Bases: `PictureDescriptionBaseOptions`

Attributes:

- **`batch_size`**
( `int`)
–


- **`generation_config`**
( `Dict[str, Any]`)
–


- **`kind`**
( `Literal['vlm']`)
–


- **`picture_area_threshold`**
( `float`)
–


- **`prompt`**
( `str`)
–


- **`repo_cache_folder`**
( `str`)
–


- **`repo_id`**
( `str`)
–


- **`scale`**
( `float`)
–



#### `` batch\_size`class-attribute``instance-attribute`

```
batch_size: int = 8

```

#### `` generation\_config`class-attribute``instance-attribute`

```
generation_config: Dict[str, Any] = dict(max_new_tokens=200, do_sample=False)

```

#### `` kind`class-attribute`

```
kind: Literal['vlm'] = 'vlm'

```

#### `` picture\_area\_threshold`class-attribute``instance-attribute`

```
picture_area_threshold: float = 0.05

```

#### `` prompt`class-attribute``instance-attribute`

```
prompt: str = 'Describe this image in a few sentences.'

```

#### `` repo\_cache\_folder`property`

```
repo_cache_folder: str

```

#### `` repo\_id`instance-attribute`

```
repo_id: str

```

#### `` scale`class-attribute``instance-attribute`

```
scale: float = 2

```

### `` PipelineOptions

Bases: `BaseModel`

Base pipeline options.

Attributes:

- **`accelerator_options`**
( `AcceleratorOptions`)
–


- **`allow_external_plugins`**
( `bool`)
–


- **`create_legacy_output`**
( `bool`)
–


- **`document_timeout`**
( `Optional[float]`)
–


- **`enable_remote_services`**
( `bool`)
–



#### `` accelerator\_options`class-attribute``instance-attribute`

```
accelerator_options: AcceleratorOptions = AcceleratorOptions()

```

#### `` allow\_external\_plugins`class-attribute``instance-attribute`

```
allow_external_plugins: bool = False

```

#### `` create\_legacy\_output`class-attribute``instance-attribute`

```
create_legacy_output: bool = True

```

#### `` document\_timeout`class-attribute``instance-attribute`

```
document_timeout: Optional[float] = None

```

#### `` enable\_remote\_services`class-attribute``instance-attribute`

```
enable_remote_services: bool = False

```

### `` RapidOcrOptions

Bases: `OcrOptions`

Options for the RapidOCR engine.

Attributes:

- **`bitmap_area_threshold`**
( `float`)
–


- **`cls_model_path`**
( `Optional[str]`)
–


- **`det_model_path`**
( `Optional[str]`)
–


- **`force_full_page_ocr`**
( `bool`)
–


- **`kind`**
( `Literal['rapidocr']`)
–


- **`lang`**
( `List[str]`)
–


- **`model_config`**
–


- **`print_verbose`**
( `bool`)
–


- **`rec_keys_path`**
( `Optional[str]`)
–


- **`rec_model_path`**
( `Optional[str]`)
–


- **`text_score`**
( `float`)
–


- **`use_cls`**
( `Optional[bool]`)
–


- **`use_det`**
( `Optional[bool]`)
–


- **`use_rec`**
( `Optional[bool]`)
–



#### `` bitmap\_area\_threshold`class-attribute``instance-attribute`

```
bitmap_area_threshold: float = 0.05

```

#### `` cls\_model\_path`class-attribute``instance-attribute`

```
cls_model_path: Optional[str] = None

```

#### `` det\_model\_path`class-attribute``instance-attribute`

```
det_model_path: Optional[str] = None

```

#### `` force\_full\_page\_ocr`class-attribute``instance-attribute`

```
force_full_page_ocr: bool = False

```

#### `` kind`class-attribute`

```
kind: Literal['rapidocr'] = 'rapidocr'

```

#### `` lang`class-attribute``instance-attribute`

```
lang: List[str] = ['english', 'chinese']

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(extra='forbid')

```

#### `` print\_verbose`class-attribute``instance-attribute`

```
print_verbose: bool = False

```

#### `` rec\_keys\_path`class-attribute``instance-attribute`

```
rec_keys_path: Optional[str] = None

```

#### `` rec\_model\_path`class-attribute``instance-attribute`

```
rec_model_path: Optional[str] = None

```

#### `` text\_score`class-attribute``instance-attribute`

```
text_score: float = 0.5

```

#### `` use\_cls`class-attribute``instance-attribute`

```
use_cls: Optional[bool] = None

```

#### `` use\_det`class-attribute``instance-attribute`

```
use_det: Optional[bool] = None

```

#### `` use\_rec`class-attribute``instance-attribute`

```
use_rec: Optional[bool] = None

```

### `` TableFormerMode

Bases: `str`, `Enum`

Modes for the TableFormer model.

Attributes:

- **`ACCURATE`**
–


- **`FAST`**
–



#### `` ACCURATE`class-attribute``instance-attribute`

```
ACCURATE = 'accurate'

```

#### `` FAST`class-attribute``instance-attribute`

```
FAST = 'fast'

```

### `` TableStructureOptions

Bases: `BaseModel`

Options for the table structure.

Attributes:

- **`do_cell_matching`**
( `bool`)
–


- **`mode`**
( `TableFormerMode`)
–



#### `` do\_cell\_matching`class-attribute``instance-attribute`

```
do_cell_matching: bool = True

```

#### `` mode`class-attribute``instance-attribute`

```
mode: TableFormerMode = ACCURATE

```

### `` TesseractCliOcrOptions

Bases: `OcrOptions`

Options for the TesseractCli engine.

Attributes:

- **`bitmap_area_threshold`**
( `float`)
–


- **`force_full_page_ocr`**
( `bool`)
–


- **`kind`**
( `Literal['tesseract']`)
–


- **`lang`**
( `List[str]`)
–


- **`model_config`**
–


- **`path`**
( `Optional[str]`)
–


- **`tesseract_cmd`**
( `str`)
–



#### `` bitmap\_area\_threshold`class-attribute``instance-attribute`

```
bitmap_area_threshold: float = 0.05

```

#### `` force\_full\_page\_ocr`class-attribute``instance-attribute`

```
force_full_page_ocr: bool = False

```

#### `` kind`class-attribute`

```
kind: Literal['tesseract'] = 'tesseract'

```

#### `` lang`class-attribute``instance-attribute`

```
lang: List[str] = ['fra', 'deu', 'spa', 'eng']

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(extra='forbid')

```

#### `` path`class-attribute``instance-attribute`

```
path: Optional[str] = None

```

#### `` tesseract\_cmd`class-attribute``instance-attribute`

```
tesseract_cmd: str = 'tesseract'

```

### `` TesseractOcrOptions

Bases: `OcrOptions`

Options for the Tesseract engine.

Attributes:

- **`bitmap_area_threshold`**
( `float`)
–


- **`force_full_page_ocr`**
( `bool`)
–


- **`kind`**
( `Literal['tesserocr']`)
–


- **`lang`**
( `List[str]`)
–


- **`model_config`**
–


- **`path`**
( `Optional[str]`)
–



#### `` bitmap\_area\_threshold`class-attribute``instance-attribute`

```
bitmap_area_threshold: float = 0.05

```

#### `` force\_full\_page\_ocr`class-attribute``instance-attribute`

```
force_full_page_ocr: bool = False

```

#### `` kind`class-attribute`

```
kind: Literal['tesserocr'] = 'tesserocr'

```

#### `` lang`class-attribute``instance-attribute`

```
lang: List[str] = ['fra', 'deu', 'spa', 'eng']

```

#### `` model\_config`class-attribute``instance-attribute`

```
model_config = ConfigDict(extra='forbid')

```

#### `` path`class-attribute``instance-attribute`

```
path: Optional[str] = None

```

### `` VlmPipelineOptions

Bases: `PaginatedPipelineOptions`

Attributes:

- **`accelerator_options`**
( `AcceleratorOptions`)
–


- **`allow_external_plugins`**
( `bool`)
–


- **`artifacts_path`**
( `Optional[Union[Path, str]]`)
–


- **`create_legacy_output`**
( `bool`)
–


- **`document_timeout`**
( `Optional[float]`)
–


- **`enable_remote_services`**
( `bool`)
–


- **`force_backend_text`**
( `bool`)
–


- **`generate_page_images`**
( `bool`)
–


- **`generate_picture_images`**
( `bool`)
–


- **`images_scale`**
( `float`)
–


- **`vlm_options`**
( `Union[InlineVlmOptions, ApiVlmOptions]`)
–



#### `` accelerator\_options`class-attribute``instance-attribute`

```
accelerator_options: AcceleratorOptions = AcceleratorOptions()

```

#### `` allow\_external\_plugins`class-attribute``instance-attribute`

```
allow_external_plugins: bool = False

```

#### `` artifacts\_path`class-attribute``instance-attribute`

```
artifacts_path: Optional[Union[Path, str]] = None

```

#### `` create\_legacy\_output`class-attribute``instance-attribute`

```
create_legacy_output: bool = True

```

#### `` document\_timeout`class-attribute``instance-attribute`

```
document_timeout: Optional[float] = None

```

#### `` enable\_remote\_services`class-attribute``instance-attribute`

```
enable_remote_services: bool = False

```

#### `` force\_backend\_text`class-attribute``instance-attribute`

```
force_backend_text: bool = False

```

#### `` generate\_page\_images`class-attribute``instance-attribute`

```
generate_page_images: bool = True

```

#### `` generate\_picture\_images`class-attribute``instance-attribute`

```
generate_picture_images: bool = False

```

#### `` images\_scale`class-attribute``instance-attribute`

```
images_scale: float = 1.0

```

#### `` vlm\_options`class-attribute``instance-attribute`

```
vlm_options: Union[InlineVlmOptions, ApiVlmOptions] = SMOLDOCLING_TRANSFORMERS

```

Back to top