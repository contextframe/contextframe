---
url: "https://docling-project.github.io/docling/reference/docling_document/"
title: "Docling Document - Docling"
---

[Skip to content](https://docling-project.github.io/docling/reference/docling_document/#docling-document)

# Docling Document

This is an automatic generated API reference of the DoclingDocument type.

## `` doc

Package for models defined by the Document type.

Classes:

- **`DoclingDocument`**
–



DoclingDocument.

- **`DocumentOrigin`**
–



FileSource.

- **`DocItem`**
–



DocItem.

- **`DocItemLabel`**
–



DocItemLabel.

- **`ProvenanceItem`**
–



ProvenanceItem.

- **`GroupItem`**
–



GroupItem.

- **`GroupLabel`**
–



GroupLabel.

- **`NodeItem`**
–



NodeItem.

- **`PageItem`**
–



PageItem.

- **`FloatingItem`**
–



FloatingItem.

- **`TextItem`**
–



TextItem.

- **`TableItem`**
–



TableItem.

- **`TableCell`**
–



TableCell.

- **`TableData`**
–



BaseTableData.

- **`TableCellLabel`**
–



TableCellLabel.

- **`KeyValueItem`**
–



KeyValueItem.

- **`SectionHeaderItem`**
–



SectionItem.

- **`PictureItem`**
–



PictureItem.

- **`ImageRef`**
–



ImageRef.

- **`PictureClassificationClass`**
–



PictureClassificationData.

- **`PictureClassificationData`**
–



PictureClassificationData.

- **`RefItem`**
–



RefItem.

- **`BoundingBox`**
–



BoundingBox.

- **`CoordOrigin`**
–



CoordOrigin.

- **`ImageRefMode`**
–



ImageRefMode.

- **`Size`**
–



Size.


### `` DoclingDocument

Bases: `BaseModel`

DoclingDocument.

Methods:

- **`add_code`**
–



add\_code.

- **`add_form`**
–



add\_form.

- **`add_formula`**
–



add\_formula.

- **`add_group`**
–



add\_group.

- **`add_heading`**
–



add\_heading.

- **`add_inline_group`**
–



add\_inline\_group.

- **`add_key_values`**
–



add\_key\_values.

- **`add_list_item`**
–



add\_list\_item.

- **`add_ordered_list`**
–



add\_ordered\_list.

- **`add_page`**
–



add\_page.

- **`add_picture`**
–



add\_picture.

- **`add_table`**
–



add\_table.

- **`add_text`**
–



add\_text.

- **`add_title`**
–



add\_title.

- **`add_unordered_list`**
–



add\_unordered\_list.

- **`append_child_item`**
–



Adds an item.

- **`check_version_is_compatible`**
–



Check if this document version is compatible with current version.

- **`delete_items`**
–



Deletes an item, given its instance or ref, and any children it has.

- **`export_to_dict`**
–



Export to dict.

- **`export_to_doctags`**
–



Exports the document content to a DocumentToken format.

- **`export_to_document_tokens`**
–



Export to DocTags format.

- **`export_to_element_tree`**
–



Export\_to\_element\_tree.

- **`export_to_html`**
–



Serialize to HTML.

- **`export_to_markdown`**
–



Serialize to Markdown.

- **`export_to_text`**
–



export\_to\_text.

- **`get_visualization`**
–



Get visualization of the document as images by page.

- **`insert_item_after_sibling`**
–



Inserts an item, given its node\_item instance, after other as a sibling.

- **`insert_item_before_sibling`**
–



Inserts an item, given its node\_item instance, before other as a sibling.

- **`iterate_items`**
–



Iterate elements with level.

- **`load_from_doctags`**
–



Load Docling document from lists of DocTags and Images.

- **`load_from_json`**
–



load\_from\_json.

- **`load_from_yaml`**
–



load\_from\_yaml.

- **`num_pages`**
–



num\_pages.

- **`print_element_tree`**
–



Print\_element\_tree.

- **`replace_item`**
–



Replace item with new item.

- **`save_as_doctags`**
–



Save the document content to DocTags format.

- **`save_as_document_tokens`**
–



Save the document content to a DocumentToken format.

- **`save_as_html`**
–



Save to HTML.

- **`save_as_json`**
–



Save as json.

- **`save_as_markdown`**
–



Save to markdown.

- **`save_as_yaml`**
–



Save as yaml.

- **`transform_to_content_layer`**
–



transform\_to\_content\_layer.

- **`validate_document`**
–



validate\_document.

- **`validate_tree`**
–



validate\_tree.


Attributes:

- **`body`**
( `GroupItem`)
–


- **`form_items`**
( `List[FormItem]`)
–


- **`furniture`**
( `Annotated[GroupItem, Field(deprecated=True)]`)
–


- **`groups`**
( `List[Union[OrderedList, UnorderedList, InlineGroup, GroupItem]]`)
–


- **`key_value_items`**
( `List[KeyValueItem]`)
–


- **`name`**
( `str`)
–


- **`origin`**
( `Optional[DocumentOrigin]`)
–


- **`pages`**
( `Dict[int, PageItem]`)
–


- **`pictures`**
( `List[PictureItem]`)
–


- **`schema_name`**
( `Literal['DoclingDocument']`)
–


- **`tables`**
( `List[TableItem]`)
–


- **`texts`**
( `List[Union[TitleItem, SectionHeaderItem, ListItem, CodeItem, FormulaItem, TextItem]]`)
–


- **`version`**
( `Annotated[str, StringConstraints(pattern=VERSION_PATTERN, strict=True)]`)
–



#### `` body

```
body: GroupItem = GroupItem(name='_root_', self_ref='#/body')

```

#### `` form\_items

```
form_items: List[FormItem] = []

```

#### `` furniture

```
furniture: Annotated[GroupItem, Field(deprecated=True)] = GroupItem(name='_root_', self_ref='#/furniture', content_layer=FURNITURE)

```

#### `` groups

```
groups: List[Union[OrderedList, UnorderedList, InlineGroup, GroupItem]] = []

```

#### `` key\_value\_items

```
key_value_items: List[KeyValueItem] = []

```

#### `` name

```
name: str

```

#### `` origin

```
origin: Optional[DocumentOrigin] = None

```

#### `` pages

```
pages: Dict[int, PageItem] = {}

```

#### `` pictures

```
pictures: List[PictureItem] = []

```

#### `` schema\_name

```
schema_name: Literal['DoclingDocument'] = 'DoclingDocument'

```

#### `` tables

```
tables: List[TableItem] = []

```

#### `` texts

```
texts: List[Union[TitleItem, SectionHeaderItem, ListItem, CodeItem, FormulaItem, TextItem]] = []

```

#### `` version

```
version: Annotated[str, StringConstraints(pattern=VERSION_PATTERN, strict=True)] = CURRENT_VERSION

```

#### `` add\_code

```
add_code(text: str, code_language: Optional[CodeLanguageLabel] = None, orig: Optional[str] = None, caption: Optional[Union[TextItem, RefItem]] = None, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None, formatting: Optional[Formatting] = None, hyperlink: Optional[Union[AnyUrl, Path]] = None)

```

add\_code.

Parameters:

- **`text`**
( `str`)
–



str:

- **`code_language`**
( `Optional[CodeLanguageLabel]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`orig`**
( `Optional[str]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`caption`**
( `Optional[Union[TextItem, RefItem]]`, default:
`None`
)
–



Optional\[Union\[TextItem:\
\
- **`RefItem]]`**
–



(Default value = None)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_form

```
add_form(graph: GraphData, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None)

```

add\_form.

Parameters:

- **`graph`**
( `GraphData`)
–



GraphData:

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_formula

```
add_formula(text: str, orig: Optional[str] = None, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None, formatting: Optional[Formatting] = None, hyperlink: Optional[Union[AnyUrl, Path]] = None)

```

add\_formula.

Parameters:

- **`text`**
( `str`)
–



str:

- **`orig`**
( `Optional[str]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`level`**
–



LevelNumber: (Default value = 1)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_group

```
add_group(label: Optional[GroupLabel] = None, name: Optional[str] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None) -> GroupItem

```

add\_group.

Parameters:

- **`label`**
( `Optional[GroupLabel]`, default:
`None`
)
–



Optional\[GroupLabel\]: (Default value = None)

- **`name`**
( `Optional[str]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_heading

```
add_heading(text: str, orig: Optional[str] = None, level: LevelNumber = 1, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None, formatting: Optional[Formatting] = None, hyperlink: Optional[Union[AnyUrl, Path]] = None)

```

add\_heading.

Parameters:

- **`label`**
–



DocItemLabel:

- **`text`**
( `str`)
–



str:

- **`orig`**
( `Optional[str]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`level`**
( `LevelNumber`, default:
`1`
)
–



LevelNumber: (Default value = 1)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_inline\_group

```
add_inline_group(name: Optional[str] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None) -> GroupItem

```

add\_inline\_group.

#### `` add\_key\_values

```
add_key_values(graph: GraphData, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None)

```

add\_key\_values.

Parameters:

- **`graph`**
( `GraphData`)
–



GraphData:

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_list\_item

```
add_list_item(text: str, enumerated: bool = False, marker: Optional[str] = None, orig: Optional[str] = None, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None, formatting: Optional[Formatting] = None, hyperlink: Optional[Union[AnyUrl, Path]] = None)

```

add\_list\_item.

Parameters:

- **`label`**
–



str:

- **`text`**
( `str`)
–



str:

- **`orig`**
( `Optional[str]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_ordered\_list

```
add_ordered_list(name: Optional[str] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None) -> GroupItem

```

add\_ordered\_list.

#### `` add\_page

```
add_page(page_no: int, size: Size, image: Optional[ImageRef] = None) -> PageItem

```

add\_page.

Parameters:

- **`page_no`**
( `int`)
–



int:

- **`size`**
( `Size`)
–



Size:


#### `` add\_picture

```
add_picture(annotations: List[PictureDataType] = [], image: Optional[ImageRef] = None, caption: Optional[Union[TextItem, RefItem]] = None, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None)

```

add\_picture.

Parameters:

- **`data`**
–



List\[PictureData\]: (Default value = \[\])

- **`caption`**
( `Optional[Union[TextItem, RefItem]]`, default:
`None`
)
–



Optional\[Union\[TextItem:\
\
- **`RefItem]]`**
–



(Default value = None)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_table

```
add_table(data: TableData, caption: Optional[Union[TextItem, RefItem]] = None, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, label: DocItemLabel = TABLE, content_layer: Optional[ContentLayer] = None)

```

add\_table.

Parameters:

- **`data`**
( `TableData`)
–



TableData:

- **`caption`**
( `Optional[Union[TextItem, RefItem]]`, default:
`None`
)
–



Optional\[Union\[TextItem, RefItem\]\]: (Default value = None)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)

- **`label`**
( `DocItemLabel`, default:
`TABLE`
)
–



DocItemLabel: (Default value = DocItemLabel.TABLE)


#### `` add\_text

```
add_text(label: DocItemLabel, text: str, orig: Optional[str] = None, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None, formatting: Optional[Formatting] = None, hyperlink: Optional[Union[AnyUrl, Path]] = None)

```

add\_text.

Parameters:

- **`label`**
( `DocItemLabel`)
–



str:

- **`text`**
( `str`)
–



str:

- **`orig`**
( `Optional[str]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_title

```
add_title(text: str, orig: Optional[str] = None, prov: Optional[ProvenanceItem] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None, formatting: Optional[Formatting] = None, hyperlink: Optional[Union[AnyUrl, Path]] = None)

```

add\_title.

Parameters:

- **`text`**
( `str`)
–



str:

- **`orig`**
( `Optional[str]`, default:
`None`
)
–



Optional\[str\]: (Default value = None)

- **`level`**
–



LevelNumber: (Default value = 1)

- **`prov`**
( `Optional[ProvenanceItem]`, default:
`None`
)
–



Optional\[ProvenanceItem\]: (Default value = None)

- **`parent`**
( `Optional[NodeItem]`, default:
`None`
)
–



Optional\[NodeItem\]: (Default value = None)


#### `` add\_unordered\_list

```
add_unordered_list(name: Optional[str] = None, parent: Optional[NodeItem] = None, content_layer: Optional[ContentLayer] = None) -> GroupItem

```

add\_unordered\_list.

#### `` append\_child\_item

```
append_child_item(*, child: NodeItem, parent: Optional[NodeItem] = None) -> None

```

Adds an item.

#### `` check\_version\_is\_compatible

```
check_version_is_compatible(v: str) -> str

```

Check if this document version is compatible with current version.

#### `` delete\_items

```
delete_items(*, node_items: List[NodeItem]) -> None

```

Deletes an item, given its instance or ref, and any children it has.

#### `` export\_to\_dict

```
export_to_dict(mode: str = 'json', by_alias: bool = True, exclude_none: bool = True) -> Dict[str, Any]

```

Export to dict.

#### `` export\_to\_doctags

```
export_to_doctags(delim: str = '', from_element: int = 0, to_element: int = maxsize, labels: Optional[set[DocItemLabel]] = None, xsize: int = 500, ysize: int = 500, add_location: bool = True, add_content: bool = True, add_page_index: bool = True, add_table_cell_location: bool = False, add_table_cell_text: bool = True, minified: bool = False) -> str

```

Exports the document content to a DocumentToken format.

Operates on a slice of the document's body as defined through arguments
from\_element and to\_element; defaulting to the whole main\_text.

Parameters:

- **`delim`**
( `str`, default:
`''`
)
–



str: (Default value = "") Deprecated

- **`from_element`**
( `int`, default:
`0`
)
–



int: (Default value = 0)

- **`to_element`**
( `int`, default:
`maxsize`
)
–



Optional\[int\]: (Default value = None)

- **`labels`**
( `Optional[set[DocItemLabel]]`, default:
`None`
)
–



set\[DocItemLabel\]

- **`xsize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`ysize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`add_location`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_content`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_page_index`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_table_cell_text`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`minified`**
( `bool`, default:
`False`
)
–



bool: (Default value = False)


Returns:

- `str`
–



The content of the document formatted as a DocTags string.


#### `` export\_to\_document\_tokens

```
export_to_document_tokens(*args, **kwargs)

```

Export to DocTags format.

#### `` export\_to\_element\_tree

```
export_to_element_tree() -> str

```

Export\_to\_element\_tree.

#### `` export\_to\_html

```
export_to_html(from_element: int = 0, to_element: int = maxsize, labels: Optional[set[DocItemLabel]] = None, enable_chart_tables: bool = True, image_mode: ImageRefMode = PLACEHOLDER, formula_to_mathml: bool = True, page_no: Optional[int] = None, html_lang: str = 'en', html_head: str = 'null', included_content_layers: Optional[set[ContentLayer]] = None, split_page_view: bool = False, include_annotations: bool = True) -> str

```

Serialize to HTML.

#### `` export\_to\_markdown

```
export_to_markdown(delim: str = '\n\n', from_element: int = 0, to_element: int = maxsize, labels: Optional[set[DocItemLabel]] = None, strict_text: bool = False, escape_underscores: bool = True, image_placeholder: str = '<!-- image -->', enable_chart_tables: bool = True, image_mode: ImageRefMode = PLACEHOLDER, indent: int = 4, text_width: int = -1, page_no: Optional[int] = None, included_content_layers: Optional[set[ContentLayer]] = None, page_break_placeholder: Optional[str] = None, include_annotations: bool = True, mark_annotations: bool = False) -> str

```

Serialize to Markdown.

Operates on a slice of the document's body as defined through arguments
from\_element and to\_element; defaulting to the whole document.

Parameters:

- **`delim`**
( `str`, default:
`'\n\n'`
)
–



Deprecated.

- **`from_element`**
( `int`, default:
`0`
)
–



Body slicing start index (inclusive). (Default value = 0).

- **`to_element`**
( `int`, default:
`maxsize`
)
–



Body slicing stop index (exclusive). (Default value = maxint).

- **`labels`**
( `Optional[set[DocItemLabel]]`, default:
`None`
)
–



The set of document labels to include in the export. None falls back to the system-defined default.

- **`strict_text`**
( `bool`, default:
`False`
)
–



Deprecated.

- **`escape_underscores`**
( `bool`, default:
`True`
)
–



bool: Whether to escape underscores in the text content of the document. (Default value = True).

- **`image_placeholder`**
( `str`, default:
`'<!-- image -->'`
)
–



The placeholder to include to position images in the markdown. (Default value = "\\<!-- image -->").

- **`image_mode`**
( `ImageRefMode`, default:
`PLACEHOLDER`
)
–



The mode to use for including images in the markdown. (Default value = ImageRefMode.PLACEHOLDER).

- **`indent`**
( `int`, default:
`4`
)
–



The indent in spaces of the nested lists. (Default value = 4).

- **`included_content_layers`**
( `Optional[set[ContentLayer]]`, default:
`None`
)
–



The set of layels to include in the export. None falls back to the system-defined default.

- **`page_break_placeholder`**
( `Optional[str]`, default:
`None`
)
–



The placeholder to include for marking page breaks. None means no page break placeholder will be used.

- **`include_annotations`**
( `bool`, default:
`True`
)
–



bool: Whether to include annotations in the export. (Default value = True).

- **`mark_annotations`**
( `bool`, default:
`False`
)
–



bool: Whether to mark annotations in the export; only relevant if include\_annotations is True. (Default value = False).


Returns:

- `str`
–



The exported Markdown representation.


#### `` export\_to\_text

```
export_to_text(delim: str = '\n\n', from_element: int = 0, to_element: int = 1000000, labels: Optional[set[DocItemLabel]] = None) -> str

```

export\_to\_text.

#### `` get\_visualization

```
get_visualization(show_label: bool = True) -> dict[Optional[int], Image]

```

Get visualization of the document as images by page.

#### `` insert\_item\_after\_sibling

```
insert_item_after_sibling(*, new_item: NodeItem, sibling: NodeItem) -> None

```

Inserts an item, given its node\_item instance, after other as a sibling.

#### `` insert\_item\_before\_sibling

```
insert_item_before_sibling(*, new_item: NodeItem, sibling: NodeItem) -> None

```

Inserts an item, given its node\_item instance, before other as a sibling.

#### `` iterate\_items

```
iterate_items(root: Optional[NodeItem] = None, with_groups: bool = False, traverse_pictures: bool = False, page_no: Optional[int] = None, included_content_layers: Optional[set[ContentLayer]] = None, _level: int = 0) -> Iterable[Tuple[NodeItem, int]]

```

Iterate elements with level.

#### `` load\_from\_doctags

```
load_from_doctags(doctag_document: DocTagsDocument, document_name: str = 'Document') -> DoclingDocument

```

Load Docling document from lists of DocTags and Images.

#### `` load\_from\_json

```
load_from_json(filename: Union[str, Path]) -> DoclingDocument

```

load\_from\_json.

Parameters:

- **`filename`**
( `Union[str, Path]`)
–



The filename to load a saved DoclingDocument from a .json.


Returns:

- `DoclingDocument`
–



The loaded DoclingDocument.


#### `` load\_from\_yaml

```
load_from_yaml(filename: Union[str, Path]) -> DoclingDocument

```

load\_from\_yaml.

Args:
filename: The filename to load a YAML-serialized DoclingDocument from.

Returns:
DoclingDocument: the loaded DoclingDocument

#### `` num\_pages

```
num_pages()

```

num\_pages.

#### `` print\_element\_tree

```
print_element_tree()

```

Print\_element\_tree.

#### `` replace\_item

```
replace_item(*, new_item: NodeItem, old_item: NodeItem) -> None

```

Replace item with new item.

#### `` save\_as\_doctags

```
save_as_doctags(filename: Union[str, Path], delim: str = '', from_element: int = 0, to_element: int = maxsize, labels: Optional[set[DocItemLabel]] = None, xsize: int = 500, ysize: int = 500, add_location: bool = True, add_content: bool = True, add_page_index: bool = True, add_table_cell_location: bool = False, add_table_cell_text: bool = True, minified: bool = False)

```

Save the document content to DocTags format.

#### `` save\_as\_document\_tokens

```
save_as_document_tokens(*args, **kwargs)

```

Save the document content to a DocumentToken format.

#### `` save\_as\_html

```
save_as_html(filename: Union[str, Path], artifacts_dir: Optional[Path] = None, from_element: int = 0, to_element: int = maxsize, labels: Optional[set[DocItemLabel]] = None, image_mode: ImageRefMode = PLACEHOLDER, formula_to_mathml: bool = True, page_no: Optional[int] = None, html_lang: str = 'en', html_head: str = 'null', included_content_layers: Optional[set[ContentLayer]] = None, split_page_view: bool = False, include_annotations: bool = True)

```

Save to HTML.

#### `` save\_as\_json

```
save_as_json(filename: Union[str, Path], artifacts_dir: Optional[Path] = None, image_mode: ImageRefMode = EMBEDDED, indent: int = 2)

```

Save as json.

#### `` save\_as\_markdown

```
save_as_markdown(filename: Union[str, Path], artifacts_dir: Optional[Path] = None, delim: str = '\n\n', from_element: int = 0, to_element: int = maxsize, labels: Optional[set[DocItemLabel]] = None, strict_text: bool = False, escaping_underscores: bool = True, image_placeholder: str = '<!-- image -->', image_mode: ImageRefMode = PLACEHOLDER, indent: int = 4, text_width: int = -1, page_no: Optional[int] = None, included_content_layers: Optional[set[ContentLayer]] = None, page_break_placeholder: Optional[str] = None, include_annotations: bool = True)

```

Save to markdown.

#### `` save\_as\_yaml

```
save_as_yaml(filename: Union[str, Path], artifacts_dir: Optional[Path] = None, image_mode: ImageRefMode = EMBEDDED, default_flow_style: bool = False)

```

Save as yaml.

#### `` transform\_to\_content\_layer

```
transform_to_content_layer(data: dict) -> dict

```

transform\_to\_content\_layer.

#### `` validate\_document

```
validate_document(d: DoclingDocument)

```

validate\_document.

#### `` validate\_tree

```
validate_tree(root) -> bool

```

validate\_tree.

### `` DocumentOrigin

Bases: `BaseModel`

FileSource.

Methods:

- **`parse_hex_string`**
–



parse\_hex\_string.

- **`validate_mimetype`**
–



validate\_mimetype.


Attributes:

- **`binary_hash`**
( `Uint64`)
–


- **`filename`**
( `str`)
–


- **`mimetype`**
( `str`)
–


- **`uri`**
( `Optional[AnyUrl]`)
–



#### `` binary\_hash

```
binary_hash: Uint64

```

#### `` filename

```
filename: str

```

#### `` mimetype

```
mimetype: str

```

#### `` uri

```
uri: Optional[AnyUrl] = None

```

#### `` parse\_hex\_string

```
parse_hex_string(value)

```

parse\_hex\_string.

#### `` validate\_mimetype

```
validate_mimetype(v)

```

validate\_mimetype.

### `` DocItem

Bases: `NodeItem`

DocItem.

Methods:

- **`get_image`**
–



Returns the image of this DocItem.

- **`get_location_tokens`**
–



Get the location string for the BaseCell.

- **`get_ref`**
–



get\_ref.


Attributes:

- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`label`**
( `DocItemLabel`)
–


- **`model_config`**
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`prov`**
( `List[ProvenanceItem]`)
–


- **`self_ref`**
( `str`)
–



#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` label

```
label: DocItemLabel

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` prov

```
prov: List[ProvenanceItem] = []

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` get\_image

```
get_image(doc: DoclingDocument, prov_index: int = 0) -> Optional[Image]

```

Returns the image of this DocItem.

The function returns None if this DocItem has no valid provenance or
if a valid image of the page containing this DocItem is not available
in doc.

#### `` get\_location\_tokens

```
get_location_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500) -> str

```

Get the location string for the BaseCell.

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` DocItemLabel

Bases: `str`, `Enum`

DocItemLabel.

Methods:

- **`get_color`**
–



Return the RGB color associated with a given label.


Attributes:

- **`CAPTION`**
–


- **`CHART`**
–


- **`CHECKBOX_SELECTED`**
–


- **`CHECKBOX_UNSELECTED`**
–


- **`CODE`**
–


- **`DOCUMENT_INDEX`**
–


- **`FOOTNOTE`**
–


- **`FORM`**
–


- **`FORMULA`**
–


- **`GRADING_SCALE`**
–


- **`KEY_VALUE_REGION`**
–


- **`LIST_ITEM`**
–


- **`PAGE_FOOTER`**
–


- **`PAGE_HEADER`**
–


- **`PARAGRAPH`**
–


- **`PICTURE`**
–


- **`REFERENCE`**
–


- **`SECTION_HEADER`**
–


- **`TABLE`**
–


- **`TEXT`**
–


- **`TITLE`**
–



#### `` CAPTION

```
CAPTION = 'caption'

```

#### `` CHART

```
CHART = 'chart'

```

#### `` CHECKBOX\_SELECTED

```
CHECKBOX_SELECTED = 'checkbox_selected'

```

#### `` CHECKBOX\_UNSELECTED

```
CHECKBOX_UNSELECTED = 'checkbox_unselected'

```

#### `` CODE

```
CODE = 'code'

```

#### `` DOCUMENT\_INDEX

```
DOCUMENT_INDEX = 'document_index'

```

#### `` FOOTNOTE

```
FOOTNOTE = 'footnote'

```

#### `` FORM

```
FORM = 'form'

```

#### `` FORMULA

```
FORMULA = 'formula'

```

#### `` GRADING\_SCALE

```
GRADING_SCALE = 'grading_scale'

```

#### `` KEY\_VALUE\_REGION

```
KEY_VALUE_REGION = 'key_value_region'

```

#### `` LIST\_ITEM

```
LIST_ITEM = 'list_item'

```

#### `` PAGE\_FOOTER

```
PAGE_FOOTER = 'page_footer'

```

#### `` PAGE\_HEADER

```
PAGE_HEADER = 'page_header'

```

#### `` PARAGRAPH

```
PARAGRAPH = 'paragraph'

```

#### `` PICTURE

```
PICTURE = 'picture'

```

#### `` REFERENCE

```
REFERENCE = 'reference'

```

#### `` SECTION\_HEADER

```
SECTION_HEADER = 'section_header'

```

#### `` TABLE

```
TABLE = 'table'

```

#### `` TEXT

```
TEXT = 'text'

```

#### `` TITLE

```
TITLE = 'title'

```

#### `` get\_color

```
get_color(label: DocItemLabel) -> Tuple[int, int, int]

```

Return the RGB color associated with a given label.

### `` ProvenanceItem

Bases: `BaseModel`

ProvenanceItem.

Attributes:

- **`bbox`**
( `BoundingBox`)
–


- **`charspan`**
( `Tuple[int, int]`)
–


- **`page_no`**
( `int`)
–



#### `` bbox

```
bbox: BoundingBox

```

#### `` charspan

```
charspan: Tuple[int, int]

```

#### `` page\_no

```
page_no: int

```

### `` GroupItem

Bases: `NodeItem`

GroupItem.

Methods:

- **`get_ref`**
–



get\_ref.


Attributes:

- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`label`**
( `GroupLabel`)
–


- **`model_config`**
–


- **`name`**
( `str`)
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`self_ref`**
( `str`)
–



#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` label

```
label: GroupLabel = UNSPECIFIED

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` name

```
name: str = 'group'

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` GroupLabel

Bases: `str`, `Enum`

GroupLabel.

Attributes:

- **`CHAPTER`**
–


- **`COMMENT_SECTION`**
–


- **`FORM_AREA`**
–


- **`INLINE`**
–


- **`KEY_VALUE_AREA`**
–


- **`LIST`**
–


- **`ORDERED_LIST`**
–


- **`PICTURE_AREA`**
–


- **`SECTION`**
–


- **`SHEET`**
–


- **`SLIDE`**
–


- **`UNSPECIFIED`**
–



#### `` CHAPTER

```
CHAPTER = 'chapter'

```

#### `` COMMENT\_SECTION

```
COMMENT_SECTION = 'comment_section'

```

#### `` FORM\_AREA

```
FORM_AREA = 'form_area'

```

#### `` INLINE

```
INLINE = 'inline'

```

#### `` KEY\_VALUE\_AREA

```
KEY_VALUE_AREA = 'key_value_area'

```

#### `` LIST

```
LIST = 'list'

```

#### `` ORDERED\_LIST

```
ORDERED_LIST = 'ordered_list'

```

#### `` PICTURE\_AREA

```
PICTURE_AREA = 'picture_area'

```

#### `` SECTION

```
SECTION = 'section'

```

#### `` SHEET

```
SHEET = 'sheet'

```

#### `` SLIDE

```
SLIDE = 'slide'

```

#### `` UNSPECIFIED

```
UNSPECIFIED = 'unspecified'

```

### `` NodeItem

Bases: `BaseModel`

NodeItem.

Methods:

- **`get_ref`**
–



get\_ref.


Attributes:

- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`model_config`**
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`self_ref`**
( `str`)
–



#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` PageItem

Bases: `BaseModel`

PageItem.

Attributes:

- **`image`**
( `Optional[ImageRef]`)
–


- **`page_no`**
( `int`)
–


- **`size`**
( `Size`)
–



#### `` image

```
image: Optional[ImageRef] = None

```

#### `` page\_no

```
page_no: int

```

#### `` size

```
size: Size

```

### `` FloatingItem

Bases: `DocItem`

FloatingItem.

Methods:

- **`caption_text`**
–



Computes the caption as a single text.

- **`get_image`**
–



Returns the image corresponding to this FloatingItem.

- **`get_location_tokens`**
–



Get the location string for the BaseCell.

- **`get_ref`**
–



get\_ref.


Attributes:

- **`captions`**
( `List[RefItem]`)
–


- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`footnotes`**
( `List[RefItem]`)
–


- **`image`**
( `Optional[ImageRef]`)
–


- **`label`**
( `DocItemLabel`)
–


- **`model_config`**
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`prov`**
( `List[ProvenanceItem]`)
–


- **`references`**
( `List[RefItem]`)
–


- **`self_ref`**
( `str`)
–



#### `` captions

```
captions: List[RefItem] = []

```

#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` footnotes

```
footnotes: List[RefItem] = []

```

#### `` image

```
image: Optional[ImageRef] = None

```

#### `` label

```
label: DocItemLabel

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` prov

```
prov: List[ProvenanceItem] = []

```

#### `` references

```
references: List[RefItem] = []

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` caption\_text

```
caption_text(doc: DoclingDocument) -> str

```

Computes the caption as a single text.

#### `` get\_image

```
get_image(doc: DoclingDocument, prov_index: int = 0) -> Optional[Image]

```

Returns the image corresponding to this FloatingItem.

This function returns the PIL image from self.image if one is available.
Otherwise, it uses DocItem.get\_image to get an image of this FloatingItem.

In particular, when self.image is None, the function returns None if this
FloatingItem has no valid provenance or the doc does not contain a valid image
for the required page.

#### `` get\_location\_tokens

```
get_location_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500) -> str

```

Get the location string for the BaseCell.

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` TextItem

Bases: `DocItem`

TextItem.

Methods:

- **`export_to_doctags`**
–



Export text element to document tokens format.

- **`export_to_document_tokens`**
–



Export to DocTags format.

- **`get_image`**
–



Returns the image of this DocItem.

- **`get_location_tokens`**
–



Get the location string for the BaseCell.

- **`get_ref`**
–



get\_ref.


Attributes:

- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`formatting`**
( `Optional[Formatting]`)
–


- **`hyperlink`**
( `Optional[Union[AnyUrl, Path]]`)
–


- **`label`**
( `Literal[CAPTION, CHECKBOX_SELECTED, CHECKBOX_UNSELECTED, FOOTNOTE, PAGE_FOOTER, PAGE_HEADER, PARAGRAPH, REFERENCE, TEXT]`)
–


- **`model_config`**
–


- **`orig`**
( `str`)
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`prov`**
( `List[ProvenanceItem]`)
–


- **`self_ref`**
( `str`)
–


- **`text`**
( `str`)
–



#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` formatting

```
formatting: Optional[Formatting] = None

```

#### `` hyperlink

```
hyperlink: Optional[Union[AnyUrl, Path]] = Field(union_mode='left_to_right', default=None)

```

#### `` label

```
label: Literal[CAPTION, CHECKBOX_SELECTED, CHECKBOX_UNSELECTED, FOOTNOTE, PAGE_FOOTER, PAGE_HEADER, PARAGRAPH, REFERENCE, TEXT]

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` orig

```
orig: str

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` prov

```
prov: List[ProvenanceItem] = []

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` text

```
text: str

```

#### `` export\_to\_doctags

```
export_to_doctags(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500, add_location: bool = True, add_content: bool = True)

```

Export text element to document tokens format.

Parameters:

- **`doc`**
( `DoclingDocument`)
–



"DoclingDocument":

- **`new_line`**
( `str`, default:
`''`
)
–



str (Default value = "") Deprecated

- **`xsize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`ysize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`add_location`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_content`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)


#### `` export\_to\_document\_tokens

```
export_to_document_tokens(*args, **kwargs)

```

Export to DocTags format.

#### `` get\_image

```
get_image(doc: DoclingDocument, prov_index: int = 0) -> Optional[Image]

```

Returns the image of this DocItem.

The function returns None if this DocItem has no valid provenance or
if a valid image of the page containing this DocItem is not available
in doc.

#### `` get\_location\_tokens

```
get_location_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500) -> str

```

Get the location string for the BaseCell.

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` TableItem

Bases: `FloatingItem`

TableItem.

Methods:

- **`caption_text`**
–



Computes the caption as a single text.

- **`export_to_dataframe`**
–



Export the table as a Pandas DataFrame.

- **`export_to_doctags`**
–



Export table to document tokens format.

- **`export_to_document_tokens`**
–



Export to DocTags format.

- **`export_to_html`**
–



Export the table as html.

- **`export_to_markdown`**
–



Export the table as markdown.

- **`export_to_otsl`**
–



Export the table as OTSL.

- **`get_image`**
–



Returns the image corresponding to this FloatingItem.

- **`get_location_tokens`**
–



Get the location string for the BaseCell.

- **`get_ref`**
–



get\_ref.


Attributes:

- **`captions`**
( `List[RefItem]`)
–


- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`data`**
( `TableData`)
–


- **`footnotes`**
( `List[RefItem]`)
–


- **`image`**
( `Optional[ImageRef]`)
–


- **`label`**
( `Literal[DOCUMENT_INDEX, TABLE]`)
–


- **`model_config`**
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`prov`**
( `List[ProvenanceItem]`)
–


- **`references`**
( `List[RefItem]`)
–


- **`self_ref`**
( `str`)
–



#### `` captions

```
captions: List[RefItem] = []

```

#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` data

```
data: TableData

```

#### `` footnotes

```
footnotes: List[RefItem] = []

```

#### `` image

```
image: Optional[ImageRef] = None

```

#### `` label

```
label: Literal[DOCUMENT_INDEX, TABLE] = TABLE

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` prov

```
prov: List[ProvenanceItem] = []

```

#### `` references

```
references: List[RefItem] = []

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` caption\_text

```
caption_text(doc: DoclingDocument) -> str

```

Computes the caption as a single text.

#### `` export\_to\_dataframe

```
export_to_dataframe() -> DataFrame

```

Export the table as a Pandas DataFrame.

#### `` export\_to\_doctags

```
export_to_doctags(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500, add_location: bool = True, add_cell_location: bool = True, add_cell_text: bool = True, add_caption: bool = True)

```

Export table to document tokens format.

Parameters:

- **`doc`**
( `DoclingDocument`)
–



"DoclingDocument":

- **`new_line`**
( `str`, default:
`''`
)
–



str (Default value = "") Deprecated

- **`xsize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`ysize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`add_location`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_cell_location`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_cell_text`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_caption`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)


#### `` export\_to\_document\_tokens

```
export_to_document_tokens(*args, **kwargs)

```

Export to DocTags format.

#### `` export\_to\_html

```
export_to_html(doc: Optional[DoclingDocument] = None, add_caption: bool = True) -> str

```

Export the table as html.

#### `` export\_to\_markdown

```
export_to_markdown(doc: Optional[DoclingDocument] = None) -> str

```

Export the table as markdown.

#### `` export\_to\_otsl

```
export_to_otsl(doc: DoclingDocument, add_cell_location: bool = True, add_cell_text: bool = True, xsize: int = 500, ysize: int = 500) -> str

```

Export the table as OTSL.

#### `` get\_image

```
get_image(doc: DoclingDocument, prov_index: int = 0) -> Optional[Image]

```

Returns the image corresponding to this FloatingItem.

This function returns the PIL image from self.image if one is available.
Otherwise, it uses DocItem.get\_image to get an image of this FloatingItem.

In particular, when self.image is None, the function returns None if this
FloatingItem has no valid provenance or the doc does not contain a valid image
for the required page.

#### `` get\_location\_tokens

```
get_location_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500) -> str

```

Get the location string for the BaseCell.

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` TableCell

Bases: `BaseModel`

TableCell.

Methods:

- **`from_dict_format`**
–



from\_dict\_format.


Attributes:

- **`bbox`**
( `Optional[BoundingBox]`)
–


- **`col_span`**
( `int`)
–


- **`column_header`**
( `bool`)
–


- **`end_col_offset_idx`**
( `int`)
–


- **`end_row_offset_idx`**
( `int`)
–


- **`row_header`**
( `bool`)
–


- **`row_section`**
( `bool`)
–


- **`row_span`**
( `int`)
–


- **`start_col_offset_idx`**
( `int`)
–


- **`start_row_offset_idx`**
( `int`)
–


- **`text`**
( `str`)
–



#### `` bbox

```
bbox: Optional[BoundingBox] = None

```

#### `` col\_span

```
col_span: int = 1

```

#### `` column\_header

```
column_header: bool = False

```

#### `` end\_col\_offset\_idx

```
end_col_offset_idx: int

```

#### `` end\_row\_offset\_idx

```
end_row_offset_idx: int

```

#### `` row\_header

```
row_header: bool = False

```

#### `` row\_section

```
row_section: bool = False

```

#### `` row\_span

```
row_span: int = 1

```

#### `` start\_col\_offset\_idx

```
start_col_offset_idx: int

```

#### `` start\_row\_offset\_idx

```
start_row_offset_idx: int

```

#### `` text

```
text: str

```

#### `` from\_dict\_format

```
from_dict_format(data: Any) -> Any

```

from\_dict\_format.

### `` TableData

Bases: `BaseModel`

BaseTableData.

Attributes:

- **`grid`**
( `List[List[TableCell]]`)
–



grid.

- **`num_cols`**
( `int`)
–


- **`num_rows`**
( `int`)
–


- **`table_cells`**
( `List[TableCell]`)
–



#### `` grid

```
grid: List[List[TableCell]]

```

grid.

#### `` num\_cols

```
num_cols: int = 0

```

#### `` num\_rows

```
num_rows: int = 0

```

#### `` table\_cells

```
table_cells: List[TableCell] = []

```

### `` TableCellLabel

Bases: `str`, `Enum`

TableCellLabel.

Methods:

- **`get_color`**
–



Return the RGB color associated with a given label.


Attributes:

- **`BODY`**
–


- **`COLUMN_HEADER`**
–


- **`ROW_HEADER`**
–


- **`ROW_SECTION`**
–



#### `` BODY

```
BODY = 'body'

```

#### `` COLUMN\_HEADER

```
COLUMN_HEADER = 'col_header'

```

#### `` ROW\_HEADER

```
ROW_HEADER = 'row_header'

```

#### `` ROW\_SECTION

```
ROW_SECTION = 'row_section'

```

#### `` get\_color

```
get_color(label: TableCellLabel) -> Tuple[int, int, int]

```

Return the RGB color associated with a given label.

### `` KeyValueItem

Bases: `FloatingItem`

KeyValueItem.

Methods:

- **`caption_text`**
–



Computes the caption as a single text.

- **`export_to_document_tokens`**
–



Export key value item to document tokens format.

- **`get_image`**
–



Returns the image corresponding to this FloatingItem.

- **`get_location_tokens`**
–



Get the location string for the BaseCell.

- **`get_ref`**
–



get\_ref.


Attributes:

- **`captions`**
( `List[RefItem]`)
–


- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`footnotes`**
( `List[RefItem]`)
–


- **`graph`**
( `GraphData`)
–


- **`image`**
( `Optional[ImageRef]`)
–


- **`label`**
( `Literal[KEY_VALUE_REGION]`)
–


- **`model_config`**
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`prov`**
( `List[ProvenanceItem]`)
–


- **`references`**
( `List[RefItem]`)
–


- **`self_ref`**
( `str`)
–



#### `` captions

```
captions: List[RefItem] = []

```

#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` footnotes

```
footnotes: List[RefItem] = []

```

#### `` graph

```
graph: GraphData

```

#### `` image

```
image: Optional[ImageRef] = None

```

#### `` label

```
label: Literal[KEY_VALUE_REGION] = KEY_VALUE_REGION

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` prov

```
prov: List[ProvenanceItem] = []

```

#### `` references

```
references: List[RefItem] = []

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` caption\_text

```
caption_text(doc: DoclingDocument) -> str

```

Computes the caption as a single text.

#### `` export\_to\_document\_tokens

```
export_to_document_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500, add_location: bool = True, add_content: bool = True)

```

Export key value item to document tokens format.

Parameters:

- **`doc`**
( `DoclingDocument`)
–



"DoclingDocument":

- **`new_line`**
( `str`, default:
`''`
)
–



str (Default value = "") Deprecated

- **`xsize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`ysize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`add_location`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_content`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)


#### `` get\_image

```
get_image(doc: DoclingDocument, prov_index: int = 0) -> Optional[Image]

```

Returns the image corresponding to this FloatingItem.

This function returns the PIL image from self.image if one is available.
Otherwise, it uses DocItem.get\_image to get an image of this FloatingItem.

In particular, when self.image is None, the function returns None if this
FloatingItem has no valid provenance or the doc does not contain a valid image
for the required page.

#### `` get\_location\_tokens

```
get_location_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500) -> str

```

Get the location string for the BaseCell.

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` SectionHeaderItem

Bases: `TextItem`

SectionItem.

Methods:

- **`export_to_doctags`**
–



Export text element to document tokens format.

- **`export_to_document_tokens`**
–



Export to DocTags format.

- **`get_image`**
–



Returns the image of this DocItem.

- **`get_location_tokens`**
–



Get the location string for the BaseCell.

- **`get_ref`**
–



get\_ref.


Attributes:

- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`formatting`**
( `Optional[Formatting]`)
–


- **`hyperlink`**
( `Optional[Union[AnyUrl, Path]]`)
–


- **`label`**
( `Literal[SECTION_HEADER]`)
–


- **`level`**
( `LevelNumber`)
–


- **`model_config`**
–


- **`orig`**
( `str`)
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`prov`**
( `List[ProvenanceItem]`)
–


- **`self_ref`**
( `str`)
–


- **`text`**
( `str`)
–



#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` formatting

```
formatting: Optional[Formatting] = None

```

#### `` hyperlink

```
hyperlink: Optional[Union[AnyUrl, Path]] = Field(union_mode='left_to_right', default=None)

```

#### `` label

```
label: Literal[SECTION_HEADER] = SECTION_HEADER

```

#### `` level

```
level: LevelNumber = 1

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` orig

```
orig: str

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` prov

```
prov: List[ProvenanceItem] = []

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` text

```
text: str

```

#### `` export\_to\_doctags

```
export_to_doctags(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500, add_location: bool = True, add_content: bool = True)

```

Export text element to document tokens format.

Parameters:

- **`doc`**
( `DoclingDocument`)
–



"DoclingDocument":

- **`new_line`**
( `str`, default:
`''`
)
–



str (Default value = "") Deprecated

- **`xsize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`ysize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`add_location`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_content`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)


#### `` export\_to\_document\_tokens

```
export_to_document_tokens(*args, **kwargs)

```

Export to DocTags format.

#### `` get\_image

```
get_image(doc: DoclingDocument, prov_index: int = 0) -> Optional[Image]

```

Returns the image of this DocItem.

The function returns None if this DocItem has no valid provenance or
if a valid image of the page containing this DocItem is not available
in doc.

#### `` get\_location\_tokens

```
get_location_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500) -> str

```

Get the location string for the BaseCell.

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` PictureItem

Bases: `FloatingItem`

PictureItem.

Methods:

- **`caption_text`**
–



Computes the caption as a single text.

- **`export_to_doctags`**
–



Export picture to document tokens format.

- **`export_to_document_tokens`**
–



Export to DocTags format.

- **`export_to_html`**
–



Export picture to HTML format.

- **`export_to_markdown`**
–



Export picture to Markdown format.

- **`get_image`**
–



Returns the image corresponding to this FloatingItem.

- **`get_location_tokens`**
–



Get the location string for the BaseCell.

- **`get_ref`**
–



get\_ref.


Attributes:

- **`annotations`**
( `List[PictureDataType]`)
–


- **`captions`**
( `List[RefItem]`)
–


- **`children`**
( `List[RefItem]`)
–


- **`content_layer`**
( `ContentLayer`)
–


- **`footnotes`**
( `List[RefItem]`)
–


- **`image`**
( `Optional[ImageRef]`)
–


- **`label`**
( `Literal[PICTURE, CHART]`)
–


- **`model_config`**
–


- **`parent`**
( `Optional[RefItem]`)
–


- **`prov`**
( `List[ProvenanceItem]`)
–


- **`references`**
( `List[RefItem]`)
–


- **`self_ref`**
( `str`)
–



#### `` annotations

```
annotations: List[PictureDataType] = []

```

#### `` captions

```
captions: List[RefItem] = []

```

#### `` children

```
children: List[RefItem] = []

```

#### `` content\_layer

```
content_layer: ContentLayer = BODY

```

#### `` footnotes

```
footnotes: List[RefItem] = []

```

#### `` image

```
image: Optional[ImageRef] = None

```

#### `` label

```
label: Literal[PICTURE, CHART] = PICTURE

```

#### `` model\_config

```
model_config = ConfigDict(extra='forbid')

```

#### `` parent

```
parent: Optional[RefItem] = None

```

#### `` prov

```
prov: List[ProvenanceItem] = []

```

#### `` references

```
references: List[RefItem] = []

```

#### `` self\_ref

```
self_ref: str = Field(pattern=_JSON_POINTER_REGEX)

```

#### `` caption\_text

```
caption_text(doc: DoclingDocument) -> str

```

Computes the caption as a single text.

#### `` export\_to\_doctags

```
export_to_doctags(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500, add_location: bool = True, add_caption: bool = True, add_content: bool = True)

```

Export picture to document tokens format.

Parameters:

- **`doc`**
( `DoclingDocument`)
–



"DoclingDocument":

- **`new_line`**
( `str`, default:
`''`
)
–



str (Default value = "") Deprecated

- **`xsize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`ysize`**
( `int`, default:
`500`
)
–



int: (Default value = 500)

- **`add_location`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_caption`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)

- **`add_content`**
( `bool`, default:
`True`
)
–



bool: (Default value = True)


#### `` export\_to\_document\_tokens

```
export_to_document_tokens(*args, **kwargs)

```

Export to DocTags format.

#### `` export\_to\_html

```
export_to_html(doc: DoclingDocument, add_caption: bool = True, image_mode: ImageRefMode = PLACEHOLDER) -> str

```

Export picture to HTML format.

#### `` export\_to\_markdown

```
export_to_markdown(doc: DoclingDocument, add_caption: bool = True, image_mode: ImageRefMode = EMBEDDED, image_placeholder: str = '<!-- image -->') -> str

```

Export picture to Markdown format.

#### `` get\_image

```
get_image(doc: DoclingDocument, prov_index: int = 0) -> Optional[Image]

```

Returns the image corresponding to this FloatingItem.

This function returns the PIL image from self.image if one is available.
Otherwise, it uses DocItem.get\_image to get an image of this FloatingItem.

In particular, when self.image is None, the function returns None if this
FloatingItem has no valid provenance or the doc does not contain a valid image
for the required page.

#### `` get\_location\_tokens

```
get_location_tokens(doc: DoclingDocument, new_line: str = '', xsize: int = 500, ysize: int = 500) -> str

```

Get the location string for the BaseCell.

#### `` get\_ref

```
get_ref() -> RefItem

```

get\_ref.

### `` ImageRef

Bases: `BaseModel`

ImageRef.

Methods:

- **`from_pil`**
–



Construct ImageRef from a PIL Image.

- **`validate_mimetype`**
–



validate\_mimetype.


Attributes:

- **`dpi`**
( `int`)
–


- **`mimetype`**
( `str`)
–


- **`pil_image`**
( `Optional[Image]`)
–



Return the PIL Image.

- **`size`**
( `Size`)
–


- **`uri`**
( `Union[AnyUrl, Path]`)
–



#### `` dpi

```
dpi: int

```

#### `` mimetype

```
mimetype: str

```

#### `` pil\_image

```
pil_image: Optional[Image]

```

Return the PIL Image.

#### `` size

```
size: Size

```

#### `` uri

```
uri: Union[AnyUrl, Path] = Field(union_mode='left_to_right')

```

#### `` from\_pil

```
from_pil(image: Image, dpi: int) -> Self

```

Construct ImageRef from a PIL Image.

#### `` validate\_mimetype

```
validate_mimetype(v)

```

validate\_mimetype.

### `` PictureClassificationClass

Bases: `BaseModel`

PictureClassificationData.

Attributes:

- **`class_name`**
( `str`)
–


- **`confidence`**
( `float`)
–



#### `` class\_name

```
class_name: str

```

#### `` confidence

```
confidence: float

```

### `` PictureClassificationData

Bases: `BasePictureData`

PictureClassificationData.

Attributes:

- **`kind`**
( `Literal['classification']`)
–


- **`predicted_classes`**
( `List[PictureClassificationClass]`)
–


- **`provenance`**
( `str`)
–



#### `` kind

```
kind: Literal['classification'] = 'classification'

```

#### `` predicted\_classes

```
predicted_classes: List[PictureClassificationClass]

```

#### `` provenance

```
provenance: str

```

### `` RefItem

Bases: `BaseModel`

RefItem.

Methods:

- **`get_ref`**
–



get\_ref.

- **`resolve`**
–



Resolve the path in the document.


Attributes:

- **`cref`**
( `str`)
–


- **`model_config`**
–



#### `` cref

```
cref: str = Field(alias='$ref', pattern=_JSON_POINTER_REGEX)

```

#### `` model\_config

```
model_config = ConfigDict(populate_by_name=True)

```

#### `` get\_ref

```
get_ref()

```

get\_ref.

#### `` resolve

```
resolve(doc: DoclingDocument)

```

Resolve the path in the document.

### `` BoundingBox

Bases: `BaseModel`

BoundingBox.

Methods:

- **`area`**
–



area.

- **`as_tuple`**
–



as\_tuple.

- **`enclosing_bbox`**
–



Create a bounding box that covers all of the given boxes.

- **`expand_by_scale`**
–



expand\_to\_size.

- **`from_tuple`**
–



from\_tuple.

- **`intersection_area_with`**
–



Calculate the intersection area with another bounding box.

- **`intersection_over_self`**
–



intersection\_over\_self.

- **`intersection_over_union`**
–



intersection\_over\_union.

- **`is_above`**
–



is\_above.

- **`is_horizontally_connected`**
–



is\_horizontally\_connected.

- **`is_left_of`**
–



is\_left\_of.

- **`is_strictly_above`**
–



is\_strictly\_above.

- **`is_strictly_left_of`**
–



is\_strictly\_left\_of.

- **`normalized`**
–



normalized.

- **`overlaps`**
–



overlaps.

- **`overlaps_horizontally`**
–



Check if two bounding boxes overlap horizontally.

- **`overlaps_vertically`**
–



Check if two bounding boxes overlap vertically.

- **`overlaps_vertically_with_iou`**
–



overlaps\_y\_with\_iou.

- **`resize_by_scale`**
–



resize\_by\_scale.

- **`scale_to_size`**
–



scale\_to\_size.

- **`scaled`**
–



scaled.

- **`to_bottom_left_origin`**
–



to\_bottom\_left\_origin.

- **`to_top_left_origin`**
–



to\_top\_left\_origin.

- **`union_area_with`**
–



Calculates the union area with another bounding box.

- **`x_overlap_with`**
–



Calculates the horizontal overlap with another bounding box.

- **`x_union_with`**
–



Calculates the horizontal union dimension with another bounding box.

- **`y_overlap_with`**
–



Calculates the vertical overlap with another bounding box, respecting coordinate origin.

- **`y_union_with`**
–



Calculates the vertical union dimension with another bounding box, respecting coordinate origin.


Attributes:

- **`b`**
( `float`)
–


- **`coord_origin`**
( `CoordOrigin`)
–


- **`height`**
–



height.

- **`l`**
( `float`)
–


- **`r`**
( `float`)
–


- **`t`**
( `float`)
–


- **`width`**
–



width.


#### `` b

```
b: float

```

#### `` coord\_origin

```
coord_origin: CoordOrigin = TOPLEFT

```

#### `` height

```
height

```

height.

#### `` l

```
l: float

```

#### `` r

```
r: float

```

#### `` t

```
t: float

```

#### `` width

```
width

```

width.

#### `` area

```
area() -> float

```

area.

#### `` as\_tuple

```
as_tuple() -> Tuple[float, float, float, float]

```

as\_tuple.

#### `` enclosing\_bbox

```
enclosing_bbox(boxes: List[BoundingBox]) -> BoundingBox

```

Create a bounding box that covers all of the given boxes.

#### `` expand\_by\_scale

```
expand_by_scale(x_scale: float, y_scale: float) -> BoundingBox

```

expand\_to\_size.

#### `` from\_tuple

```
from_tuple(coord: Tuple[float, ...], origin: CoordOrigin)

```

from\_tuple.

Parameters:

- **`coord`**
( `Tuple[float, ...]`)
–



Tuple\[float:\
\
- **`...]`**
–


- **`origin`**
( `CoordOrigin`)
–



CoordOrigin:


#### `` intersection\_area\_with

```
intersection_area_with(other: BoundingBox) -> float

```

Calculate the intersection area with another bounding box.

#### `` intersection\_over\_self

```
intersection_over_self(other: BoundingBox, eps: float = 1e-06) -> float

```

intersection\_over\_self.

#### `` intersection\_over\_union

```
intersection_over_union(other: BoundingBox, eps: float = 1e-06) -> float

```

intersection\_over\_union.

#### `` is\_above

```
is_above(other: BoundingBox) -> bool

```

is\_above.

#### `` is\_horizontally\_connected

```
is_horizontally_connected(elem_i: BoundingBox, elem_j: BoundingBox) -> bool

```

is\_horizontally\_connected.

#### `` is\_left\_of

```
is_left_of(other: BoundingBox) -> bool

```

is\_left\_of.

#### `` is\_strictly\_above

```
is_strictly_above(other: BoundingBox, eps: float = 0.001) -> bool

```

is\_strictly\_above.

#### `` is\_strictly\_left\_of

```
is_strictly_left_of(other: BoundingBox, eps: float = 0.001) -> bool

```

is\_strictly\_left\_of.

#### `` normalized

```
normalized(page_size: Size)

```

normalized.

#### `` overlaps

```
overlaps(other: BoundingBox) -> bool

```

overlaps.

#### `` overlaps\_horizontally

```
overlaps_horizontally(other: BoundingBox) -> bool

```

Check if two bounding boxes overlap horizontally.

#### `` overlaps\_vertically

```
overlaps_vertically(other: BoundingBox) -> bool

```

Check if two bounding boxes overlap vertically.

#### `` overlaps\_vertically\_with\_iou

```
overlaps_vertically_with_iou(other: BoundingBox, iou: float) -> bool

```

overlaps\_y\_with\_iou.

#### `` resize\_by\_scale

```
resize_by_scale(x_scale: float, y_scale: float)

```

resize\_by\_scale.

#### `` scale\_to\_size

```
scale_to_size(old_size: Size, new_size: Size)

```

scale\_to\_size.

#### `` scaled

```
scaled(scale: float)

```

scaled.

#### `` to\_bottom\_left\_origin

```
to_bottom_left_origin(page_height: float) -> BoundingBox

```

to\_bottom\_left\_origin.

Parameters:

- **`page_height`**
( `float`)
–



#### `` to\_top\_left\_origin

```
to_top_left_origin(page_height: float) -> BoundingBox

```

to\_top\_left\_origin.

Parameters:

- **`page_height`**
( `float`)
–



#### `` union\_area\_with

```
union_area_with(other: BoundingBox) -> float

```

Calculates the union area with another bounding box.

#### `` x\_overlap\_with

```
x_overlap_with(other: BoundingBox) -> float

```

Calculates the horizontal overlap with another bounding box.

#### `` x\_union\_with

```
x_union_with(other: BoundingBox) -> float

```

Calculates the horizontal union dimension with another bounding box.

#### `` y\_overlap\_with

```
y_overlap_with(other: BoundingBox) -> float

```

Calculates the vertical overlap with another bounding box, respecting coordinate origin.

#### `` y\_union\_with

```
y_union_with(other: BoundingBox) -> float

```

Calculates the vertical union dimension with another bounding box, respecting coordinate origin.

### `` CoordOrigin

Bases: `str`, `Enum`

CoordOrigin.

Attributes:

- **`BOTTOMLEFT`**
–


- **`TOPLEFT`**
–



#### `` BOTTOMLEFT

```
BOTTOMLEFT = 'BOTTOMLEFT'

```

#### `` TOPLEFT

```
TOPLEFT = 'TOPLEFT'

```

### `` ImageRefMode

Bases: `str`, `Enum`

ImageRefMode.

Attributes:

- **`EMBEDDED`**
–


- **`PLACEHOLDER`**
–


- **`REFERENCED`**
–



#### `` EMBEDDED

```
EMBEDDED = 'embedded'

```

#### `` PLACEHOLDER

```
PLACEHOLDER = 'placeholder'

```

#### `` REFERENCED

```
REFERENCED = 'referenced'

```

### `` Size

Bases: `BaseModel`

Size.

Methods:

- **`as_tuple`**
–



as\_tuple.


Attributes:

- **`height`**
( `float`)
–


- **`width`**
( `float`)
–



#### `` height

```
height: float = 0.0

```

#### `` width

```
width: float = 0.0

```

#### `` as\_tuple

```
as_tuple()

```

as\_tuple.

Back to top